#!/bin/bash

# Shopping Cart Microservices Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if architecture type is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [serverless|microservices]"
    echo "  serverless    - Deploy original serverless architecture"
    echo "  microservices - Deploy 3-tier microservices architecture"
    exit 1
fi

ARCHITECTURE=$1

# Validate architecture choice
if [ "$ARCHITECTURE" != "serverless" ] && [ "$ARCHITECTURE" != "microservices" ]; then
    print_error "Invalid architecture choice. Use 'serverless' or 'microservices'"
    exit 1
fi

print_status "Starting deployment of $ARCHITECTURE architecture..."

# Check prerequisites
print_status "Checking prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    print_error "AWS CDK is not installed. Please install it with: npm install -g aws-cdk"
    exit 1
fi

# Check if Docker is installed (for microservices)
if [ "$ARCHITECTURE" = "microservices" ]; then
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
fi

print_success "Prerequisites check passed"

# Navigate to CDK directory
cd infrastructure_cdk

# Install Python dependencies
print_status "Installing CDK dependencies..."
pip install -r requirements.txt
print_success "CDK dependencies installed"

# Bootstrap CDK if needed
print_status "Checking CDK bootstrap status..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit &> /dev/null; then
    print_warning "CDK not bootstrapped. Bootstrapping now..."
    cdk bootstrap
    print_success "CDK bootstrap completed"
else
    print_success "CDK already bootstrapped"
fi

# Deploy based on architecture choice
if [ "$ARCHITECTURE" = "serverless" ]; then
    print_status "Deploying serverless architecture..."
    STACK_NAME="ShoppingCartServerlessStack"
    
    # Deploy the stack
    cdk deploy $STACK_NAME --require-approval never
    
    print_success "Serverless deployment completed!"
    print_status "Getting API Gateway URL..."
    
    # Get the API Gateway URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text 2>/dev/null || echo "Not found")
    
    if [ "$API_URL" != "Not found" ]; then
        print_success "API Gateway URL: $API_URL"
        echo ""
        echo "Test your API with:"
        echo "curl -X POST $API_URL/cart/items \\"
        echo "  -H 'Content-Type: application/json' \\"
        echo "  -d '{\"customer_id\":\"test-123\",\"product_id\":\"prod-456\",\"product_name\":\"Test Product\",\"price\":\"10.99\",\"quantity\":1}'"
    fi

elif [ "$ARCHITECTURE" = "microservices" ]; then
    print_status "Deploying microservices architecture..."
    STACK_NAME="ShoppingCartMicroservicesStack"
    
    # Check if Node.js is available for frontend build
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found. Frontend container will build Node.js during deployment."
    fi
    
    # Deploy the stack
    print_status "This may take 15-20 minutes for the first deployment..."
    cdk deploy $STACK_NAME --require-approval never
    
    print_success "Microservices deployment completed!"
    print_status "Getting service URLs..."
    
    # Get the frontend URL
    FRONTEND_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`FrontendURL`].OutputValue' \
        --output text 2>/dev/null || echo "Not found")
    
    # Get the backend URL (internal)
    BACKEND_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' \
        --output text 2>/dev/null || echo "Not found")
    
    if [ "$FRONTEND_URL" != "Not found" ]; then
        print_success "Frontend URL: $FRONTEND_URL"
        print_success "Backend URL (internal): $BACKEND_URL"
        echo ""
        print_status "Waiting for services to be ready (this may take a few minutes)..."
        sleep 30
        
        echo "Test your application:"
        echo "1. Open your browser to: $FRONTEND_URL"
        echo "2. Or run verification script: python ../verify_deployment.py $FRONTEND_URL $BACKEND_URL"
    fi
fi

print_success "Deployment completed successfully!"

# Show cleanup instructions
echo ""
print_warning "To avoid ongoing charges, remember to clean up resources when done:"
echo "cd infrastructure_cdk && cdk destroy $STACK_NAME"
