# Carthub Quick Start Guide

Get your Carthub shopping cart system up and running in minutes! This guide provides the fastest path to deployment for each architecture option.

## 🚀 Choose Your Adventure

### Option 1: Serverless (5 minutes) ⚡
**Best for**: Quick demos, MVPs, learning

```bash
cd infrastructure_cdk
pip install -r requirements.txt
cdk deploy ShoppingCartServerlessStack
```

### Option 2: Current CI/CD Setup (Ready Now!) 🎉
**Best for**: Production-ready microservices

```bash
# Your infrastructure is already deployed!
# ECR repositories: ✅ Created
# CodeCommit repos: ✅ Created
# Just need to create EKS cluster
```

### Option 3: ECS Microservices (15 minutes) 🐳
**Best for**: Traditional containerized apps

```bash
cd infrastructure_cdk
cdk deploy ShoppingCartMicroservicesStack
```

### Option 4: EKS Kubernetes (20 minutes) ☸️
**Best for**: Cloud-native applications

```bash
cd infrastructure_cdk
cdk deploy ShoppingCartEKSStack
```

## 🎯 Current Status - CI/CD Microservices

**✅ Already Deployed for You:**

### ECR Repositories (Container Registry)
- `013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-frontend`
- `013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-backend`
- `013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-database`

### CodeCommit Repositories (Source Control)
- `https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-frontend`
- `https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-backend`
- `https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-database`

## ⚡ Complete Your CI/CD Setup (10 minutes)

### Step 1: Create EKS Cluster (5 minutes)

**Option A: Using eksctl (Recommended)**
```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster \
  --name carthub-cluster \
  --region us-west-2 \
  --nodegroup-name carthub-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --managed
```

**Option B: Using AWS Console**
1. Go to [EKS Console](https://us-west-2.console.aws.amazon.com/eks/home?region=us-west-2#/clusters)
2. Click "Create cluster"
3. Use existing `EKSServiceRole`
4. Select default VPC and subnets

### Step 2: Push Code to Repositories (3 minutes)

```bash
# Setup Git credentials
git config --global credential.helper '!aws codecommit credential-helper $@'
git config --global credential.UseHttpPath true

# Push frontend code
cd /Workshop/carthub/microservices/frontend
git init && git add . && git commit -m "Initial frontend"
git remote add origin https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-frontend
git push -u origin main

# Push backend code
cd ../backend
git init && git add . && git commit -m "Initial backend"
git remote add origin https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-backend
git push -u origin main

# Push database code
cd ../database
git init && git add . && git commit -m "Initial database"
git remote add origin https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-database
git push -u origin main
```

### Step 3: Build and Deploy (2 minutes)

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 013443956821.dkr.ecr.us-west-2.amazonaws.com

# Build and push images (if Docker is available)
cd /Workshop/carthub/microservices/frontend
docker build -t carthub-frontend .
docker tag carthub-frontend:latest 013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-frontend:latest
docker push 013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-frontend:latest

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name carthub-cluster

# Deploy to Kubernetes
kubectl apply -f k8s/
```

## 🏃‍♂️ Alternative Quick Starts

### Serverless Quick Start

```bash
# 1. Navigate to CDK directory
cd /Workshop/carthub/infrastructure_cdk

# 2. Install dependencies
pip install aws-cdk-lib constructs

# 3. Bootstrap CDK (first time only)
cdk bootstrap

# 4. Deploy serverless stack
cdk deploy ShoppingCartServerlessStack

# 5. Test the API
curl -X POST https://your-api-gateway-url/cart/items \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "test-customer",
    "product_id": "test-product",
    "product_name": "Test Product",
    "price": 29.99,
    "quantity": 1
  }'
```

### ECS Microservices Quick Start

```bash
# 1. Navigate to CDK directory
cd /Workshop/carthub/infrastructure_cdk

# 2. Deploy ECS stack
cdk deploy ShoppingCartMicroservicesStack

# 3. Get the load balancer URL from outputs
aws cloudformation describe-stacks \
  --stack-name ShoppingCartMicroservicesStack \
  --query 'Stacks[0].Outputs'

# 4. Test the application
curl http://your-alb-url/api/v1/cart/test-customer
```

### EKS Kubernetes Quick Start

```bash
# 1. Deploy EKS stack
cd /Workshop/carthub/infrastructure_cdk
cdk deploy ShoppingCartEKSStack

# 2. Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name your-cluster-name

# 3. Deploy applications
kubectl apply -f ../k8s/

# 4. Get service URL
kubectl get ingress -n shopping-cart
```

## 🔍 Verify Your Deployment

### Check Infrastructure
```bash
# ECR repositories
aws ecr describe-repositories --region us-west-2

# CodeCommit repositories
aws codecommit list-repositories --region us-west-2

# EKS cluster
aws eks describe-cluster --name carthub-cluster --region us-west-2
```

### Check Applications
```bash
# Kubernetes resources
kubectl get all -n shopping-cart

# Application health
kubectl get pods -n shopping-cart
kubectl logs -f deployment/frontend-deployment -n shopping-cart
kubectl logs -f deployment/backend-deployment -n shopping-cart
```

### Test API Endpoints
```bash
# Get application URL
ALB_URL=$(kubectl get ingress frontend-ingress -n shopping-cart -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Test frontend
curl http://$ALB_URL/health

# Test backend API
curl http://$ALB_URL/api/v1/cart/test-customer

# Add item to cart
curl -X POST http://$ALB_URL/api/v1/cart/items \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "test-customer",
    "product_id": "laptop-001",
    "product_name": "Gaming Laptop",
    "price": 1299.99,
    "quantity": 1
  }'
```

## 🎯 What You Get

### Serverless Architecture
- ✅ Lambda functions for API
- ✅ DynamoDB for data storage
- ✅ API Gateway for HTTP endpoints
- ✅ CloudWatch for monitoring

### CI/CD Microservices Architecture (Current)
- ✅ 3 ECR repositories with vulnerability scanning
- ✅ 3 CodeCommit repositories with encryption
- ✅ Complete microservice code structure
- ✅ Kubernetes manifests with auto-scaling
- ⏳ EKS cluster (create in Step 1)
- ⏳ CI/CD pipelines (activate with code push)

### ECS Microservices Architecture
- ✅ React frontend in containers
- ✅ FastAPI backend in containers
- ✅ PostgreSQL RDS database
- ✅ Application Load Balancer
- ✅ 3-tier VPC architecture

### EKS Kubernetes Architecture
- ✅ Managed Kubernetes cluster
- ✅ Horizontal Pod Autoscaler
- ✅ Cluster Autoscaler
- ✅ AWS Load Balancer Controller
- ✅ Network policies for security

## 🚨 Troubleshooting Quick Fixes

### Common Issues

#### CDK Bootstrap Error
```bash
# Solution: Bootstrap CDK
cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/us-west-2
```

#### Docker Permission Error
```bash
# Solution: Add user to docker group or use sudo
sudo docker build -t carthub-frontend .
```

#### kubectl Not Found
```bash
# Solution: Install kubectl
curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.28.3/2023-11-14/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin
```

#### EKS Cluster Not Found
```bash
# Solution: Wait for cluster creation or check region
aws eks describe-cluster --name carthub-cluster --region us-west-2
```

#### Git Credentials Error
```bash
# Solution: Configure Git for CodeCommit
git config --global credential.helper '!aws codecommit credential-helper $@'
git config --global credential.UseHttpPath true
```

## 📊 Cost Estimates

### Serverless (Low Traffic)
- **Monthly Cost**: ~$5-10
- **Components**: Lambda, DynamoDB, API Gateway

### CI/CD Microservices
- **Monthly Cost**: ~$133
- **Components**: EKS ($73), EC2 nodes ($60), ECR (minimal)

### ECS Microservices
- **Monthly Cost**: ~$110-165
- **Components**: ECS tasks, RDS, ALB, VPC

### EKS Kubernetes
- **Monthly Cost**: ~$170-270
- **Components**: EKS cluster, EC2 nodes, RDS, ALB

## 🎉 Success Indicators

### Deployment Success
- ✅ Infrastructure deployed without errors
- ✅ Services responding to health checks
- ✅ Database connections established
- ✅ Load balancers routing traffic

### Application Success
- ✅ Frontend loads in browser
- ✅ API endpoints return valid responses
- ✅ Cart operations work correctly
- ✅ Data persists between requests

### Monitoring Success
- ✅ CloudWatch logs showing activity
- ✅ Kubernetes pods in Running state
- ✅ Auto-scaling responding to load
- ✅ Health checks passing

## 🚀 Next Steps

### After Quick Start
1. **Explore the API**: Use the interactive docs at `/docs`
2. **Monitor Performance**: Check CloudWatch dashboards
3. **Scale Testing**: Use load testing tools
4. **Security Review**: Implement authentication
5. **CI/CD Enhancement**: Add automated testing

### Production Readiness
1. **Domain Setup**: Configure custom domain
2. **SSL Certificates**: Enable HTTPS
3. **Monitoring**: Set up alerts and dashboards
4. **Backup Strategy**: Implement data backups
5. **Disaster Recovery**: Plan for failures

### Development Workflow
1. **Local Development**: Set up development environment
2. **Testing Strategy**: Implement comprehensive tests
3. **Code Quality**: Set up linting and formatting
4. **Documentation**: Maintain API documentation
5. **Team Onboarding**: Create developer guides

---

**🎯 You're now ready to build amazing shopping cart experiences with Carthub!**

**Need help?** Check the detailed documentation in the `/docs` folder or open an issue in the repository.
