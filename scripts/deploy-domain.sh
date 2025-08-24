#!/bin/bash

# Quick Domain Deployment Script
# Deploys CartHub to a custom domain

set -e

DOMAIN_NAME=${1:-"carthub-demo.com"}
STACK_NAME="CartHubDomainStack"

echo "🚀 Deploying CartHub to domain: $DOMAIN_NAME"
echo "============================================="

# Check if domain exists in Route 53
echo "🔍 Checking if domain exists in Route 53..."
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name \
    --dns-name "$DOMAIN_NAME" \
    --query "HostedZones[?Name=='${DOMAIN_NAME}.'].Id" \
    --output text 2>/dev/null | cut -d'/' -f3)

if [ -n "$HOSTED_ZONE_ID" ]; then
    echo "✅ Found existing hosted zone: $HOSTED_ZONE_ID"
else
    echo "⚠️  No hosted zone found for $DOMAIN_NAME"
    echo "📝 You may need to register the domain first"
fi

# Navigate to CDK directory
cd infrastructure_cdk

echo "📦 Installing CDK dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "🔧 Bootstrapping CDK (if needed)..."
cdk bootstrap --app "python app_domain.py" \
    --context domain_name="$DOMAIN_NAME" > /dev/null 2>&1 || true

echo "🏗️  Deploying infrastructure..."
cdk deploy $STACK_NAME \
    --app "python app_domain.py" \
    --context domain_name="$DOMAIN_NAME" \
    --require-approval never

echo ""
echo "✅ Deployment Complete!"
echo "======================"

# Get deployment outputs
echo "📋 Getting deployment information..."

WEBSITE_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
    --output text 2>/dev/null || echo "Not available")

CLOUDFRONT_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
    --output text 2>/dev/null || echo "Not available")

NAME_SERVERS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`NameServers`].OutputValue' \
    --output text 2>/dev/null || echo "Not available")

echo ""
echo "🎉 CartHub Deployment Information"
echo "================================="
echo "🌐 Website URL: $WEBSITE_URL"
echo "📡 CloudFront ID: $CLOUDFRONT_ID"
echo "🔗 Name Servers: $NAME_SERVERS"
echo ""

if [ "$NAME_SERVERS" != "Not available" ]; then
    echo "📝 Next Steps:"
    echo "1. Update your domain nameservers to:"
    echo "$NAME_SERVERS" | tr ',' '\n' | sed 's/^/   /'
    echo ""
    echo "2. Wait for DNS propagation (up to 48 hours)"
    echo "3. Test your site at: $WEBSITE_URL"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   # Test DNS: dig app.$DOMAIN_NAME"
    echo "   # Check SSL: curl -I $WEBSITE_URL"
    echo "   # Update content: aws s3 sync frontend/public/ s3://carthub-${DOMAIN_NAME//./-}/"
fi

cd ..

echo ""
echo "🎯 Deployment completed successfully!"
