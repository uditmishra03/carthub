#!/bin/bash

# Complete EKS Deployment Script for Shopping Cart Microservices
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Default values
AWS_REGION="us-east-1"
CLUSTER_NAME="shopping-cart-cluster"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            AWS_REGION="$2"
            shift 2
            ;;
        --cluster-name)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --region REGION        AWS region (default: us-east-1)"
            echo "  --cluster-name NAME    EKS cluster name (default: shopping-cart-cluster)"
            echo "  --help                 Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_status "🚀 Starting EKS deployment for Shopping Cart Microservices"
print_status "AWS Region: $AWS_REGION"
print_status "Cluster Name: $CLUSTER_NAME"
echo "============================================================"

# Check prerequisites
print_status "🔍 Checking prerequisites..."

MISSING_TOOLS=()

if ! command -v aws &> /dev/null; then
    MISSING_TOOLS+=("aws-cli")
fi

if ! command -v cdk &> /dev/null; then
    MISSING_TOOLS+=("aws-cdk")
fi

if ! command -v kubectl &> /dev/null; then
    MISSING_TOOLS+=("kubectl")
fi

if ! command -v docker &> /dev/null; then
    MISSING_TOOLS+=("docker")
fi

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    print_error "Missing required tools: ${MISSING_TOOLS[*]}"
    echo ""
    echo "Installation instructions:"
    echo "- AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    echo "- AWS CDK: npm install -g aws-cdk"
    echo "- kubectl: https://kubernetes.io/docs/tasks/tools/"
    echo "- Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker daemon
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure'"
    exit 1
fi

print_success "✅ Prerequisites check passed"

# Step 1: Deploy EKS infrastructure
print_status "🏗️  Step 1: Deploying EKS infrastructure..."
cd infrastructure_cdk

# Install CDK dependencies
print_status "Installing CDK dependencies..."
pip install -r requirements.txt

# Bootstrap CDK if needed
print_status "Checking CDK bootstrap status..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit --region $AWS_REGION &> /dev/null; then
    print_warning "CDK not bootstrapped. Bootstrapping now..."
    cdk bootstrap --region $AWS_REGION
    print_success "CDK bootstrap completed"
else
    print_success "CDK already bootstrapped"
fi

# Deploy EKS stack
print_status "Deploying EKS stack (this may take 15-20 minutes)..."
cdk deploy ShoppingCartEKSStack --region $AWS_REGION --require-approval never

if [ $? -ne 0 ]; then
    print_error "Failed to deploy EKS stack"
    exit 1
fi

print_success "✅ EKS infrastructure deployed successfully"

# Get stack outputs
print_status "Getting stack outputs..."
FRONTEND_ECR_URI=$(aws cloudformation describe-stacks \
    --stack-name ShoppingCartEKSStack \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendECRRepository`].OutputValue' \
    --output text)

BACKEND_ECR_URI=$(aws cloudformation describe-stacks \
    --stack-name ShoppingCartEKSStack \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`BackendECRRepository`].OutputValue' \
    --output text)

ACTUAL_CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --stack-name ShoppingCartEKSStack \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`EKSClusterName`].OutputValue' \
    --output text)

if [ -z "$FRONTEND_ECR_URI" ] || [ -z "$BACKEND_ECR_URI" ] || [ -z "$ACTUAL_CLUSTER_NAME" ]; then
    print_error "Failed to get stack outputs"
    exit 1
fi

print_success "Stack outputs retrieved:"
print_status "Frontend ECR: $FRONTEND_ECR_URI"
print_status "Backend ECR: $BACKEND_ECR_URI"
print_status "Cluster Name: $ACTUAL_CLUSTER_NAME"

cd ..

# Step 2: Build and push Docker images
print_status "🐳 Step 2: Building and pushing Docker images..."
./scripts/build-and-push.sh $AWS_REGION $FRONTEND_ECR_URI $BACKEND_ECR_URI

if [ $? -ne 0 ]; then
    print_error "Failed to build and push Docker images"
    exit 1
fi

print_success "✅ Docker images built and pushed successfully"

# Step 3: Deploy to Kubernetes
print_status "☸️  Step 3: Deploying to Kubernetes..."
./scripts/deploy-k8s.sh $ACTUAL_CLUSTER_NAME $AWS_REGION $FRONTEND_ECR_URI $BACKEND_ECR_URI

if [ $? -ne 0 ]; then
    print_error "Failed to deploy to Kubernetes"
    exit 1
fi

print_success "✅ Kubernetes deployment completed successfully"

# Step 4: Wait for and get application URL
print_status "🌐 Step 4: Getting application URL..."
print_status "Waiting for Load Balancer to be ready (this may take a few minutes)..."

# Update kubeconfig
aws eks update-kubeconfig --region $AWS_REGION --name $ACTUAL_CLUSTER_NAME

# Wait for ingress to get an address
for i in {1..20}; do
    INGRESS_HOST=$(kubectl get ingress shopping-cart-ingress -n shopping-cart -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
    if [ -n "$INGRESS_HOST" ]; then
        break
    fi
    print_status "Waiting for Load Balancer... (attempt $i/20)"
    sleep 30
done

if [ -n "$INGRESS_HOST" ]; then
    print_success "🎉 Application deployed successfully!"
    echo ""
    echo "============================================================"
    echo "🌟 DEPLOYMENT COMPLETE"
    echo "============================================================"
    echo "Application URL: http://$INGRESS_HOST"
    echo "Cluster Name: $ACTUAL_CLUSTER_NAME"
    echo "Region: $AWS_REGION"
    echo ""
    echo "📊 Monitoring Commands:"
    echo "kubectl get pods -n shopping-cart"
    echo "kubectl get svc -n shopping-cart"
    echo "kubectl get ingress -n shopping-cart"
    echo "kubectl logs -f deployment/backend-deployment -n shopping-cart"
    echo ""
    echo "🔧 Scaling Commands:"
    echo "kubectl scale deployment backend-deployment --replicas=5 -n shopping-cart"
    echo "kubectl scale deployment frontend-deployment --replicas=5 -n shopping-cart"
    echo ""
    echo "🧹 Cleanup Command:"
    echo "cd infrastructure_cdk && cdk destroy ShoppingCartEKSStack --region $AWS_REGION"
    echo "============================================================"
    
    # Test the application
    print_status "🧪 Testing application health..."
    sleep 60  # Wait for application to be fully ready
    
    if curl -f -s "http://$INGRESS_HOST/health" > /dev/null; then
        print_success "✅ Application health check passed"
    else
        print_warning "⚠️  Application health check failed (may still be starting up)"
    fi
    
else
    print_warning "⚠️  Load Balancer hostname not yet available"
    echo "Check the ingress status with:"
    echo "kubectl get ingress shopping-cart-ingress -n shopping-cart"
fi

# Show final status
print_status "📋 Final Status:"
kubectl get all -n shopping-cart

print_success "🎉 EKS deployment process completed!"
