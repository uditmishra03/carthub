# Carthub Frontend Microservice

React-based frontend application for the Carthub shopping cart system.

## Architecture

This microservice is part of a complete CI/CD pipeline that includes:
- **Source Control**: AWS CodeCommit
- **CI/CD Pipeline**: AWS CodePipeline + CodeBuild
- **Container Registry**: Amazon ECR
- **Orchestration**: Amazon EKS
- **Load Balancing**: AWS Application Load Balancer

## Features

- React 18 with modern hooks
- Responsive design with Tailwind CSS
- API integration with backend service
- Docker containerization with nginx
- Kubernetes deployment with auto-scaling
- Health checks and monitoring

## Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Docker Build

```bash
# Build image
docker build -t carthub-frontend .

# Run container
docker run -p 80:80 carthub-frontend
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
kubectl apply -f k8s/ingress.yaml
```

## Environment Variables

- `REACT_APP_API_URL`: Backend API URL (automatically configured in Kubernetes)
- `NODE_ENV`: Environment (development/production)

## CI/CD Pipeline

The pipeline includes the following stages:

1. **Source**: Triggered by commits to main branch
2. **Build**: 
   - Install dependencies
   - Build React application
   - Create Docker image
   - Push to ECR
3. **Deploy**:
   - Update Kubernetes deployment
   - Apply manifests to EKS cluster

## Monitoring

- Health check endpoint: `/health`
- Kubernetes readiness and liveness probes
- Horizontal Pod Autoscaler based on CPU/memory
- Application Load Balancer health checks

## Security

- Non-root container user
- Read-only root filesystem
- Security contexts and capabilities dropped
- Network policies for pod-to-pod communication
- HTTPS termination at load balancer

## Scaling

- **Horizontal Pod Autoscaler**: 2-10 replicas based on CPU/memory
- **Cluster Autoscaler**: Automatic node scaling
- **Pod Anti-Affinity**: Distribute pods across nodes

## Troubleshooting

```bash
# Check pod status
kubectl get pods -n shopping-cart

# View logs
kubectl logs -f deployment/frontend-deployment -n shopping-cart

# Check ingress
kubectl get ingress -n shopping-cart

# Describe deployment
kubectl describe deployment frontend-deployment -n shopping-cart
```
