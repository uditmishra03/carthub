#!/usr/bin/env python3
"""
CartHub Domain Application
Main CDK app for domain infrastructure deployment
"""

import aws_cdk as cdk
from domain_stack import CartHubDomainStack

# Configuration
DOMAIN_NAME = "carthub-demo.com"  # Change this to your desired domain
AWS_REGION = "us-east-1"  # CloudFront requires certificates in us-east-1
AWS_ACCOUNT = "013443956821"  # Your AWS account ID

app = cdk.App()

# Get domain name from context or use default
domain_name = app.node.try_get_context("domain_name") or DOMAIN_NAME

# Create the domain stack
domain_stack = CartHubDomainStack(
    app, 
    "CartHubDomainStack",
    domain_name=domain_name,
    env=cdk.Environment(
        account=AWS_ACCOUNT,
        region=AWS_REGION
    ),
    description=f"CartHub domain infrastructure for {domain_name}"
)

# Add tags
cdk.Tags.of(domain_stack).add("Project", "CartHub")
cdk.Tags.of(domain_stack).add("Environment", "Production")
cdk.Tags.of(domain_stack).add("Domain", domain_name)

app.synth()
