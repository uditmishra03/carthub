# Carthub Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the Carthub application across different environments and architectures. Choose the deployment option that best fits your requirements.

**Current Status**: ✅ **INFRASTRUCTURE DEPLOYED** (Version 2.0.0)

## 🎉 **What's Already Deployed**

As of August 21, 2025, the following infrastructure is **LIVE and READY**:

### ✅ **Container Registry (ECR) - ACTIVE**
- **3 ECR repositories** with vulnerability scanning enabled
- **Region**: us-west-2
- **Repositories**:
  - `013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-frontend`
  - `013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-backend`
  - `013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-database`

### ✅ **Source Control (CodeCommit) - ACTIVE**
- **3 CodeCommit repositories** with KMS encryption
- **Region**: us-west-2
- **Repositories**:
  - `https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-frontend`
  - `https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-backend`
  - `https://git-codecommit.us-west-2.amazonaws.com/v1/repos/carthub-database`

### ✅ **IAM Roles - CONFIGURED**
- **EKS Service Role**: `arn:aws:iam::013443956821:role/EKSServiceRole`
- **Policies**: AmazonEKSClusterPolicy attached
- **Ready for**: EKS cluster creation

### ✅ **Microservices Code - PRODUCTION READY**
- **Complete React frontend** with shopping cart functionality
- **Complete FastAPI backend** with PostgreSQL integration
- **Database migration service** with schema management
- **Docker containers** optimized for production
- **Kubernetes manifests** with auto-scaling configured

## 🚀 **Quick Access Links**

- **[ECR Console](https://us-west-2.console.aws.amazon.com/ecr/repositories?region=us-west-2)** - View container repositories
- **[CodeCommit Console](https://us-west-2.console.aws.amazon.com/codesuite/codecommit/repositories?region=us-west-2)** - Access source repositories
- **[EKS Console](https://us-west-2.console.aws.amazon.com/eks/home?region=us-west-2#/clusters)** - Create EKS cluster
- **[IAM Console](https://console.aws.amazon.com/iam/home#/roles)** - View service roles

## Table of Contents
- [Prerequisites](#prerequisites)
- [Architecture Options](#architecture-options)
- [Current Deployment Status](#current-deployment-status)
- [Next Steps](#next-steps)
- [Environment Setup](#environment-setup)
- [Deployment Methods](#deployment-methods)
- [Configuration Management](#configuration-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

## Current Deployment Status

### 🎯 **What You Can Do RIGHT NOW**

#### **1. View Your Infrastructure** (0 minutes)
```bash
# List ECR repositories
aws ecr describe-repositories --region us-west-2

# List CodeCommit repositories  
aws codecommit list-repositories --region us-west-2

# Check IAM roles
aws iam get-role --role-name EKSServiceRole
```

#### **2. Build and Push Docker Images** (10 minutes)
```bash
# Get ECR login
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 013443956821.dkr.ecr.us-west-2.amazonaws.com

# Build and push all services
cd /Workshop/carthub/microservices

# Frontend
cd frontend
docker build -t carthub-frontend .
docker tag carthub-frontend:latest 013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-frontend:latest
docker push 013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-frontend:latest

# Backend  
cd ../backend
docker build -t carthub-backend .
docker tag carthub-backend:latest 013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-backend:latest
docker push 013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-backend:latest

# Database
cd ../database
docker build -t carthub-database .
docker tag carthub-database:latest 013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-database:latest
docker push 013443956821.dkr.ecr.us-west-2.amazonaws.com/carthub-database:latest
```

#### **3. Create EKS Cluster** (15-20 minutes)
```bash
# Option 1: Using eksctl (Recommended)
eksctl create cluster \
  --name carthub-cluster \
  --region us-west-2 \
  --nodegroup-name carthub-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed

# Option 2: Using the deployment script
./deploy-eks.sh --region us-west-2 --cluster-name carthub-cluster
```

#### **4. Deploy Applications** (5 minutes)
```bash
# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name carthub-cluster

# Deploy all services
kubectl apply -f microservices/database/k8s/
kubectl apply -f microservices/backend/k8s/
kubectl apply -f microservices/frontend/k8s/

# Verify deployment
kubectl get pods -n shopping-cart
kubectl get services -n shopping-cart
kubectl get ingress -n shopping-cart
```

### 📊 **Infrastructure Cost Analysis**

#### **Current Monthly Costs**
```bash
# Already Deployed (FREE/LOW COST):
├── ECR repositories: ~$0.10/month (minimal storage)
├── CodeCommit repositories: FREE (under 5 users)
├── IAM roles: FREE
└── VPC (basic): FREE

# When EKS is Added:
├── EKS control plane: $73/month
├── EC2 nodes (2x t3.medium): ~$60/month
├── RDS PostgreSQL: ~$25/month (when added)
├── ALB: ~$20/month
└── Data transfer: ~$5/month
# TOTAL: ~$183/month for production setup
```

### 🔄 **Next Steps Priority**

**Priority 1: Create EKS Cluster** (Required for deployment)
- Use eksctl or AWS Console
- Takes 15-20 minutes
- Enables application deployment

**Priority 2: Push Code to Repositories** (Optional, enables CI/CD)
- Copy microservices code to CodeCommit
- Enables automated deployments
- Takes 5 minutes

**Priority 3: Set up CI/CD Pipelines** (Optional, for automation)
- CodePipeline will auto-deploy on code changes
- Requires CodeCommit repositories with code
- Takes 10 minutes to configure

## Next Steps
- **AWS CLI** (v2.0+): For AWS resource management
- **Docker** (v20.0+): For containerization
- **kubectl** (v1.25+): For Kubernetes management
- **Node.js** (v18+): For frontend development
- **Python** (v3.12+): For backend development
- **Git**: For version control

### AWS Account Requirements
- AWS account with appropriate permissions
- IAM roles configured for EKS, ECR, and RDS
- VPC with public and private subnets
- Domain name (optional, for custom URLs)

### Installation Commands
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Docker
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

## Architecture Options

### 1. Serverless Architecture (Recommended for Development)
**Best for**: Rapid prototyping, low traffic, minimal operational overhead

**Components**:
- AWS Lambda for compute
- DynamoDB for data storage
- API Gateway for API management
- CloudFront for content delivery

**Deployment Time**: ~5 minutes
**Monthly Cost**: ~$5-50 (depending on usage)

### 2. ECS Microservices Architecture
**Best for**: Production workloads, predictable traffic, full container control

**Components**:
- ECS Fargate for container orchestration
- PostgreSQL RDS for data storage
- Application Load Balancer
- VPC with multi-AZ deployment

**Deployment Time**: ~15-20 minutes
**Monthly Cost**: ~$110-500 (depending on instance sizes)

### 3. EKS Kubernetes Architecture (Recommended for Production)
**Best for**: High-scale applications, advanced orchestration, DevOps teams

**Components**:
- Amazon EKS for Kubernetes management
- PostgreSQL RDS for data storage
- AWS Load Balancer Controller
- Horizontal Pod Autoscaler
- Cluster Autoscaler

**Deployment Time**: ~20-25 minutes
**Monthly Cost**: ~$170-1000+ (depending on scale)

## Environment Setup

### Development Environment
```bash
# Clone repository
git clone https://github.com/your-org/carthub.git
cd carthub

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Run tests
python -m pytest tests/ -v
```

### AWS Configuration
```bash
# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format

# Verify configuration
aws sts get-caller-identity

# Create ECR repositories (if using containers)
aws ecr create-repository --repository-name carthub-frontend
aws ecr create-repository --repository-name carthub-backend
```

## Deployment Methods

### Method 1: One-Command EKS Deployment (Recommended)

This is the fastest way to deploy the complete Carthub application to production.

```bash
# Make deployment script executable
chmod +x deploy-eks.sh

# Deploy with default settings
./deploy-eks.sh

# Deploy with custom configuration
./deploy-eks.sh --region us-west-2 --cluster-name my-carthub --node-count 3
```

**What this script does**:
1. Creates EKS cluster with managed node groups
2. Builds and pushes Docker images to ECR
3. Deploys PostgreSQL RDS instance
4. Configures networking and security groups
5. Deploys application to Kubernetes
6. Sets up monitoring and logging
7. Configures auto-scaling policies

### Method 2: Manual EKS Deployment

For more control over the deployment process:

#### Step 1: Infrastructure Setup
```bash
cd infrastructure_cdk

# Install CDK dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy EKS infrastructure
cdk deploy CarthubEKSStack
```

#### Step 2: Build and Push Images
```bash
# Build and push images to ECR
./scripts/build-and-push.sh

# Verify images are pushed
aws ecr list-images --repository-name carthub-frontend
aws ecr list-images --repository-name carthub-backend
```

#### Step 3: Deploy to Kubernetes
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name carthub-cluster

# Deploy application
kubectl apply -f k8s/

# Verify deployment
kubectl get pods -n shopping-cart
kubectl get services -n shopping-cart
```

### Method 3: ECS Deployment

For container-based deployment without Kubernetes:

```bash
cd infrastructure_cdk

# Deploy ECS infrastructure
cdk deploy CarthubMicroservicesStack

# Monitor deployment
aws ecs describe-services --cluster carthub-cluster --services carthub-frontend carthub-backend
```

### Method 4: Serverless Deployment

For serverless architecture:

```bash
cd infrastructure_cdk

# Deploy serverless stack
cdk deploy CarthubServerlessStack

# Test API endpoint
curl -X GET "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health"
```

## Configuration Management

### Environment Variables

#### Backend Configuration
```bash
# Database configuration
DATABASE_URL=postgresql://username:password@host:5432/carthub
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis configuration (for caching)
REDIS_URL=redis://redis-cluster:6379/0

# JWT configuration
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# AWS configuration
AWS_REGION=us-east-1
AWS_S3_BUCKET=carthub-assets
```

#### Frontend Configuration
```bash
# API configuration
REACT_APP_API_BASE_URL=https://api.carthub.com/api/v1
REACT_APP_ENVIRONMENT=production

# Analytics configuration
REACT_APP_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
REACT_APP_HOTJAR_ID=XXXXXXX
```

### Kubernetes ConfigMaps and Secrets

#### ConfigMap Example
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: carthub-config
  namespace: shopping-cart
data:
  DATABASE_POOL_SIZE: "20"
  JWT_ALGORITHM: "HS256"
  AWS_REGION: "us-east-1"
```

#### Secret Example
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: carthub-secrets
  namespace: shopping-cart
type: Opaque
data:
  DATABASE_URL: <base64-encoded-database-url>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
```

### Applying Configuration
```bash
# Create namespace
kubectl create namespace shopping-cart

# Apply configuration
kubectl apply -f k8s/config/configmap.yaml
kubectl apply -f k8s/config/secrets.yaml

# Verify configuration
kubectl get configmaps -n shopping-cart
kubectl get secrets -n shopping-cart
```

## Monitoring and Logging

### CloudWatch Integration

#### Log Groups Setup
```bash
# Create log groups
aws logs create-log-group --log-group-name /aws/eks/carthub/frontend
aws logs create-log-group --log-group-name /aws/eks/carthub/backend
aws logs create-log-group --log-group-name /aws/eks/carthub/database
```

#### Metrics and Alarms
```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "CarthubHighCPU" \
  --alarm-description "High CPU usage" \
  --metric-name CPUUtilization \
  --namespace AWS/EKS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

### Kubernetes Monitoring

#### Prometheus and Grafana Setup
```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Access Grafana dashboard
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Open http://localhost:3000 (admin/prom-operator)
```

#### Application Metrics
```bash
# View application logs
kubectl logs -f deployment/backend-deployment -n shopping-cart
kubectl logs -f deployment/frontend-deployment -n shopping-cart

# Monitor resource usage
kubectl top pods -n shopping-cart
kubectl top nodes
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Pod Startup Issues
**Problem**: Pods stuck in `Pending` or `CrashLoopBackOff` state

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n shopping-cart
kubectl logs <pod-name> -n shopping-cart --previous
```

**Common Solutions**:
- Check resource requests and limits
- Verify image pull secrets
- Ensure ConfigMaps and Secrets exist
- Check node capacity and scheduling constraints

#### 2. Database Connection Issues
**Problem**: Backend cannot connect to database

**Diagnosis**:
```bash
# Test database connectivity
kubectl exec -it <backend-pod> -n shopping-cart -- psql $DATABASE_URL -c "SELECT 1;"

# Check security groups
aws ec2 describe-security-groups --group-ids <rds-security-group-id>
```

**Solutions**:
- Verify database credentials in secrets
- Check security group rules
- Ensure RDS instance is in correct subnets
- Verify DNS resolution

#### 3. Load Balancer Issues
**Problem**: External access not working

**Diagnosis**:
```bash
# Check load balancer status
kubectl get ingress -n shopping-cart
kubectl describe ingress carthub-ingress -n shopping-cart

# Check AWS Load Balancer Controller
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

**Solutions**:
- Verify AWS Load Balancer Controller is installed
- Check IAM permissions for load balancer controller
- Ensure proper annotations on ingress
- Verify target group health

#### 4. Auto-scaling Issues
**Problem**: Pods not scaling as expected

**Diagnosis**:
```bash
# Check HPA status
kubectl get hpa -n shopping-cart
kubectl describe hpa backend-hpa -n shopping-cart

# Check metrics server
kubectl top pods -n shopping-cart
```

**Solutions**:
- Verify metrics server is running
- Check resource requests are set on pods
- Ensure HPA configuration is correct
- Monitor cluster autoscaler logs

### Performance Optimization

#### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_cart_customer_id ON cart_items(customer_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM cart_items WHERE customer_id = 'customer-123';
```

#### Application Optimization
```bash
# Optimize Docker images
docker build --target production -t carthub-backend:optimized .

# Use multi-stage builds to reduce image size
# Enable gzip compression in nginx
# Implement Redis caching for frequently accessed data
```

### Backup and Recovery

#### Database Backup
```bash
# Create RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier carthub-db \
  --db-snapshot-identifier carthub-backup-$(date +%Y%m%d)

# Automated backup configuration
aws rds modify-db-instance \
  --db-instance-identifier carthub-db \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"
```

#### Application Backup
```bash
# Backup Kubernetes configurations
kubectl get all -n shopping-cart -o yaml > carthub-k8s-backup.yaml

# Backup persistent volumes
kubectl get pv,pvc -n shopping-cart -o yaml > carthub-storage-backup.yaml
```

### Security Checklist

- [ ] Enable encryption at rest for RDS
- [ ] Use AWS Secrets Manager for sensitive data
- [ ] Implement network policies in Kubernetes
- [ ] Enable VPC Flow Logs
- [ ] Configure security groups with least privilege
- [ ] Enable CloudTrail for audit logging
- [ ] Implement pod security policies
- [ ] Use non-root containers
- [ ] Enable image vulnerability scanning
- [ ] Implement proper RBAC in Kubernetes

### Scaling Guidelines

#### Horizontal Scaling
```yaml
# HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-deployment
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### Vertical Scaling
```bash
# Update resource limits
kubectl patch deployment backend-deployment -n shopping-cart -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"limits":{"cpu":"1000m","memory":"2Gi"},"requests":{"cpu":"500m","memory":"1Gi"}}}]}}}}'
```

## Support and Maintenance

### Regular Maintenance Tasks
- **Weekly**: Review CloudWatch logs and metrics
- **Monthly**: Update container images and security patches
- **Quarterly**: Review and optimize resource allocation
- **Annually**: Conduct security audit and disaster recovery testing

### Getting Help
- **Documentation**: Check this guide and API documentation
- **Logs**: Review application and infrastructure logs
- **Monitoring**: Use CloudWatch and Grafana dashboards
- **Support**: Contact the development team for assistance

### Version Updates
```bash
# Update application version
kubectl set image deployment/backend-deployment backend=carthub-backend:v2.1.0 -n shopping-cart
kubectl set image deployment/frontend-deployment frontend=carthub-frontend:v2.1.0 -n shopping-cart

# Monitor rollout
kubectl rollout status deployment/backend-deployment -n shopping-cart
kubectl rollout status deployment/frontend-deployment -n shopping-cart
```

---

*This deployment guide is maintained by the Carthub development team. For updates and additional information, please refer to the project repository.*
