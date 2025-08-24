# Carthub Backend Microservice

FastAPI-based backend service for the Carthub shopping cart system.

## Architecture

This microservice is part of a complete CI/CD pipeline that includes:
- **Source Control**: AWS CodeCommit
- **CI/CD Pipeline**: AWS CodePipeline + CodeBuild
- **Container Registry**: Amazon ECR
- **Orchestration**: Amazon EKS
- **Database**: Amazon RDS PostgreSQL
- **Secrets Management**: AWS Secrets Manager

## Features

- FastAPI with automatic OpenAPI documentation
- SQLAlchemy ORM with PostgreSQL
- Pydantic models for data validation
- Comprehensive test suite with pytest
- Docker containerization
- Kubernetes deployment with auto-scaling
- Database connection pooling
- Health checks and monitoring

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /api/v1/cart/{customer_id}` - Get cart contents
- `POST /api/v1/cart/items` - Add item to cart
- `PUT /api/v1/cart/{customer_id}/items/{product_id}` - Update item quantity
- `DELETE /api/v1/cart/{customer_id}/items/{product_id}` - Remove item
- `DELETE /api/v1/cart/{customer_id}` - Clear cart
- `POST /api/v1/cart/checkout` - Process checkout

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/carthub"

# Run development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
python -m pytest tests/ -v --cov=app

# Access API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## Docker Build

```bash
# Build image
docker build -t carthub-backend .

# Run container
docker run -p 8000:8000 -e DATABASE_URL="postgresql://..." carthub-backend
```

## Kubernetes Deployment

The application is automatically deployed to EKS via the CI/CD pipeline when code is pushed to the main branch.

### Manual Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `DB_USERNAME`: Database username (from Kubernetes secret)
- `DB_PASSWORD`: Database password (from Kubernetes secret)
- `ENVIRONMENT`: Environment (development/production)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

## Database Schema

The backend uses the following tables:
- `carts`: Customer shopping carts
- `cart_items`: Items in shopping carts
- `orders`: Completed orders
- `order_items`: Items in completed orders

## CI/CD Pipeline

The pipeline includes the following stages:

1. **Source**: Triggered by commits to main branch
2. **Build**: 
   - Install dependencies
   - Run tests with coverage
   - Build Docker image
   - Push to ECR
3. **Deploy**:
   - Create database secrets in Kubernetes
   - Update Kubernetes deployment
   - Apply manifests to EKS cluster

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_cart_routes.py -v
```

## Monitoring

- Health check endpoint: `/health`
- Kubernetes readiness and liveness probes
- Horizontal Pod Autoscaler based on CPU/memory
- Database connection monitoring
- Application metrics and logging

## Security

- Non-root container user
- Read-only root filesystem
- Security contexts and capabilities dropped
- Database credentials stored in Kubernetes secrets
- Network policies for pod-to-pod communication
- Input validation with Pydantic models

## Scaling

- **Horizontal Pod Autoscaler**: 2-15 replicas based on CPU/memory
- **Cluster Autoscaler**: Automatic node scaling
- **Pod Anti-Affinity**: Distribute pods across nodes
- **Database Connection Pooling**: Efficient database connections

## Database Integration

The backend integrates with Amazon RDS PostgreSQL:
- Automatic failover and backups
- Connection pooling with SQLAlchemy
- Database migrations handled by separate microservice
- Secrets managed by AWS Secrets Manager

## Troubleshooting

```bash
# Check pod status
kubectl get pods -n shopping-cart

# View logs
kubectl logs -f deployment/backend-deployment -n shopping-cart

# Check service
kubectl get service backend-service -n shopping-cart

# Describe deployment
kubectl describe deployment backend-deployment -n shopping-cart

# Check database connectivity
kubectl exec -it deployment/backend-deployment -n shopping-cart -- python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT version();')
    print(result.fetchone())
"
```

## API Documentation

Once deployed, the API documentation is available at:
- Swagger UI: `http://<alb-hostname>/docs`
- ReDoc: `http://<alb-hostname>/redoc`
