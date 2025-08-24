#!/bin/bash

# Build and Push Docker Images to ECR
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required parameters are provided
if [ $# -lt 3 ]; then
    echo "Usage: $0 <aws-region> <frontend-ecr-uri> <backend-ecr-uri>"
    echo "Example: $0 us-east-1 123456789012.dkr.ecr.us-east-1.amazonaws.com/shopping-cart-frontend 123456789012.dkr.ecr.us-east-1.amazonaws.com/shopping-cart-backend"
    exit 1
fi

AWS_REGION=$1
FRONTEND_ECR_URI=$2
BACKEND_ECR_URI=$3

print_status "Starting Docker image build and push process..."
print_status "AWS Region: $AWS_REGION"
print_status "Frontend ECR: $FRONTEND_ECR_URI"
print_status "Backend ECR: $BACKEND_ECR_URI"

# Check prerequisites
print_status "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    exit 1
fi

print_success "Prerequisites check passed"

# Login to ECR
print_status "Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${FRONTEND_ECR_URI%/*}

if [ $? -ne 0 ]; then
    print_error "Failed to login to ECR"
    exit 1
fi

print_success "Successfully logged in to ECR"

# Build and push backend image
print_status "Building backend Docker image..."
cd ../backend

docker build -t shopping-cart-backend:latest .

if [ $? -ne 0 ]; then
    print_error "Failed to build backend image"
    exit 1
fi

print_success "Backend image built successfully"

print_status "Tagging and pushing backend image to ECR..."
docker tag shopping-cart-backend:latest $BACKEND_ECR_URI:latest
docker tag shopping-cart-backend:latest $BACKEND_ECR_URI:$(date +%Y%m%d-%H%M%S)

docker push $BACKEND_ECR_URI:latest
docker push $BACKEND_ECR_URI:$(date +%Y%m%d-%H%M%S)

if [ $? -ne 0 ]; then
    print_error "Failed to push backend image"
    exit 1
fi

print_success "Backend image pushed successfully"

# Build and push frontend image
print_status "Building frontend Docker image..."
cd ../frontend

docker build -t shopping-cart-frontend:latest .

if [ $? -ne 0 ]; then
    print_error "Failed to build frontend image"
    exit 1
fi

print_success "Frontend image built successfully"

print_status "Tagging and pushing frontend image to ECR..."
docker tag shopping-cart-frontend:latest $FRONTEND_ECR_URI:latest
docker tag shopping-cart-frontend:latest $FRONTEND_ECR_URI:$(date +%Y%m%d-%H%M%S)

docker push $FRONTEND_ECR_URI:latest
docker push $FRONTEND_ECR_URI:$(date +%Y%m%d-%H%M%S)

if [ $? -ne 0 ]; then
    print_error "Failed to push frontend image"
    exit 1
fi

print_success "Frontend image pushed successfully"

# Clean up local images to save space
print_status "Cleaning up local images..."
docker rmi shopping-cart-backend:latest $BACKEND_ECR_URI:latest 2>/dev/null || true
docker rmi shopping-cart-frontend:latest $FRONTEND_ECR_URI:latest 2>/dev/null || true

print_success "Build and push process completed successfully!"
print_status "Images are now available in ECR and ready for Kubernetes deployment"

cd ../scripts
