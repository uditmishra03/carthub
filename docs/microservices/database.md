# Database Microservice Documentation

The database microservice handles schema management, migrations, and database operations for the Carthub shopping cart system.

## 🏗️ Architecture

### Technology Stack
- **Database**: PostgreSQL 15 (Amazon RDS)
- **Migration Tool**: Alembic for schema versioning
- **Language**: Python 3.12 with SQLAlchemy
- **Container**: Python slim with PostgreSQL client tools
- **Orchestration**: Kubernetes Jobs for migration execution

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CI/CD         │───▶│  Migration Job  │───▶│  PostgreSQL     │
│   Pipeline      │    │  (K8s Job)      │    │  Database       │
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
database/
├── migrations/                 # Alembic migration files
│   ├── versions/              # Migration version files
│   ├── alembic.ini           # Alembic configuration
│   └── env.py                # Migration environment
├── k8s/                       # Kubernetes manifests
│   ├── migration-job.yaml    # Migration job configuration
│   ├── network-policies.yaml # Security policies
│   └── namespace.yaml        # Kubernetes namespace
├── tests/                     # Test suite
│   └── test_schema.py        # Schema validation tests
├── scripts/                   # Utility scripts
│   └── backup.sh             # Database backup script
├── Dockerfile                 # Container configuration
├── buildspec.yml             # CodeBuild CI/CD pipeline
├── migrate.py                # Migration execution script
├── requirements.txt          # Python dependencies
└── README.md                 # Service documentation
```

## 🐳 Docker Configuration

### Migration Container
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc libpq-dev postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy migration scripts and schema
COPY . .

# Create non-root user
RUN groupadd -r dbuser && useradd -r -g dbuser dbuser
RUN chown -R dbuser:dbuser /app
USER dbuser

# Default command runs migrations
CMD ["python", "migrate.py"]
```

## 🗄️ Database Schema

### Core Tables

#### Shopping Cart Tables
```sql
-- Customer shopping carts
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Items in shopping carts
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

#### Order Management Tables
```sql
-- Completed orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    shipping_address JSONB,
    payment_method VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Items in completed orders
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

#### Performance Indexes
```sql
-- Cart operations
CREATE INDEX idx_carts_customer_id ON carts(customer_id);
CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);

-- Order operations
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
```

#### Data Integrity Constraints
```sql
-- Price validation
ALTER TABLE cart_items ADD CONSTRAINT check_positive_price 
    CHECK (price > 0);
ALTER TABLE cart_items ADD CONSTRAINT check_positive_quantity 
    CHECK (quantity > 0);

-- Order validation
ALTER TABLE orders ADD CONSTRAINT check_positive_total 
    CHECK (total_amount > 0);
ALTER TABLE orders ADD CONSTRAINT check_valid_status 
    CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'));
```

### Triggers and Functions

#### Automatic Timestamp Updates
```sql
-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables
CREATE TRIGGER update_carts_updated_at 
    BEFORE UPDATE ON carts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cart_items_updated_at 
    BEFORE UPDATE ON cart_items 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## 🔧 Migration Management

### Migration Script (`migrate.py`)
```python
#!/usr/bin/env python3
"""
Database migration script for Carthub
Handles schema creation and data migrations
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
import boto3
import json

def get_database_url():
    """Get database URL from environment or AWS Secrets Manager"""
    # Try environment variables first
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    
    # Get from AWS Secrets Manager
    secret_arn = os.getenv('DB_SECRET_ARN')
    if not secret_arn:
        raise ValueError("DATABASE_URL or DB_SECRET_ARN must be set")
    
    try:
        secrets_client = boto3.client('secretsmanager')
        response = secrets_client.get_secret_value(SecretId=secret_arn)
        secret = json.loads(response['SecretString'])
        
        username = secret['username']
        password = secret['password']
        host = secret.get('host', 'localhost')
        port = secret.get('port', 5432)
        database = secret.get('dbname', 'carthub')
        
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    except Exception as e:
        logger.error(f"Failed to get database credentials: {e}")
        raise

def create_tables(engine):
    """Create database tables"""
    logger.info("Creating database tables...")
    
    # Execute schema creation SQL
    with engine.connect() as conn:
        # Create tables, indexes, triggers
        conn.execute(text(schema_sql))
        conn.commit()
    
    logger.info("Database tables created successfully")

def main():
    """Main migration function"""
    try:
        logger.info("Starting database migration...")
        
        # Get database URL and create engine
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"Connected to PostgreSQL: {version}")
        
        # Create tables and run migrations
        create_tables(engine)
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Alembic Configuration
```python
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# Import your models
from app.models import Base

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

## ☸️ Kubernetes Configuration

### Migration Job
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: database-migration
  namespace: shopping-cart
  labels:
    app: database-migration
spec:
  template:
    metadata:
      labels:
        app: database-migration
    spec:
      restartPolicy: OnFailure
      containers:
      - name: migration
        image: IMAGE_URI_PLACEHOLDER
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-migration-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-migration-secret
              key: password
        - name: DATABASE_URL
          value: "postgresql://$(DB_USERNAME):$(DB_PASSWORD)@carthub-database:5432/carthub"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir: {}
  backoffLimit: 3
```

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-to-database
  namespace: shopping-cart
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Egress
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 5432    # PostgreSQL
    - protocol: TCP
      port: 443     # AWS services
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: migration-to-database
  namespace: shopping-cart
spec:
  podSelector:
    matchLabels:
      app: database-migration
  policyTypes:
  - Egress
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 5432    # PostgreSQL
    - protocol: TCP
      port: 443     # AWS services
```

## 🔄 CI/CD Pipeline

### Build Stages
1. **Pre-build**: AWS authentication, dependency installation
2. **Build**: Schema validation, Docker image creation
3. **Post-build**: ECR push, Kubernetes job execution

### Pipeline Features
- **Schema Validation**: Test migrations against test database
- **Rollback Testing**: Validate migration rollback procedures
- **Security Scanning**: ECR vulnerability scanning
- **Job Monitoring**: Kubernetes job completion tracking

### Build Specification
```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
      - IMAGE_TAG=${COMMIT_HASH:=latest}
      - echo Installing dependencies...
      - pip install -r requirements.txt
  build:
    commands:
      - echo Running database schema validation...
      - python -m pytest tests/ -v
      - echo Building the Docker image...
      - docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $REPOSITORY_URI:$IMAGE_TAG
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $REPOSITORY_URI:latest
  post_build:
    commands:
      - echo Pushing the Docker images...
      - docker push $REPOSITORY_URI:$IMAGE_TAG
      - docker push $REPOSITORY_URI:latest
      - echo Installing kubectl...
      - curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.28.3/2023-11-14/bin/linux/amd64/kubectl
      - chmod +x ./kubectl
      - mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
      - echo Configuring kubectl...
      - aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $EKS_CLUSTER_NAME
      - echo Running database migrations...
      - DB_SECRET=$(aws secretsmanager get-secret-value --secret-id $DB_SECRET_ARN --query SecretString --output text)
      - DB_USERNAME=$(echo $DB_SECRET | jq -r .username)
      - DB_PASSWORD=$(echo $DB_SECRET | jq -r .password)
      - kubectl create secret generic db-migration-secret --from-literal=username=$DB_USERNAME --from-literal=password=$DB_PASSWORD -n shopping-cart --dry-run=client -o yaml | kubectl apply -f -
      - echo Updating Kubernetes job...
      - sed -i 's|IMAGE_URI_PLACEHOLDER|'$REPOSITORY_URI:$IMAGE_TAG'|g' k8s/migration-job.yaml
      - kubectl apply -f k8s/namespace.yaml
      - kubectl apply -f k8s/migration-job.yaml
      - kubectl apply -f k8s/network-policies.yaml
      - echo Database migration completed successfully
```

## 🧪 Testing Strategy

### Test Categories
- **Schema Tests**: Database schema validation
- **Migration Tests**: Migration up/down testing
- **Data Integrity Tests**: Constraint and trigger testing
- **Performance Tests**: Query performance validation

### Test Implementation
```python
import pytest
from unittest.mock import Mock, patch
import os
import sys

class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_get_database_url_from_env(self):
        """Test getting database URL from environment variable"""
        test_url = "postgresql://test:test@localhost:5432/test"
        
        with patch.dict(os.environ, {'DATABASE_URL': test_url}):
            url = get_database_url()
            assert url == test_url

    @patch('boto3.client')
    def test_get_database_url_from_secrets_manager(self, mock_boto_client):
        """Test getting database URL from AWS Secrets Manager"""
        mock_secrets_client = Mock()
        mock_boto_client.return_value = mock_secrets_client
        
        mock_secret_value = {
            'SecretString': '{"username": "testuser", "password": "testpass", "host": "testhost", "port": 5432, "dbname": "testdb"}'
        }
        mock_secrets_client.get_secret_value.return_value = mock_secret_value
        
        with patch.dict(os.environ, {'DB_SECRET_ARN': 'arn:aws:secretsmanager:us-west-2:123456789012:secret:test'}, clear=True):
            url = get_database_url()
            expected_url = "postgresql://testuser:testpass@testhost:5432/testdb"
            assert url == expected_url

class TestSchemaCreation:
    """Test database schema creation"""
    
    @patch('migrate.create_engine')
    def test_create_tables_success(self, mock_create_engine):
        """Test successful table creation"""
        mock_engine = Mock()
        mock_connection = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        mock_connection.execute.return_value = None
        mock_connection.commit.return_value = None
        
        create_tables(mock_engine)
        
        assert mock_connection.execute.call_count > 0
        mock_connection.commit.assert_called_once()
```

## 📊 Monitoring and Observability

### Job Monitoring
- **Job Status**: Kubernetes Job completion status
- **Migration Logs**: Detailed logging of migration steps
- **Database Health**: Connection and schema validation
- **Error Handling**: Comprehensive error reporting

### Metrics Collection
```python
import time
import logging
from contextlib import contextmanager

@contextmanager
def migration_timer(operation_name):
    """Context manager for timing migration operations"""
    start_time = time.time()
    logger.info(f"Starting {operation_name}")
    try:
        yield
        duration = time.time() - start_time
        logger.info(f"Completed {operation_name} in {duration:.2f} seconds")
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed {operation_name} after {duration:.2f} seconds: {e}")
        raise

# Usage in migration script
with migration_timer("table_creation"):
    create_tables(engine)
```

### Health Validation
```python
def validate_schema(engine):
    """Validate database schema after migration"""
    with engine.connect() as conn:
        # Check table existence
        tables = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)).fetchall()
        
        expected_tables = ['carts', 'cart_items', 'orders', 'order_items']
        existing_tables = [row[0] for row in tables]
        
        for table in expected_tables:
            if table not in existing_tables:
                raise ValueError(f"Table {table} not found")
        
        logger.info(f"Schema validation passed. Found tables: {existing_tables}")
```

## 🔒 Security Implementation

### Container Security
- **Non-root User**: Migration jobs run as non-root
- **Read-only Filesystem**: Immutable container filesystem
- **Minimal Privileges**: Dropped capabilities
- **Security Scanning**: ECR vulnerability scanning

### Database Security
- **Connection Encryption**: TLS encryption in transit
- **Credential Management**: AWS Secrets Manager integration
- **Network Isolation**: Kubernetes network policies
- **Audit Logging**: Database operation logging

### Access Control
```yaml
# RBAC for migration job
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: shopping-cart
  name: migration-role
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
- apiGroups: ["batch"]
  resources: ["jobs"]
  verbs: ["get", "list", "create"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: migration-rolebinding
  namespace: shopping-cart
subjects:
- kind: ServiceAccount
  name: migration-service-account
  namespace: shopping-cart
roleRef:
  kind: Role
  name: migration-role
  apiGroup: rbac.authorization.k8s.io
```

## 🚀 Performance Optimization

### Migration Performance
- **Batch Operations**: Bulk data operations
- **Index Creation**: Concurrent index creation
- **Connection Pooling**: Efficient connection management
- **Parallel Execution**: Parallel migration steps

### Query Optimization
```sql
-- Optimized queries for common operations
EXPLAIN ANALYZE SELECT c.customer_id, COUNT(ci.id) as item_count, SUM(ci.price * ci.quantity) as total
FROM carts c
LEFT JOIN cart_items ci ON c.id = ci.cart_id
WHERE c.customer_id = $1
GROUP BY c.customer_id;

-- Index usage validation
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename IN ('carts', 'cart_items', 'orders', 'order_items');
```

### Resource Management
- **Memory Limits**: 256Mi container limit
- **CPU Limits**: 200m CPU limit
- **Connection Limits**: Database connection pooling
- **Timeout Configuration**: Migration timeout settings

## 🔧 Development Workflow

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/carthub"

# Run migrations
python migrate.py

# Run tests
python -m pytest tests/ -v

# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migration
alembic upgrade head
```

### Docker Development
```bash
# Build container
docker build -t carthub-database .

# Run migration container
docker run -e DATABASE_URL="postgresql://..." carthub-database

# Interactive development
docker run -it -v $(pwd):/app carthub-database bash
```

### Testing Migrations
```bash
# Test migration up
alembic upgrade head

# Test migration down
alembic downgrade -1

# Test migration idempotency
alembic upgrade head
alembic upgrade head  # Should be no-op
```

## 🐛 Troubleshooting

### Common Issues

#### Migration Failures
```bash
# Check migration job status
kubectl get jobs -n shopping-cart

# View migration logs
kubectl logs job/database-migration -n shopping-cart

# Check database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql $DATABASE_URL
```

#### Schema Issues
```bash
# Verify schema
kubectl exec -it deployment/backend-deployment -n shopping-cart -- python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\';'))
    print('Tables:', [row[0] for row in result])
"
```

#### Performance Issues
```bash
# Check database performance
kubectl exec -it deployment/backend-deployment -n shopping-cart -- python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text('SELECT * FROM pg_stat_activity WHERE state = \\'active\\';'))
    print('Active connections:', len(result.fetchall()))
"
```

## 📈 Backup and Recovery

### Backup Strategy
```bash
#!/bin/bash
# backup.sh - Database backup script

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="carthub_backup_${TIMESTAMP}.sql"

# Create backup
pg_dump $DATABASE_URL > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3 (optional)
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://carthub-backups/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "carthub_backup_*.sql.gz" -mtime +7 -delete
```

### Recovery Procedures
```bash
# Restore from backup
pg_restore -d $DATABASE_URL backup_file.sql

# Point-in-time recovery (RDS)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier carthub-db \
  --target-db-instance-identifier carthub-db-restored \
  --restore-time 2025-08-21T18:00:00Z
```

## 🎯 Best Practices

### Migration Best Practices
- **Backward Compatibility**: Non-breaking schema changes
- **Idempotent Operations**: Safe to run multiple times
- **Testing**: Comprehensive migration testing
- **Rollback Strategy**: Plan for schema rollbacks
- **Documentation**: Document all schema changes

### Security Best Practices
- **Least Privilege**: Minimal database permissions
- **Encryption**: Data encryption at rest and in transit
- **Audit Logging**: Track all database changes
- **Secret Rotation**: Regular credential rotation
- **Network Isolation**: Database network segmentation

### Performance Best Practices
- **Index Strategy**: Optimize for query patterns
- **Connection Pooling**: Efficient connection management
- **Query Optimization**: Regular query performance review
- **Monitoring**: Continuous performance monitoring
- **Capacity Planning**: Proactive scaling decisions

---

**Service Status**: ✅ Production Ready  
**Last Updated**: August 21, 2025  
**Version**: 2.0.0
