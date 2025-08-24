# Backend Microservice Documentation

The backend microservice is a FastAPI-based REST API that provides the core business logic and data management for the Carthub shopping cart system.

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI with automatic OpenAPI documentation
- **Database ORM**: SQLAlchemy with PostgreSQL
- **Validation**: Pydantic models for data validation
- **Testing**: pytest with comprehensive test coverage
- **Container**: Python 3.12 slim with security hardening

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│  FastAPI App    │───▶│  PostgreSQL     │
│   Service       │    │  (Port 8000)    │    │  Database       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Secrets Manager │
                       │ (DB Credentials)│
                       └─────────────────┘
```

## 📁 Directory Structure

```
backend/
├── app/                        # FastAPI application
│   ├── config/                 # Configuration management
│   │   ├── database.py         # Database connection setup
│   │   └── settings.py         # Application settings
│   ├── models/                 # SQLAlchemy models
│   │   ├── cart.py            # Cart data models
│   │   └── schemas.py         # Pydantic schemas
│   ├── routes/                 # API route handlers
│   │   ├── cart_routes.py     # Cart API endpoints
│   │   └── health_routes.py   # Health check endpoints
│   ├── services/               # Business logic services
│   │   └── cart_service.py    # Cart business logic
│   └── main.py                # FastAPI application entry point
├── k8s/                        # Kubernetes manifests
│   ├── deployment.yaml         # Pod deployment configuration
│   ├── service.yaml            # Service exposure
│   ├── hpa.yaml               # Horizontal Pod Autoscaler
│   └── namespace.yaml         # Kubernetes namespace
├── tests/                      # Test suite
│   └── test_api.py            # API integration tests
├── Dockerfile                  # Container configuration
├── buildspec.yml              # CodeBuild CI/CD pipeline
├── requirements.txt           # Python dependencies
└── README.md                  # Service documentation
```

## 🐳 Docker Configuration

### Production Container
```dockerfile
FROM python:3.12-slim

# Security and optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Features
- Non-root user execution
- Read-only root filesystem
- Minimal system dependencies
- Health check integration

## 📡 API Endpoints

### Core Shopping Cart API

#### GET `/api/v1/cart/{customer_id}`
Get cart contents for a customer.

**Response:**
```json
{
  "customer_id": "customer-123",
  "items": [
    {
      "product_id": "prod-456",
      "product_name": "Gaming Laptop",
      "price": 1299.99,
      "quantity": 1
    }
  ],
  "total_items": 1,
  "subtotal": 1299.99
}
```

#### POST `/api/v1/cart/items`
Add item to shopping cart.

**Request:**
```json
{
  "customer_id": "customer-123",
  "product_id": "prod-456",
  "product_name": "Gaming Laptop",
  "price": 1299.99,
  "quantity": 1
}
```

#### PUT `/api/v1/cart/{customer_id}/items/{product_id}`
Update item quantity in cart.

**Request:**
```json
{
  "quantity": 2
}
```

#### DELETE `/api/v1/cart/{customer_id}/items/{product_id}`
Remove item from cart.

#### DELETE `/api/v1/cart/{customer_id}`
Clear entire cart.

#### POST `/api/v1/cart/checkout`
Process checkout and create order.

**Request:**
```json
{
  "customer_id": "customer-123",
  "payment_method": "credit_card",
  "shipping_address": {
    "street": "123 Main St",
    "city": "Seattle",
    "state": "WA",
    "zip": "98101"
  }
}
```

### System Endpoints

#### GET `/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-21T18:26:30Z",
  "database": "connected"
}
```

#### GET `/`
Service information endpoint.

**Response:**
```json
{
  "service": "Shopping Cart Backend",
  "version": "2.0.0",
  "status": "running"
}
```

## 🗄️ Database Schema

### Tables

#### `carts`
```sql
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `cart_items`
```sql
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    product_id VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cart_id, product_id)
);
```

#### `orders`
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `order_items`
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Constraints
- Optimized indexes for common queries
- Foreign key constraints for data integrity
- Unique constraints to prevent duplicates
- Automatic timestamp updates with triggers

## ☸️ Kubernetes Configuration

### Deployment
- **Replicas**: 3 pods for high availability
- **Resource Limits**: 512Mi memory, 500m CPU
- **Health Checks**: Readiness and liveness probes
- **Security Context**: Non-root user, read-only filesystem

### Environment Variables
```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: database_url
- name: DB_USERNAME
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: username
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: password
- name: ENVIRONMENT
  value: "production"
- name: LOG_LEVEL
  value: "INFO"
```

### Horizontal Pod Autoscaler (HPA)
- **Min Replicas**: 2
- **Max Replicas**: 15
- **Scaling Metrics**: CPU (70%) and Memory (80%)
- **Aggressive Scale Up**: 100% increase per minute
- **Conservative Scale Down**: 10% decrease per minute

## 🔄 CI/CD Pipeline

### Build Stages
1. **Pre-build**: ECR authentication, dependency installation
2. **Build**: Run tests with coverage, build Docker image
3. **Post-build**: ECR push, Kubernetes deployment, secret management

### Pipeline Features
- **Automated Testing**: pytest with coverage reporting
- **Code Quality**: Linting with flake8 and black
- **Security Scanning**: ECR vulnerability scanning
- **Database Migration**: Automated schema updates
- **Rolling Deployment**: Zero-downtime updates

### Test Coverage
```bash
# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=xml

# Coverage requirements
--cov-fail-under=80
```

## 🧪 Testing Strategy

### Test Categories
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Database and API integration
- **Contract Tests**: API contract validation
- **Performance Tests**: Load and stress testing

### Test Configuration
```python
# pytest configuration
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### Mock Strategy
```python
# Database mocking
@patch('app.routes.cart_routes.get_db')
def test_get_cart_empty(mock_get_db):
    mock_db = Mock()
    mock_get_db.return_value = mock_db
    # Test implementation
```

## 📊 Monitoring and Observability

### Health Checks
- **Readiness Probe**: Database connectivity check
- **Liveness Probe**: Application health check
- **Startup Probe**: Initial container readiness

### Metrics
- **Request Metrics**: Response times, error rates, throughput
- **Database Metrics**: Connection pool, query performance
- **Business Metrics**: Cart operations, checkout success rate

### Logging
```python
import logging
import structlog

# Structured logging configuration
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## 🔒 Security Implementation

### Input Validation
```python
from pydantic import BaseModel, validator

class CartItemRequest(BaseModel):
    customer_id: str
    product_id: str
    product_name: str
    price: float
    quantity: int

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
```

### Database Security
- **Connection Pooling**: SQLAlchemy connection pooling
- **Parameterized Queries**: SQL injection prevention
- **Connection Encryption**: TLS encryption in transit
- **Credential Management**: AWS Secrets Manager integration

### API Security
- **CORS Configuration**: Controlled cross-origin requests
- **Rate Limiting**: Request throttling and limiting
- **Input Sanitization**: Pydantic model validation
- **Error Handling**: Secure error responses

## 🚀 Performance Optimization

### Database Optimization
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Indexed queries and joins
- **Lazy Loading**: On-demand data loading
- **Caching**: Redis integration (optional)

### Application Optimization
- **Async Operations**: FastAPI async/await support
- **Response Compression**: Gzip compression
- **Pagination**: Large dataset pagination
- **Background Tasks**: Celery integration (optional)

### Resource Management
- **Memory Limits**: 512Mi container limit
- **CPU Limits**: 500m CPU limit
- **Connection Limits**: Database connection pooling
- **Request Timeouts**: Configurable timeout values

## 🔧 Development Workflow

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/carthub"

# Run development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
python -m pytest tests/ -v --cov=app
```

### Docker Development
```bash
# Build container
docker build -t carthub-backend .

# Run container
docker run -p 8000:8000 -e DATABASE_URL="postgresql://..." carthub-backend

# Development with volume mounting
docker run -p 8000:8000 -v $(pwd):/app carthub-backend
```

### Database Development
```bash
# Run PostgreSQL locally
docker run -d --name postgres \
  -e POSTGRES_DB=carthub \
  -e POSTGRES_USER=carthub \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 postgres:15

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Add new table"
```

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
kubectl exec -it deployment/backend-deployment -- python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT version();')
    print(result.fetchone())
"
```

#### Performance Issues
```bash
# Check resource usage
kubectl top pods -l app=backend

# Check database performance
kubectl exec -it deployment/backend-deployment -- python -c "
from app.config.database import engine
print(engine.pool.status())
"
```

#### API Issues
```bash
# Check API health
curl http://backend-service:8000/health

# Check API documentation
curl http://backend-service:8000/docs
```

## 📈 Scaling Configuration

### Horizontal Scaling
- **HPA Metrics**: CPU and memory utilization
- **Custom Metrics**: Request rate and response time
- **Scale Up**: Aggressive scaling for traffic spikes
- **Scale Down**: Conservative scaling to maintain performance

### Database Scaling
- **Read Replicas**: Read-only database replicas
- **Connection Pooling**: Efficient connection management
- **Query Optimization**: Index optimization and query tuning
- **Caching Layer**: Redis for frequently accessed data

## 🔄 Deployment Strategies

### Rolling Update
- **Max Unavailable**: 25% of pods
- **Max Surge**: 25% additional pods
- **Health Checks**: Database connectivity validation
- **Rollback**: Automatic on health check failure

### Database Migration
- **Schema Versioning**: Alembic migration management
- **Backward Compatibility**: Non-breaking schema changes
- **Migration Testing**: Pre-deployment migration validation
- **Rollback Strategy**: Schema rollback procedures

## 📚 Dependencies

### Core Dependencies
```txt
fastapi==0.104.1          # Web framework
uvicorn[standard]==0.24.0 # ASGI server
sqlalchemy==2.0.23        # ORM
psycopg2-binary==2.9.9    # PostgreSQL adapter
pydantic==2.5.0           # Data validation
alembic==1.13.0           # Database migrations
```

### Development Dependencies
```txt
pytest==7.4.3             # Testing framework
pytest-asyncio==0.21.1    # Async testing
pytest-cov==4.1.0         # Coverage reporting
httpx==0.25.2             # HTTP client for testing
```

### Production Dependencies
```txt
boto3==1.34.0             # AWS SDK
python-dotenv==1.0.0      # Environment management
structlog==23.2.0         # Structured logging
```

## 🎯 Best Practices

### Code Organization
- **Clean Architecture**: Separation of concerns
- **Dependency Injection**: Testable code structure
- **Error Handling**: Comprehensive exception handling
- **Documentation**: OpenAPI automatic documentation

### Database Practices
- **Migration Management**: Version-controlled schema changes
- **Connection Pooling**: Efficient resource utilization
- **Query Optimization**: Performance-focused queries
- **Data Validation**: Model-level validation

### Security Practices
- **Input Validation**: Pydantic model validation
- **SQL Injection Prevention**: ORM usage
- **Secrets Management**: External secret storage
- **Error Sanitization**: Secure error responses

---

**Service Status**: ✅ Production Ready  
**Last Updated**: August 21, 2025  
**Version**: 2.0.0
