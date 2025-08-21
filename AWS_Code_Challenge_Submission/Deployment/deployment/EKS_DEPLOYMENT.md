# EKS Microservices Deployment Guide

This guide covers deploying the Shopping Cart application using Amazon EKS (Elastic Kubernetes Service) for maximum scalability and Kubernetes features.

## 🏗️ EKS Architecture Overview

The application is deployed on a fully managed Kubernetes cluster with:

### **Infrastructure Components**
- **EKS Cluster**: Managed Kubernetes control plane
- **Managed Node Groups**: Auto-scaling worker nodes (t3.medium/large)
- **VPC**: 3-tier architecture across 3 AZs
- **ECR**: Container image repositories
- **RDS PostgreSQL**: Managed database
- **ALB**: Application Load Balancer via AWS Load Balancer Controller

### **Kubernetes Components**
- **Deployments**: Frontend (React/nginx) and Backend (FastAPI)
- **Services**: ClusterIP services for internal communication
- **Ingress**: ALB ingress for external access
- **HPA**: Horizontal Pod Autoscaler for automatic scaling
- **Network Policies**: Security isolation between tiers
- **Service Accounts**: IRSA for AWS service access

### **Scalability Features**
- **Cluster Autoscaler**: Automatic node scaling
- **Horizontal Pod Autoscaler**: Pod-level scaling based on CPU/memory
- **Vertical Pod Autoscaler**: Resource optimization (optional)
- **Load Balancing**: Multi-AZ traffic distribution

## 🚀 Quick Deployment

### One-Command Deployment
```bash
./deploy-eks.sh
```

### Custom Deployment
```bash
./deploy-eks.sh --region us-west-2 --cluster-name my-shopping-cart
```

## 📋 Prerequisites

### Required Tools
1. **AWS CLI** (v2.x recommended)
   ```bash
   # Install AWS CLI
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **AWS CDK**
   ```bash
   npm install -g aws-cdk
   ```

3. **kubectl**
   ```bash
   # Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
   ```

4. **Docker**
   ```bash
   # Install Docker Engine
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

### AWS Configuration
```bash
# Configure AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

### Required Permissions
Your AWS user/role needs permissions for:
- EKS cluster management
- EC2 instances and networking
- ECR repositories
- RDS databases
- IAM roles and policies
- CloudFormation stacks

## 🔧 Manual Deployment Steps

If you prefer to deploy step by step:

### Step 1: Deploy Infrastructure
```bash
cd infrastructure_cdk
pip install -r requirements.txt
cdk bootstrap
cdk deploy ShoppingCartEKSStack
```

### Step 2: Build and Push Images
```bash
# Get ECR URIs from stack outputs
FRONTEND_ECR=$(aws cloudformation describe-stacks --stack-name ShoppingCartEKSStack --query 'Stacks[0].Outputs[?OutputKey==`FrontendECRRepository`].OutputValue' --output text)
BACKEND_ECR=$(aws cloudformation describe-stacks --stack-name ShoppingCartEKSStack --query 'Stacks[0].Outputs[?OutputKey==`BackendECRRepository`].OutputValue' --output text)

# Build and push
./scripts/build-and-push.sh us-east-1 $FRONTEND_ECR $BACKEND_ECR
```

### Step 3: Deploy to Kubernetes
```bash
# Get cluster name
CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name ShoppingCartEKSStack --query 'Stacks[0].Outputs[?OutputKey==`EKSClusterName`].OutputValue' --output text)

# Deploy
./scripts/deploy-k8s.sh $CLUSTER_NAME us-east-1 $FRONTEND_ECR $BACKEND_ECR
```

## ☸️ Kubernetes Resources

### Deployments
- **Frontend**: 3 replicas, nginx + React SPA
- **Backend**: 3 replicas, FastAPI + PostgreSQL

### Auto Scaling
- **HPA**: CPU (70%) and Memory (80%) based scaling
- **Cluster Autoscaler**: Node-level scaling
- **Min/Max Replicas**: Frontend (3-15), Backend (3-20)

### Security
- **Network Policies**: Restrict inter-pod communication
- **Security Contexts**: Non-root containers, read-only filesystems
- **RBAC**: Service accounts with minimal permissions
- **Pod Disruption Budgets**: Ensure availability during updates

### Monitoring
- **Health Checks**: Liveness and readiness probes
- **Metrics**: Prometheus-compatible endpoints
- **Logging**: CloudWatch container insights

## 📊 Scaling Configuration

### Horizontal Pod Autoscaler (HPA)
```yaml
# Backend HPA
minReplicas: 3
maxReplicas: 20
targetCPUUtilization: 70%
targetMemoryUtilization: 80%

# Frontend HPA  
minReplicas: 3
maxReplicas: 15
targetCPUUtilization: 70%
targetMemoryUtilization: 80%
```

### Cluster Autoscaler
```yaml
# Node scaling
minSize: 2
maxSize: 10
desiredSize: 3
instanceTypes: [t3.medium, t3.large]
```

### Manual Scaling
```bash
# Scale pods
kubectl scale deployment backend-deployment --replicas=10 -n shopping-cart
kubectl scale deployment frontend-deployment --replicas=8 -n shopping-cart

# Scale nodes (via node group)
aws eks update-nodegroup-config --cluster-name shopping-cart-cluster --nodegroup-name DefaultNodeGroup --scaling-config minSize=5,maxSize=15,desiredSize=8
```

## 🔍 Monitoring and Troubleshooting

### Useful Commands
```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes

# Check application status
kubectl get all -n shopping-cart
kubectl get pods -n shopping-cart -o wide

# Check HPA status
kubectl get hpa -n shopping-cart
kubectl describe hpa backend-hpa -n shopping-cart

# Check ingress
kubectl get ingress -n shopping-cart
kubectl describe ingress shopping-cart-ingress -n shopping-cart

# View logs
kubectl logs -f deployment/backend-deployment -n shopping-cart
kubectl logs -f deployment/frontend-deployment -n shopping-cart

# Check events
kubectl get events -n shopping-cart --sort-by='.lastTimestamp'
```

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n shopping-cart
   kubectl logs <pod-name> -n shopping-cart
   ```

2. **Load Balancer not accessible**
   ```bash
   # Check ALB controller
   kubectl logs -n kube-system deployment/aws-load-balancer-controller
   
   # Check security groups
   aws ec2 describe-security-groups --filters "Name=tag:elbv2.k8s.aws/cluster,Values=shopping-cart-cluster"
   ```

3. **Database connection issues**
   ```bash
   # Check database security group
   kubectl exec -it deployment/backend-deployment -n shopping-cart -- env | grep DATABASE
   ```

4. **Scaling issues**
   ```bash
   # Check metrics server
   kubectl top nodes
   kubectl top pods -n shopping-cart
   
   # Check cluster autoscaler
   kubectl logs -n kube-system deployment/cluster-autoscaler
   ```

## 🔒 Security Best Practices

### Network Security
- **VPC**: Private subnets for worker nodes
- **Security Groups**: Least privilege access
- **Network Policies**: Pod-to-pod communication control
- **ALB**: Internet-facing load balancer in public subnets

### Container Security
- **Non-root containers**: All containers run as non-root
- **Read-only filesystems**: Immutable container filesystems
- **Security contexts**: Drop all capabilities
- **Image scanning**: ECR vulnerability scanning enabled

### Access Control
- **RBAC**: Role-based access control
- **IRSA**: IAM roles for service accounts
- **Secrets**: Kubernetes secrets for sensitive data
- **Service accounts**: Dedicated accounts per service

## 💰 Cost Optimization

### Development Environment
- **Node Types**: t3.medium instances
- **Min Nodes**: 2 nodes
- **Spot Instances**: Can be enabled for cost savings

### Production Environment
- **Node Types**: Mix of instance types
- **Reserved Instances**: For predictable workloads
- **Cluster Autoscaler**: Scale down unused nodes
- **Right-sizing**: Use VPA for optimal resource allocation

### Estimated Costs (us-east-1)
- **EKS Cluster**: $73/month
- **Worker Nodes**: ~$60/month (3 x t3.medium)
- **RDS**: ~$15/month (t3.micro)
- **ALB**: ~$20/month
- **Data Transfer**: Variable
- **Total**: ~$170/month (minimum)

## 🔄 CI/CD Integration

### GitOps with ArgoCD
```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### GitHub Actions Pipeline
```yaml
name: Deploy to EKS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Configure AWS
      uses: aws-actions/configure-aws-credentials@v1
    - name: Build and push images
      run: ./scripts/build-and-push.sh
    - name: Deploy to EKS
      run: ./scripts/deploy-k8s.sh
```

## 🧪 Testing and Validation

### Load Testing
```bash
# Install hey for load testing
go install github.com/rakyll/hey@latest

# Test frontend
hey -n 1000 -c 10 http://<ALB-URL>/

# Test backend API
hey -n 1000 -c 10 -m POST -H "Content-Type: application/json" -d '{"customer_id":"test","product_id":"test","product_name":"Test","price":"10.99","quantity":1}' http://<ALB-URL>/api/v1/cart/items
```

### Chaos Engineering
```bash
# Install chaos-mesh
curl -sSL https://mirrors.chaos-mesh.org/v2.5.1/install.sh | bash

# Create pod failure experiment
kubectl apply -f chaos-experiments/pod-failure.yaml
```

## 🔮 Advanced Features

### Service Mesh (Istio)
```bash
# Install Istio
curl -L https://istio.io/downloadIstio | sh -
istioctl install --set values.defaultRevision=default
kubectl label namespace shopping-cart istio-injection=enabled
```

### Observability Stack
```bash
# Install Prometheus and Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack
```

### Certificate Management
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## 🧹 Cleanup

### Delete Application
```bash
kubectl delete namespace shopping-cart
```

### Delete Infrastructure
```bash
cd infrastructure_cdk
cdk destroy ShoppingCartEKSStack
```

### Complete Cleanup
```bash
# Delete ECR images
aws ecr list-images --repository-name shopping-cart-frontend --query 'imageIds[*]' --output json | jq '.[] | select(.imageTag != null) | {imageTag}' | aws ecr batch-delete-image --repository-name shopping-cart-frontend --image-ids file:///dev/stdin

aws ecr list-images --repository-name shopping-cart-backend --query 'imageIds[*]' --output json | jq '.[] | select(.imageTag != null) | {imageTag}' | aws ecr batch-delete-image --repository-name shopping-cart-backend --image-ids file:///dev/stdin
```

## 📞 Support

For issues:
1. Check pod logs: `kubectl logs -f deployment/backend-deployment -n shopping-cart`
2. Check events: `kubectl get events -n shopping-cart`
3. Check cluster status: `kubectl get nodes`
4. Review AWS CloudWatch logs
5. Check EKS cluster health in AWS console

## 🎯 Production Readiness Checklist

- [ ] Multi-AZ deployment
- [ ] Database backups enabled
- [ ] Monitoring and alerting configured
- [ ] Log aggregation setup
- [ ] Security scanning in CI/CD
- [ ] Disaster recovery plan
- [ ] Performance testing completed
- [ ] Cost optimization implemented
- [ ] Documentation updated
- [ ] Team training completed

This EKS deployment provides enterprise-grade scalability, security, and observability for the Shopping Cart microservices application!
