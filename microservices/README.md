# Carthub Microservices

This directory contains the separated microservices for the Carthub application, ready for deployment to individual CodeCommit repositories.

## Structure

- `frontend/` - React frontend application
- `backend/` - FastAPI backend service
- `database/` - Database migrations and schema management

Each microservice directory contains:
- Application code
- Dockerfile
- buildspec.yml for CodeBuild
- Kubernetes manifests in `k8s/` directory
- README.md with service-specific documentation

## Deployment

Each microservice will be deployed to its own CodeCommit repository and have its own CI/CD pipeline.

## Getting Started

1. Deploy the infrastructure using CDK
2. Push each microservice to its respective CodeCommit repository
3. The CI/CD pipelines will automatically build, test, and deploy to EKS
