#!/bin/bash

# Carthub Microservices CI/CD Deployment Script
# This script deploys the complete microservices architecture with CodeCommit, CodePipeline, ECR, and EKS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
REGION="us-west-2"
STACK_NAME="CarthubMicroservicesCicd"
PROFILE=""

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

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -r, --region REGION     AWS region (default: us-west-2)"
    echo "  -s, --stack-name NAME   CloudFormation stack name (default: CarthubMicroservicesCicd)"
    echo "  -p, --profile PROFILE   AWS profile to use"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy with defaults"
    echo "  $0 --region us-east-1                # Deploy to us-east-1"
    echo "  $0 --profile my-profile              # Use specific AWS profile"
    echo "  $0 --stack-name MyStack --region us-east-1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -s|--stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        -p|--profile)
            PROFILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Set AWS CLI profile if provided
if [[ -n "$PROFILE" ]]; then
    export AWS_PROFILE="$PROFILE"
    print_status "Using AWS profile: $PROFILE"
fi

print_status "Starting Carthub Microservices CI/CD deployment..."
print_status "Region: $REGION"
print_status "Stack Name: $STACK_NAME"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    print_error "AWS CDK is not installed. Please install it first."
    print_status "Run: npm install -g aws-cdk"
    exit 1
fi

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured or invalid."
    print_status "Please run 'aws configure' or set up your credentials."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_success "AWS credentials verified. Account ID: $ACCOUNT_ID"

# Navigate to CDK directory
cd infrastructure_cdk

# Install CDK dependencies
print_status "Installing CDK dependencies..."
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found. Installing basic CDK dependencies..."
    pip install aws-cdk-lib constructs
fi

# Update CDK app.py to include the new stack
print_status "Updating CDK app configuration..."
cat > app.py << 'EOF'
#!/usr/bin/env python3
"""
AWS CDK App for Carthub Shopping Cart
Supports multiple deployment architectures
"""

import os
from aws_cdk import App, Environment

from shopping_cart_stack import ShoppingCartStack
from microservices_stack import MicroservicesStack
from eks_stack import EKSStack
from microservices_cicd_stack import MicroservicesCicdStack

app = App()

# Get environment
env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'us-west-2')
)

# Serverless stack (original)
serverless_stack = ShoppingCartStack(
    app, "ShoppingCartServerlessStack",
    env=env,
    description="Serverless shopping cart with Lambda and DynamoDB"
)

# ECS Microservices stack
microservices_stack = MicroservicesStack(
    app, "ShoppingCartMicroservicesStack", 
    env=env,
    description="3-tier microservices architecture with ECS, RDS, and VPC"
)

# EKS stack
eks_stack = EKSStack(
    app, "ShoppingCartEKSStack",
    env=env,
    description="Kubernetes-native microservices with EKS, ECR, and advanced scaling"
)

# Microservices CI/CD stack
cicd_stack = MicroservicesCicdStack(
    app, "CarthubMicroservicesCicd",
    env=env,
    description="Complete CI/CD pipeline with CodeCommit, CodePipeline, ECR, and EKS"
)

app.synth()
EOF

# Bootstrap CDK if needed
print_status "Checking CDK bootstrap status..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit --region $REGION &> /dev/null; then
    print_status "Bootstrapping CDK..."
    cdk bootstrap aws://$ACCOUNT_ID/$REGION
    print_success "CDK bootstrap completed"
else
    print_success "CDK already bootstrapped"
fi

# Deploy the stack
print_status "Deploying microservices CI/CD infrastructure..."
print_status "This may take 20-30 minutes..."

if cdk deploy $STACK_NAME --region $REGION --require-approval never; then
    print_success "Infrastructure deployment completed successfully!"
else
    print_error "Infrastructure deployment failed!"
    exit 1
fi

# Get stack outputs
print_status "Retrieving stack outputs..."
OUTPUTS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs' --output json)

# Parse important outputs
EKS_CLUSTER_NAME=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="EKSClusterName") | .OutputValue')
FRONTEND_REPO_URL=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="CodeCommitFrontendRepoUrl") | .OutputValue')
BACKEND_REPO_URL=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="CodeCommitBackendRepoUrl") | .OutputValue')
DATABASE_REPO_URL=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="CodeCommitDatabaseRepoUrl") | .OutputValue')

print_success "Deployment completed successfully!"
echo ""
print_status "=== DEPLOYMENT SUMMARY ==="
echo "EKS Cluster Name: $EKS_CLUSTER_NAME"
echo "Frontend Repository: $FRONTEND_REPO_URL"
echo "Backend Repository: $BACKEND_REPO_URL"
echo "Database Repository: $DATABASE_REPO_URL"
echo ""

# Configure kubectl
print_status "Configuring kubectl for EKS cluster..."
aws eks update-kubeconfig --region $REGION --name $EKS_CLUSTER_NAME
print_success "kubectl configured successfully"

# Create repository setup script
print_status "Creating repository setup script..."
cat > ../setup-repositories.sh << EOF
#!/bin/bash

# Repository Setup Script
# This script helps you set up the CodeCommit repositories with your microservices code

set -e

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m \$1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m \$1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m \$1"
}

# Repository URLs
FRONTEND_REPO="$FRONTEND_REPO_URL"
BACKEND_REPO="$BACKEND_REPO_URL"
DATABASE_REPO="$DATABASE_REPO_URL"

print_status "Setting up CodeCommit repositories..."

# Function to setup a repository
setup_repo() {
    local repo_name=\$1
    local repo_url=\$2
    local source_dir=\$3
    
    print_status "Setting up \$repo_name repository..."
    
    # Create temporary directory
    temp_dir=\$(mktemp -d)
    cd \$temp_dir
    
    # Clone the empty repository
    git clone \$repo_url \$repo_name
    cd \$repo_name
    
    # Copy source files
    cp -r \$source_dir/* .
    
    # Add all files
    git add .
    git commit -m "Initial commit: \$repo_name microservice"
    
    # Push to main branch
    git push origin main
    
    print_success "\$repo_name repository setup completed"
    
    # Cleanup
    cd /
    rm -rf \$temp_dir
}

# Setup each repository
setup_repo "frontend" "\$FRONTEND_REPO" "microservices/frontend"
setup_repo "backend" "\$BACKEND_REPO" "microservices/backend"  
setup_repo "database" "\$DATABASE_REPO" "microservices/database"

print_success "All repositories have been set up successfully!"
print_status "The CI/CD pipelines will automatically trigger when you push code to the repositories."

EOF

chmod +x ../setup-repositories.sh

print_success "Repository setup script created: setup-repositories.sh"

# Create monitoring script
print_status "Creating monitoring script..."
cat > ../monitor-deployments.sh << EOF
#!/bin/bash

# Deployment Monitoring Script
# This script helps you monitor the CI/CD pipelines and EKS deployments

set -e

REGION="$REGION"
EKS_CLUSTER_NAME="$EKS_CLUSTER_NAME"

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m \$1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m \$1"
}

# Function to check pipeline status
check_pipelines() {
    print_status "Checking CodePipeline status..."
    
    pipelines=("carthub-frontend-pipeline" "carthub-backend-pipeline" "carthub-database-pipeline")
    
    for pipeline in "\${pipelines[@]}"; do
        status=\$(aws codepipeline get-pipeline-state --name \$pipeline --region \$REGION --query 'stageStates[0].latestExecution.status' --output text 2>/dev/null || echo "NOT_FOUND")
        echo "  \$pipeline: \$status"
    done
}

# Function to check EKS deployments
check_eks_deployments() {
    print_status "Checking EKS deployments..."
    
    # Update kubeconfig
    aws eks update-kubeconfig --region \$REGION --name \$EKS_CLUSTER_NAME
    
    echo "Namespace status:"
    kubectl get namespaces | grep shopping-cart || echo "  shopping-cart namespace not found"
    
    echo ""
    echo "Deployment status:"
    kubectl get deployments -n shopping-cart 2>/dev/null || echo "  No deployments found"
    
    echo ""
    echo "Service status:"
    kubectl get services -n shopping-cart 2>/dev/null || echo "  No services found"
    
    echo ""
    echo "Pod status:"
    kubectl get pods -n shopping-cart 2>/dev/null || echo "  No pods found"
    
    echo ""
    echo "Ingress status:"
    kubectl get ingress -n shopping-cart 2>/dev/null || echo "  No ingress found"
}

# Function to get application URL
get_app_url() {
    print_status "Getting application URL..."
    
    # Get ALB hostname from ingress
    alb_hostname=\$(kubectl get ingress frontend-ingress -n shopping-cart -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    
    if [[ -n "\$alb_hostname" ]]; then
        print_success "Application URL: http://\$alb_hostname"
    else
        print_status "Application URL not yet available. Ingress may still be provisioning."
    fi
}

# Main monitoring function
main() {
    echo "=== CARTHUB MICROSERVICES MONITORING ==="
    echo ""
    
    check_pipelines
    echo ""
    
    check_eks_deployments
    echo ""
    
    get_app_url
    echo ""
    
    print_status "Monitoring completed. Run this script again to check for updates."
}

# Run monitoring
main

EOF

chmod +x ../monitor-deployments.sh

print_success "Monitoring script created: monitor-deployments.sh"

# Go back to original directory
cd ..

print_success "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
echo ""
print_status "Next Steps:"
echo "1. Run './setup-repositories.sh' to populate the CodeCommit repositories"
echo "2. The CI/CD pipelines will automatically build and deploy your microservices"
echo "3. Use './monitor-deployments.sh' to check deployment status"
echo "4. Access your application once the ALB is provisioned"
echo ""
print_status "Architecture Overview:"
echo "• 3 CodeCommit repositories (frontend, backend, database)"
echo "• 3 CodePipeline pipelines with automated CI/CD"
echo "• 3 ECR repositories for container images"
echo "• EKS cluster with auto-scaling and load balancing"
echo "• RDS PostgreSQL database with automated backups"
echo "• Network policies for security"
echo "• Horizontal Pod Autoscaler for dynamic scaling"
echo ""
print_warning "Note: The complete deployment may take additional time for EKS nodes and ALB provisioning."
print_status "Monitor the deployment using the provided monitoring script."
