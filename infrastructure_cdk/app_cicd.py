#!/usr/bin/env python3
"""
AWS CDK App for Carthub Microservices CI/CD
Deploys only the CI/CD pipeline infrastructure
"""

import os
from aws_cdk import App, Environment
from microservices_cicd_stack import MicroservicesCicdStack

app = App()

# Get environment
env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'us-west-2')
)

# Microservices CI/CD stack
cicd_stack = MicroservicesCicdStack(
    app, "CarthubMicroservicesCicd",
    env=env,
    description="Complete CI/CD pipeline with CodeCommit, CodePipeline, ECR, and EKS for microservices"
)

app.synth()
