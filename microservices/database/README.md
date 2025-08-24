# Carthub Database Microservice

Database schema management and migration service for the Carthub shopping cart system.

## Architecture

This microservice is part of a complete CI/CD pipeline that includes:
- **Source Control**: AWS CodeCommit
- **CI/CD Pipeline**: AWS CodePipeline + CodeBuild
- **Container Registry**: Amazon ECR
- **Orchestration**: Amazon EKS (Kubernetes Jobs)
- **Database**: Amazon RDS PostgreSQL
- **Secrets Management**: AWS Secrets Manager

## Features

- Database schema creation and management
- Data migrations and seeding
- PostgreSQL-specific optimizations
- Kubernetes Job-based execution
- Integration with AWS Secrets Manager
- Comprehensive testing and validation
- Network policies for security

## Database Schema

The database includes the following tables:

### Core Tables
- **carts**: Customer shopping carts
  - `id` (SERIAL PRIMARY KEY)
  - `customer_id` (VARCHAR, UNIQUE)
  - `created_at`, `updated_at` (TIMESTAMP)

- **cart_items**: Items in shopping carts
  - `id` (SERIAL PRIMARY KEY)
  - `cart_id` (INTEGER, FK to carts)
  - `product_id`, `product_name` (VARCHAR)
  - `price` (DECIMAL), `quantity` (INTEGER)
  - `created_at`, `updated_at` (TIMESTAMP)

### Order Management
- **orders**: Completed orders
  - `id` (SERIAL PRIMARY KEY)
  - `customer_id` (VARCHAR)
  - `total_amount` (DECIMAL)
  - `status` (VARCHAR)
  - `created_at`, `updated_at` (TIMESTAMP)

- **order_items**: Items in completed orders
  - `id` (SERIAL PRIMARY KEY)
  - `order_id` (INTEGER, FK to orders)
  - `product_id`, `product_name` (VARCHAR)
  - `price` (DECIMAL), `quantity` (INTEGER)
  - `created_at` (TIMESTAMP)

### Indexes and Constraints
- Optimized indexes for common queries
- Foreign key constraints for data integrity
- Unique constraints to prevent duplicates
- Automatic timestamp updates with triggers

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/carthub"

# Run migrations
python migrate.py

# Run tests
python -m pytest tests/ -v
```

## Docker Build

```bash
# Build image
docker build -t carthub-database .

# Run migration container
docker run -e DATABASE_URL="postgresql://..." carthub-database
```

## Kubernetes Deployment

The database migrations are automatically executed via Kubernetes Jobs when code is pushed to the main branch.

### Manual Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/migration-job.yaml
kubectl apply -f k8s/network-policies.yaml
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `DB_USERNAME`: Database username (from Kubernetes secret)
- `DB_PASSWORD`: Database password (from Kubernetes secret)
- `DB_SECRET_ARN`: AWS Secrets Manager ARN (for CI/CD)

## Migration Process

The migration process includes:

1. **Connection Validation**: Test database connectivity
2. **Schema Creation**: Create tables, indexes, and constraints
3. **Data Seeding**: Insert initial data if needed
4. **Validation**: Verify schema integrity
5. **Cleanup**: Remove temporary resources

## CI/CD Pipeline

The pipeline includes the following stages:

1. **Source**: Triggered by commits to main branch
2. **Build**: 
   - Install dependencies
   - Run schema validation tests
   - Build Docker image
   - Push to ECR
3. **Deploy**:
   - Create database secrets in Kubernetes
   - Execute migration job in EKS
   - Apply network policies

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific migration
python -m pytest tests/test_schema.py -v

# Validate schema
python -c "
from migrate import get_database_url, create_engine
from sqlalchemy import text
engine = create_engine(get_database_url())
with engine.connect() as conn:
    result = conn.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\';'))
    print([row[0] for row in result])
"
```

## Security Features

- **Network Policies**: Restrict database access to backend pods only
- **Secrets Management**: Database credentials stored securely
- **Non-root Execution**: Migration jobs run as non-root user
- **Read-only Filesystem**: Container security hardening
- **Minimal Privileges**: Least privilege access patterns

## Monitoring

- **Job Status**: Kubernetes Job completion status
- **Migration Logs**: Detailed logging of migration steps
- **Database Health**: Connection and schema validation
- **Error Handling**: Comprehensive error reporting

## Network Policies

The microservice implements the following network policies:

- **backend-to-database**: Allows backend pods to access RDS
- **frontend-to-backend**: Allows frontend to backend communication
- **backend-ingress**: Controls ingress to backend pods
- **frontend-ingress**: Allows ALB traffic to frontend

## Database Connection

The service connects to Amazon RDS PostgreSQL:
- **High Availability**: Multi-AZ deployment
- **Automated Backups**: Point-in-time recovery
- **Encryption**: At rest and in transit
- **Monitoring**: CloudWatch integration
- **Scaling**: Read replicas support

## Troubleshooting

```bash
# Check migration job status
kubectl get jobs -n shopping-cart

# View migration logs
kubectl logs job/database-migration -n shopping-cart

# Check database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql $DATABASE_URL

# Verify schema
kubectl exec -it deployment/backend-deployment -n shopping-cart -- python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\';'))
    print('Tables:', [row[0] for row in result])
"

# Check network policies
kubectl get networkpolicies -n shopping-cart
```

## Schema Evolution

For schema changes:

1. Update the migration script in `migrate.py`
2. Add corresponding tests
3. Commit and push to trigger CI/CD
4. Monitor job execution in Kubernetes
5. Verify changes in the database

## Best Practices

- **Idempotent Migrations**: Safe to run multiple times
- **Backward Compatibility**: Maintain compatibility during updates
- **Testing**: Comprehensive test coverage for schema changes
- **Monitoring**: Track migration success and performance
- **Rollback Strategy**: Plan for schema rollbacks if needed
