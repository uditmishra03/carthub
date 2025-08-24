#!/bin/bash

# Quick deployment script for carthub.shop

set -e

DOMAIN_NAME="carthub.shop"
STACK_NAME="CartHubShopStack"

echo "🛍️  Deploying CartHub to carthub.shop"
echo "====================================="
echo ""

# Check if we have AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured"
    echo "Please run: aws configure"
    exit 1
fi

echo "✅ AWS credentials verified"

# Check if domain exists in Route 53
echo "🔍 Checking Route 53 configuration..."
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name \
    --dns-name "$DOMAIN_NAME" \
    --query "HostedZones[?Name=='${DOMAIN_NAME}.'].Id" \
    --output text 2>/dev/null | cut -d'/' -f3)

if [ -n "$HOSTED_ZONE_ID" ]; then
    echo "✅ Found hosted zone: $HOSTED_ZONE_ID"
else
    echo "⚠️  No hosted zone found for $DOMAIN_NAME"
    echo "💡 The setup will create one automatically"
fi

# Navigate to CDK directory
cd infrastructure_cdk

echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "🔧 Bootstrapping CDK..."
cdk bootstrap --app "python app_domain.py" \
    --context domain_name="$DOMAIN_NAME" > /dev/null 2>&1 || true

echo "🏗️  Deploying CartHub infrastructure..."
echo "This may take 5-10 minutes for SSL certificate validation..."

cdk deploy CartHubDomainStack \
    --app "python app_domain.py" \
    --context domain_name="$DOMAIN_NAME" \
    --require-approval never

echo ""
echo "🎉 Deployment Complete!"
echo "======================"

# Get outputs
WEBSITE_URL=$(aws cloudformation describe-stacks \
    --stack-name CartHubDomainStack \
    --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
    --output text 2>/dev/null || echo "Not available")

CLOUDFRONT_ID=$(aws cloudformation describe-stacks \
    --stack-name CartHubDomainStack \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
    --output text 2>/dev/null || echo "Not available")

NAME_SERVERS=$(aws cloudformation describe-stacks \
    --stack-name CartHubDomainStack \
    --query 'Stacks[0].Outputs[?OutputKey==`NameServers`].OutputValue' \
    --output text 2>/dev/null || echo "Not available")

echo ""
echo "🛍️  CartHub.shop Deployment Information"
echo "======================================"
echo "🌐 Main URL: https://carthub.shop"
echo "🛒 App URL: https://app.carthub.shop"
echo "📡 CloudFront: $CLOUDFRONT_ID"
echo ""

if [ "$NAME_SERVERS" != "Not available" ]; then
    echo "🔗 Name Servers (update at your registrar):"
    echo "$NAME_SERVERS" | tr ',' '\n' | sed 's/^/   /'
    echo ""
    echo "📋 Next Steps:"
    echo "1. Update carthub.shop nameservers at your domain registrar"
    echo "2. Wait 24-48 hours for DNS propagation"
    echo "3. Visit https://app.carthub.shop to see your cart!"
    echo ""
    echo "🔧 Management Commands:"
    echo "   # Update content:"
    echo "   aws s3 sync frontend/public/ s3://carthub-carthub-shop/"
    echo ""
    echo "   # Clear CDN cache:"
    echo "   aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths '/*'"
    echo ""
    echo "   # Check DNS:"
    echo "   dig app.carthub.shop"
fi

cd ..

echo ""
echo "🎯 CartHub is now deployed to carthub.shop!"
echo "Visit https://app.carthub.shop once DNS propagates."
