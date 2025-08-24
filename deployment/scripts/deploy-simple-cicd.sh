#!/bin/bash

# Simplified Carthub Microservices CI/CD Deployment Script
# This script creates the basic infrastructure using AWS CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
REGION="us-west-2"
CLUSTER_NAME="carthub-cluster"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Starting simplified Carthub Microservices CI/CD deployment..."

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured or invalid."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_success "AWS credentials verified. Account ID: $ACCOUNT_ID"

# Create ECR repositories
print_status "Creating ECR repositories..."
for service in frontend backend database; do
    if aws ecr describe-repositories --repository-names carthub-$service --region $REGION &> /dev/null; then
        print_warning "ECR repository carthub-$service already exists"
    else
        aws ecr create-repository \
            --repository-name carthub-$service \
            --region $REGION \
            --image-scanning-configuration scanOnPush=true
        print_success "Created ECR repository: carthub-$service"
    fi
done

# Create CodeCommit repositories
print_status "Creating CodeCommit repositories..."
for service in frontend backend database; do
    if aws codecommit get-repository --repository-name carthub-$service --region $REGION &> /dev/null; then
        print_warning "CodeCommit repository carthub-$service already exists"
    else
        aws codecommit create-repository \
            --repository-name carthub-$service \
            --repository-description "Carthub $service microservice repository" \
            --region $REGION
        print_success "Created CodeCommit repository: carthub-$service"
    fi
done

# Create EKS cluster
print_status "Creating EKS cluster (this will take 15-20 minutes)..."
if aws eks describe-cluster --name $CLUSTER_NAME --region $REGION &> /dev/null; then
    print_warning "EKS cluster $CLUSTER_NAME already exists"
else
    # Create EKS service role
    if ! aws iam get-role --role-name EKSServiceRole &> /dev/null; then
        aws iam create-role \
            --role-name EKSServiceRole \
            --assume-role-policy-document '{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "eks.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }'
        
        aws iam attach-role-policy \
            --role-name EKSServiceRole \
            --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy
        
        print_success "Created EKS service role"
    fi
    
    # Get default VPC and subnets
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $REGION)
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text --region $REGION | tr '\t' ',')
    
    print_status "Using VPC: $VPC_ID"
    print_status "Using subnets: $SUBNET_IDS"
    
    # Create EKS cluster
    aws eks create-cluster \
        --name $CLUSTER_NAME \
        --version 1.28 \
        --role-arn arn:aws:iam::$ACCOUNT_ID:role/EKSServiceRole \
        --resources-vpc-config subnetIds=$SUBNET_IDS \
        --region $REGION
    
    print_status "EKS cluster creation initiated. Waiting for cluster to be active..."
    aws eks wait cluster-active --name $CLUSTER_NAME --region $REGION
    print_success "EKS cluster $CLUSTER_NAME is now active!"
fi

# Create node group
print_status "Creating EKS node group..."
if aws eks describe-nodegroup --cluster-name $CLUSTER_NAME --nodegroup-name carthub-nodes --region $REGION &> /dev/null; then
    print_warning "Node group carthub-nodes already exists"
else
    # Create node group role
    if ! aws iam get-role --role-name EKSNodeGroupRole &> /dev/null; then
        aws iam create-role \
            --role-name EKSNodeGroupRole \
            --assume-role-policy-document '{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }'
        
        aws iam attach-role-policy \
            --role-name EKSNodeGroupRole \
            --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy
        
        aws iam attach-role-policy \
            --role-name EKSNodeGroupRole \
            --policy-arn arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
        
        aws iam attach-role-policy \
            --role-name EKSNodeGroupRole \
            --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
        
        print_success "Created EKS node group role"
    fi
    
    # Get private subnets (or use all if no private subnets)
    PRIVATE_SUBNETS=$(aws ec2 describe-subnets \
        --filters "Name=vpc-id,Values=$VPC_ID" \
        --query 'Subnets[?MapPublicIpOnLaunch==`false`].SubnetId' \
        --output text --region $REGION | tr '\t' ',')
    
    if [ -z "$PRIVATE_SUBNETS" ]; then
        PRIVATE_SUBNETS=$SUBNET_IDS
        print_warning "No private subnets found, using all subnets"
    fi
    
    aws eks create-nodegroup \
        --cluster-name $CLUSTER_NAME \
        --nodegroup-name carthub-nodes \
        --node-role arn:aws:iam::$ACCOUNT_ID:role/EKSNodeGroupRole \
        --subnets $(echo $PRIVATE_SUBNETS | tr ',' ' ') \
        --instance-types t3.medium \
        --scaling-config minSize=2,maxSize=10,desiredSize=3 \
        --ami-type AL2_x86_64 \
        --region $REGION
    
    print_status "Node group creation initiated. Waiting for node group to be active..."
    aws eks wait nodegroup-active --cluster-name $CLUSTER_NAME --nodegroup-name carthub-nodes --region $REGION
    print_success "Node group carthub-nodes is now active!"
fi

# Configure kubectl
print_status "Configuring kubectl..."
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME
print_success "kubectl configured for cluster $CLUSTER_NAME"

# Test kubectl connection
print_status "Testing kubectl connection..."
kubectl get nodes
print_success "kubectl is working correctly!"

# Display results
print_success "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
echo ""
print_status "=== CREATED RESOURCES ==="
echo "EKS Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo ""

print_status "ECR Repositories:"
for service in frontend backend database; do
    REPO_URI=$(aws ecr describe-repositories --repository-names carthub-$service --region $REGION --query 'repositories[0].repositoryUri' --output text)
    echo "  carthub-$service: $REPO_URI"
done

echo ""
print_status "CodeCommit Repositories:"
for service in frontend backend database; do
    REPO_URL=$(aws codecommit get-repository --repository-name carthub-$service --region $REGION --query 'repositoryMetadata.cloneUrlHttp' --output text)
    echo "  carthub-$service: $REPO_URL"
done

echo ""
print_status "=== NEXT STEPS ==="
echo "1. Build and push Docker images to ECR repositories"
echo "2. Set up your microservice code in CodeCommit repositories"
echo "3. Deploy applications to EKS using kubectl"
echo ""

# Create a simple deployment script
cat > deploy-to-eks.sh << 'EOF'
#!/bin/bash

# Simple deployment script for EKS
REGION="us-west-2"
CLUSTER_NAME="carthub-cluster"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Deploying to EKS cluster: $CLUSTER_NAME"

# Create namespace
kubectl create namespace shopping-cart --dry-run=client -o yaml | kubectl apply -f -

# Example deployment for frontend
cat << YAML | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  namespace: shopping-cart
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: nginx:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: shopping-cart
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
YAML

echo "Deployment completed! Check status with:"
echo "kubectl get all -n shopping-cart"
EOF

chmod +x deploy-to-eks.sh
print_success "Created deploy-to-eks.sh script for easy deployment"

print_warning "Note: This is a simplified setup. For production, consider:"
echo "- Setting up proper VPC with private subnets"
echo "- Configuring CodePipeline for CI/CD"
echo "- Setting up proper security groups and IAM roles"
echo "- Adding monitoring and logging"
