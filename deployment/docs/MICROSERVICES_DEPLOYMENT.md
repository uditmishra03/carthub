# 3-Tier Microservices Deployment Guide

This guide covers deploying the Shopping Cart application using a 3-tier microservices architecture with AWS VPC.

## 🏗️ Architecture Overview

The application is split into three microservices deployed across a secure 3-tier VPC:

### 1. **Public Tier (Web Tier)**
- **Frontend Service**: React application served via nginx
- **Application Load Balancer**: Routes traffic to frontend containers
- **Internet Gateway**: Provides internet access
- **Security**: Only HTTP/HTTPS traffic allowed from internet

### 2. **Private Tier (Application Tier)**
- **Backend Service**: FastAPI application with business logic
- **Internal Load Balancer**: Routes traffic from frontend to backend
- **NAT Gateway**: Provides outbound internet access for updates
- **Security**: Only accepts traffic from frontend tier

### 3. **Database Tier (Data Tier)**
- **PostgreSQL RDS**: Managed database service
- **Isolated Subnets**: No internet access
- **Security**: Only accepts connections from backend tier

## 🚀 Deployment Steps

### Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **AWS CDK CLI installed**: `npm install -g aws-cdk`
3. **Docker installed** for building container images
4. **Python 3.12+** for CDK deployment
5. **Node.js 18+** for frontend build

### Step 1: Prepare the Environment

```bash
# Navigate to the project directory
cd /Workshop/carthub

# Install CDK dependencies
cd infrastructure_cdk
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap
```

### Step 2: Build and Test Services Locally (Optional)

#### Backend Service
```bash
cd ../backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables for local testing
export DATABASE_ENDPOINT=localhost
export DATABASE_NAME=shoppingcart
export DATABASE_PORT=5432
export DATABASE_CREDENTIALS='{"username":"cartadmin","password":"password"}'

# Run the backend service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Service
```bash
cd ../frontend

# Install dependencies
npm install

# Set environment variable for backend API
export REACT_APP_API_URL=http://localhost:8000/api/v1

# Run the frontend service
npm start
```

### Step 3: Deploy the Infrastructure

```bash
cd ../infrastructure_cdk

# Deploy the microservices stack
cdk deploy ShoppingCartMicroservicesStack

# The deployment will output:
# - VPC ID
# - Database endpoint
# - Frontend URL
# - Backend URL (internal)
```

### Step 4: Verify Deployment

1. **Check VPC Resources**:
   - VPC with 3 subnet types across 2 AZs
   - Internet Gateway attached
   - NAT Gateway in public subnet
   - Route tables configured correctly

2. **Check Security Groups**:
   - ALB: Allows HTTP/HTTPS from internet
   - Frontend: Allows traffic from ALB
   - Backend: Allows traffic from Frontend
   - Database: Allows traffic from Backend only

3. **Check Services**:
   - ECS Cluster running
   - Frontend and Backend services healthy
   - RDS database accessible from backend

4. **Test Application**:
   - Access frontend URL from deployment output
   - Add items to cart
   - Verify cart operations work
   - Test checkout process

## 🔧 Configuration

### Environment Variables

#### Backend Service
- `DATABASE_ENDPOINT`: RDS endpoint (auto-configured)
- `DATABASE_NAME`: Database name (default: shoppingcart)
- `DATABASE_PORT`: Database port (default: 5432)
- `DATABASE_CREDENTIALS`: Secrets Manager secret (auto-configured)
- `AWS_REGION`: AWS region (auto-configured)

#### Frontend Service
- `REACT_APP_API_URL`: Backend API URL (configured via nginx proxy)

### Secrets Management

Database credentials are automatically managed via AWS Secrets Manager:
- Username: `cartadmin`
- Password: Auto-generated 32-character password
- Rotation: Can be enabled for production

## 📊 Monitoring and Logging

### CloudWatch Logs
- **Frontend Logs**: `/ecs/shopping-cart-frontend`
- **Backend Logs**: `/ecs/shopping-cart-backend`
- **VPC Flow Logs**: `/aws/vpc/flowlogs`

### Health Checks
- **Frontend**: `GET /health` (nginx health check)
- **Backend**: `GET /health` (application health check)
- **Database**: Connection test via backend health check

### Metrics
- ECS service metrics (CPU, memory, task count)
- ALB metrics (request count, latency, errors)
- RDS metrics (connections, CPU, storage)

## 🔒 Security Features

### Network Security
- **VPC Flow Logs**: Monitor all network traffic
- **Security Groups**: Least privilege access
- **NACLs**: Additional subnet-level protection
- **Private Subnets**: Backend and database not directly accessible

### Data Security
- **Encryption at Rest**: RDS storage encrypted
- **Encryption in Transit**: HTTPS/TLS for all communications
- **Secrets Management**: Database credentials in Secrets Manager
- **IAM Roles**: Least privilege access for services

### Application Security
- **Input Validation**: Pydantic models validate all inputs
- **Error Handling**: No sensitive information in error messages
- **CORS Configuration**: Controlled cross-origin requests

## 🚀 Scaling and Performance

### Auto Scaling
- **ECS Services**: Auto-scale based on CPU/memory
- **RDS**: Can be upgraded to Multi-AZ for HA
- **Load Balancers**: Automatically distribute traffic

### Performance Optimization
- **Connection Pooling**: SQLAlchemy connection pooling
- **Caching**: Can add ElastiCache for session/data caching
- **CDN**: Can add CloudFront for static assets

## 🔄 CI/CD Integration

### Recommended Pipeline
1. **Source**: Git repository (GitHub/CodeCommit)
2. **Build**: 
   - Build Docker images for frontend/backend
   - Run tests
   - Push images to ECR
3. **Deploy**:
   - Update ECS services with new images
   - Run database migrations if needed
   - Perform health checks

### Blue/Green Deployment
- Use ECS service deployment configuration
- Route traffic gradually to new version
- Rollback capability if issues detected

## 🧪 Testing

### Integration Testing
```bash
# Test backend API
curl -X POST http://backend-url/api/v1/cart/items \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "test-customer",
    "product_id": "test-product",
    "product_name": "Test Product",
    "price": "10.99",
    "quantity": 1
  }'

# Test frontend
curl http://frontend-url/health
```

### Load Testing
- Use tools like Apache Bench, JMeter, or Artillery
- Test both frontend and backend endpoints
- Monitor performance metrics during tests

## 🔧 Troubleshooting

### Common Issues

1. **Service Not Starting**:
   - Check ECS task logs in CloudWatch
   - Verify environment variables
   - Check security group rules

2. **Database Connection Issues**:
   - Verify security group allows backend access
   - Check database credentials in Secrets Manager
   - Ensure database is in correct subnet group

3. **Frontend Can't Reach Backend**:
   - Check nginx proxy configuration
   - Verify backend service is healthy
   - Check internal load balancer configuration

### Debugging Commands
```bash
# Check ECS service status
aws ecs describe-services --cluster shopping-cart-cluster --services frontend-service backend-service

# Check task logs
aws logs get-log-events --log-group-name /ecs/shopping-cart-backend --log-stream-name <stream-name>

# Check RDS status
aws rds describe-db-instances --db-instance-identifier <db-instance-id>
```

## 💰 Cost Optimization

### Development Environment
- Use t3.micro instances for RDS
- Single AZ deployment
- Minimal ECS task resources

### Production Environment
- Multi-AZ RDS for high availability
- Auto Scaling for ECS services
- Reserved instances for predictable workloads

## 🔮 Future Enhancements

1. **Service Mesh**: Implement AWS App Mesh for advanced traffic management
2. **Observability**: Add X-Ray tracing and custom metrics
3. **Caching**: Implement Redis/ElastiCache for performance
4. **Message Queues**: Add SQS/SNS for asynchronous processing
5. **API Gateway**: Add API Gateway for additional features (rate limiting, API keys)
6. **Container Insights**: Enable detailed container monitoring

## 📞 Support

For issues or questions:
1. Check CloudWatch logs for error details
2. Review security group configurations
3. Verify service health checks
4. Check AWS service limits and quotas

## 🧹 Cleanup

To avoid ongoing charges, destroy the infrastructure when done:

```bash
cd infrastructure_cdk
cdk destroy ShoppingCartMicroservicesStack
```

This will remove all resources including:
- VPC and networking components
- ECS cluster and services
- RDS database
- Load balancers
- Security groups
- CloudWatch logs (with retention period)
