# Version: 2.1.0
#!/usr/bin/env python3
import aws_cdk as cdk
from shopping_cart_stack import ShoppingCartStack
from microservices_stack import MicroservicesStack
from eks_stack import EKSMicroservicesStack
from microservices_cicd_stack import MicroservicesCicdStack

app = cdk.App()

# Get environment configuration
env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-west-2"
)

# Original serverless stack (can be kept for comparison)
serverless_stack = ShoppingCartStack(
    app, "ShoppingCartServerlessStack",
    env=env,
    description="Original serverless shopping cart API"
)

# ECS-based microservices stack with 3-tier VPC architecture
microservices_stack = MicroservicesStack(
    app, "ShoppingCartMicroservicesStack",
    env=env,
    description="3-tier microservices shopping cart architecture with ECS"
)

# EKS-based microservices stack for Kubernetes deployment
eks_stack = EKSMicroservicesStack(
    app, "ShoppingCartEKSStack",
    env=env,
    description="EKS-based microservices shopping cart architecture with Kubernetes"
)

# NEW: Complete CI/CD pipeline with CodeCommit, CodePipeline, ECR, and EKS
cicd_stack = MicroservicesCicdStack(
    app, "CarthubMicroservicesCicd",
    env=env,
    description="Complete CI/CD pipeline with CodeCommit, CodePipeline, ECR, and EKS for microservices"
)

app.synth()
