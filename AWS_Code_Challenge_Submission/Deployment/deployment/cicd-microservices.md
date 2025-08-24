# Carthub Microservices CI/CD Deployment Guide

This guide walks you through deploying the complete Carthub microservices architecture with AWS CodeCommit, CodePipeline, ECR, and EKS.

## 🏗️ Architecture Overview

The microservices CI/CD architecture includes:

### Infrastructure Components
- **3 CodeCommit Repositories**: Separate repos for frontend, backend, and database
- **3 CodePipeline Pipelines**: Automated CI/CD for each microservice
- **3 ECR Repositories**: Container image storage with lifecycle policies
- **EKS Cluster**: Managed Kubernetes with auto-scaling
- **RDS PostgreSQL**: Managed database with automated backups
- **VPC**: 3-tier network architecture with security groups
- **AWS Secrets Manager**: Secure credential storage

### Microservices
1. **Frontend Service**: React SPA with nginx
2. **Backend Service**: FastAPI with PostgreSQL
3. **Database Service**: Schema management and migrations

### CI/CD Pipeline Flow
```
Code Push → CodeCommit → CodePipeline → CodeBuild → ECR → EKS Deployment
```

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **AWS CDK** installed (`npm install -g aws-cdk`)
3. **kubectl** for Kubernetes management
4. **Docker** for local testing (optional)
5. **Git** for repository management

### One-Command Deployment

```bash
# Deploy the complete infrastructure
./deploy-microservices-cicd.sh

# Setup repositories with your code
./setup-repositories.sh

# Monitor deployments
./monitor-deployments.sh
```

## 📋 Detailed Deployment Steps

### Step 1: Deploy Infrastructure

```bash
# Navigate to the project directory
cd /Workshop/carthub

# Make the deployment script executable
chmod +x deploy-microservices-cicd.sh

# Deploy with default settings (us-west-2)
./deploy-microservices-cicd.sh

# Or deploy with custom settings
./deploy-microservices-cicd.sh --region us-east-1 --profile my-profile
```

**What this creates:**
- EKS cluster with managed node groups
- 3 CodeCommit repositories
- 3 CodePipeline pipelines
- 3 ECR repositories
- RDS PostgreSQL database
- VPC with public/private/database subnets
- IAM roles and policies
- S3 bucket for pipeline artifacts

### Step 2: Setup Repositories

```bash
# Run the repository setup script
./setup-repositories.sh
```

**What this does:**
- Clones each empty CodeCommit repository
- Copies microservice code to respective repositories
- Commits and pushes initial code
- Triggers the CI/CD pipelines

### Step 3: Monitor Deployment

```bash
# Monitor the deployment progress
./monitor-deployments.sh
```

**What this shows:**
- CodePipeline execution status
- EKS deployment status
- Pod and service health
- Application URL when ready

## 🔧 Manual Deployment (Advanced)

If you prefer manual control over the deployment:

### 1. Deploy CDK Stack

```bash
cd infrastructure_cdk

# Install dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy CarthubMicroservicesCicd --require-approval never
```

### 2. Configure kubectl

```bash
# Update kubeconfig for the new EKS cluster
aws eks update-kubeconfig --region us-west-2 --name carthub-cluster
```

### 3. Setup Repositories Manually

```bash
# Get repository URLs from CloudFormation outputs
aws cloudformation describe-stacks --stack-name CarthubMicroservicesCicd \
  --query 'Stacks[0].Outputs'

# Clone and setup each repository
git clone <frontend-repo-url> carthub-frontend
cd carthub-frontend
cp -r ../microservices/frontend/* .
git add .
git commit -m "Initial frontend microservice"
git push origin main
```

## 📊 Monitoring and Observability

### Pipeline Monitoring

```bash
# Check pipeline status
aws codepipeline list-pipelines
aws codepipeline get-pipeline-state --name carthub-frontend-pipeline

# View build logs
aws logs describe-log-groups --log-group-name-prefix /aws/codebuild/carthub
```

### EKS Monitoring

```bash
# Check cluster status
kubectl get nodes
kubectl get namespaces

# Check application status
kubectl get all -n shopping-cart

# View logs
kubectl logs -f deployment/frontend-deployment -n shopping-cart
kubectl logs -f deployment/backend-deployment -n shopping-cart
```

### Application Access

```bash
# Get the application URL
kubectl get ingress frontend-ingress -n shopping-cart \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## 🔒 Security Features

### Network Security
- **VPC Isolation**: 3-tier network architecture
- **Security Groups**: Restrictive ingress/egress rules
- **Network Policies**: Kubernetes pod-to-pod communication control
- **Private Subnets**: Backend and database in private subnets

### Container Security
- **Non-root Users**: All containers run as non-root
- **Read-only Filesystems**: Immutable container filesystems
- **Security Contexts**: Dropped capabilities and privilege escalation prevention
- **Image Scanning**: ECR vulnerability scanning

### Secrets Management
- **AWS Secrets Manager**: Database credentials
- **Kubernetes Secrets**: Runtime secret injection
- **IAM Roles**: Service-specific permissions
- **IRSA**: IAM roles for service accounts

## 📈 Scaling and Performance

### Auto Scaling
- **Horizontal Pod Autoscaler**: CPU/memory-based pod scaling
- **Cluster Autoscaler**: Node-level scaling
- **Application Load Balancer**: Traffic distribution
- **RDS Scaling**: Database read replicas (configurable)

### Performance Optimization
- **Container Resource Limits**: Guaranteed resources
- **Database Connection Pooling**: Efficient database connections
- **CDN Integration**: Static asset caching (configurable)
- **Caching Strategies**: Application-level caching

## 🛠️ Customization

### Environment Configuration

Edit the deployment script or CDK parameters:

```bash
# Custom region and stack name
./deploy-microservices-cicd.sh --region eu-west-1 --stack-name MyCartHub

# Custom EKS configuration
# Edit infrastructure_cdk/microservices_cicd_stack.py
```

### Application Configuration

Modify microservice configurations:

```bash
# Frontend configuration
# Edit microservices/frontend/src/config.js

# Backend configuration  
# Edit microservices/backend/app/config/settings.py

# Database schema
# Edit microservices/database/migrate.py
```

### Kubernetes Configuration

Customize Kubernetes manifests:

```bash
# Scaling configuration
# Edit microservices/*/k8s/hpa.yaml

# Resource limits
# Edit microservices/*/k8s/deployment.yaml

# Network policies
# Edit microservices/database/k8s/network-policies.yaml
```

## 🔄 CI/CD Pipeline Details

### Pipeline Stages

Each microservice pipeline includes:

1. **Source Stage**
   - Triggered by CodeCommit push
   - Pulls latest code from main branch

2. **Build Stage**
   - Installs dependencies
   - Runs tests (backend only)
   - Builds Docker image
   - Pushes to ECR

3. **Deploy Stage**
   - Updates Kubernetes manifests
   - Applies to EKS cluster
   - Verifies deployment

### Build Specifications

Each microservice has a `buildspec.yml` that defines:
- Pre-build commands (authentication, setup)
- Build commands (test, compile, containerize)
- Post-build commands (push, deploy)

### Deployment Strategy

- **Rolling Updates**: Zero-downtime deployments
- **Health Checks**: Readiness and liveness probes
- **Rollback**: Automatic rollback on failure
- **Blue-Green**: Can be configured for critical services

## 🐛 Troubleshooting

### Common Issues

#### Pipeline Failures
```bash
# Check build logs
aws logs describe-log-groups --log-group-name-prefix /aws/codebuild/carthub

# Check pipeline execution
aws codepipeline get-pipeline-execution --pipeline-name carthub-frontend-pipeline
```

#### EKS Deployment Issues
```bash
# Check pod status
kubectl describe pod <pod-name> -n shopping-cart

# Check events
kubectl get events -n shopping-cart --sort-by='.lastTimestamp'

# Check ingress
kubectl describe ingress frontend-ingress -n shopping-cart
```

#### Database Connection Issues
```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql postgresql://username:password@host:5432/carthub

# Check secrets
kubectl get secrets -n shopping-cart
kubectl describe secret db-secret -n shopping-cart
```

### Debug Commands

```bash
# Get all resources
kubectl get all -n shopping-cart

# Check logs
kubectl logs -f deployment/backend-deployment -n shopping-cart

# Execute into pod
kubectl exec -it deployment/backend-deployment -n shopping-cart -- /bin/bash

# Port forward for local testing
kubectl port-forward service/backend-service 8000:8000 -n shopping-cart
```

## 🧹 Cleanup

### Delete Everything

```bash
# Delete the CDK stack (this removes all resources)
cd infrastructure_cdk
cdk destroy CarthubMicroservicesCicd

# Clean up local repositories
rm -rf carthub-frontend carthub-backend carthub-database
```

### Selective Cleanup

```bash
# Delete only EKS resources
kubectl delete namespace shopping-cart

# Delete only pipelines
aws codepipeline delete-pipeline --name carthub-frontend-pipeline
aws codepipeline delete-pipeline --name carthub-backend-pipeline
aws codepipeline delete-pipeline --name carthub-database-pipeline
```

## 📚 Additional Resources

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [AWS CodePipeline Documentation](https://docs.aws.amazon.com/codepipeline/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review CloudWatch logs
- Open an issue in the repository
- Contact the development team

---

**Note**: This deployment creates AWS resources that incur costs. Monitor your usage and clean up resources when not needed.
