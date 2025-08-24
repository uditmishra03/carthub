#!/bin/bash

# Deploy Shopping Cart Application to EKS
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

# Check if required parameters are provided
if [ $# -lt 4 ]; then
    echo "Usage: $0 <cluster-name> <aws-region> <frontend-ecr-uri> <backend-ecr-uri>"
    echo "Example: $0 shopping-cart-cluster us-east-1 123456789012.dkr.ecr.us-east-1.amazonaws.com/shopping-cart-frontend 123456789012.dkr.ecr.us-east-1.amazonaws.com/shopping-cart-backend"
    exit 1
fi

CLUSTER_NAME=$1
AWS_REGION=$2
FRONTEND_ECR_URI=$3
BACKEND_ECR_URI=$4

print_status "Starting Kubernetes deployment..."
print_status "Cluster: $CLUSTER_NAME"
print_status "Region: $AWS_REGION"
print_status "Frontend Image: $FRONTEND_ECR_URI:latest"
print_status "Backend Image: $BACKEND_ECR_URI:latest"

# Check prerequisites
print_status "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed"
    exit 1
fi

print_success "Prerequisites check passed"

# Update kubeconfig
print_status "Updating kubeconfig for EKS cluster..."
aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME

if [ $? -ne 0 ]; then
    print_error "Failed to update kubeconfig"
    exit 1
fi

print_success "Kubeconfig updated successfully"

# Verify cluster connection
print_status "Verifying cluster connection..."
kubectl cluster-info

if [ $? -ne 0 ]; then
    print_error "Failed to connect to cluster"
    exit 1
fi

print_success "Successfully connected to cluster"

# Create temporary directory for processed manifests
TEMP_DIR=$(mktemp -d)
print_status "Using temporary directory: $TEMP_DIR"

# Process and apply backend manifests
print_status "Processing backend manifests..."
cp ../k8s/backend/*.yaml $TEMP_DIR/

# Replace image URIs in backend manifests
sed -i "s|BACKEND_IMAGE_URI|$BACKEND_ECR_URI:latest|g" $TEMP_DIR/deployment.yaml

# Apply backend resources
print_status "Applying backend resources..."
kubectl apply -f $TEMP_DIR/deployment.yaml
kubectl apply -f $TEMP_DIR/hpa.yaml

if [ $? -ne 0 ]; then
    print_error "Failed to apply backend resources"
    exit 1
fi

print_success "Backend resources applied successfully"

# Process and apply frontend manifests
print_status "Processing frontend manifests..."
cp ../k8s/frontend/*.yaml $TEMP_DIR/

# Replace image URIs in frontend manifests
sed -i "s|FRONTEND_IMAGE_URI|$FRONTEND_ECR_URI:latest|g" $TEMP_DIR/deployment.yaml

# Apply frontend resources
print_status "Applying frontend resources..."
kubectl apply -f $TEMP_DIR/deployment.yaml
kubectl apply -f $TEMP_DIR/hpa.yaml

if [ $? -ne 0 ]; then
    print_error "Failed to apply frontend resources"
    exit 1
fi

print_success "Frontend resources applied successfully"

# Apply ingress (ALB)
print_status "Applying ingress resources..."
kubectl apply -f $TEMP_DIR/ingress.yaml

if [ $? -ne 0 ]; then
    print_error "Failed to apply ingress resources"
    exit 1
fi

print_success "Ingress resources applied successfully"

# Apply network policies
print_status "Applying network policies..."
kubectl apply -f ../k8s/database/network-policies.yaml

if [ $? -ne 0 ]; then
    print_warning "Failed to apply network policies (may not be supported)"
else
    print_success "Network policies applied successfully"
fi

# Apply monitoring resources
print_status "Applying monitoring resources..."
kubectl apply -f ../k8s/monitoring/service-monitor.yaml

if [ $? -ne 0 ]; then
    print_warning "Failed to apply monitoring resources (Prometheus may not be installed)"
else
    print_success "Monitoring resources applied successfully"
fi

# Wait for deployments to be ready
print_status "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/backend-deployment -n shopping-cart
kubectl wait --for=condition=available --timeout=300s deployment/frontend-deployment -n shopping-cart

if [ $? -ne 0 ]; then
    print_error "Deployments did not become ready within timeout"
    print_status "Checking pod status..."
    kubectl get pods -n shopping-cart
    exit 1
fi

print_success "All deployments are ready"

# Get ingress information
print_status "Getting ingress information..."
sleep 30  # Wait for ALB to be provisioned

INGRESS_HOST=$(kubectl get ingress shopping-cart-ingress -n shopping-cart -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)

if [ -n "$INGRESS_HOST" ]; then
    print_success "Application is accessible at: http://$INGRESS_HOST"
else
    print_warning "Ingress hostname not yet available. Check again in a few minutes:"
    echo "kubectl get ingress shopping-cart-ingress -n shopping-cart"
fi

# Show deployment status
print_status "Deployment Status:"
echo "===================="
kubectl get all -n shopping-cart

# Clean up temporary directory
rm -rf $TEMP_DIR

print_success "Kubernetes deployment completed successfully!"

echo ""
print_status "Useful commands:"
echo "- Check pods: kubectl get pods -n shopping-cart"
echo "- Check services: kubectl get svc -n shopping-cart"
echo "- Check ingress: kubectl get ingress -n shopping-cart"
echo "- View logs: kubectl logs -f deployment/backend-deployment -n shopping-cart"
echo "- Scale deployment: kubectl scale deployment backend-deployment --replicas=5 -n shopping-cart"
