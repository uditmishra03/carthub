#!/bin/bash

# CartHub Domain Setup Script
# This script helps you register a domain and deploy the application

set -e

echo "🌐 CartHub Domain Setup"
echo "======================"

# Configuration
DOMAIN_NAME=${1:-"carthub-demo.com"}
AWS_REGION="us-east-1"

echo "📋 Domain: $DOMAIN_NAME"
echo "🌍 Region: $AWS_REGION"
echo ""

# Function to check if domain is available
check_domain_availability() {
    echo "🔍 Checking domain availability..."
    
    AVAILABILITY=$(aws route53domains check-domain-availability \
        --domain-name "$DOMAIN_NAME" \
        --query 'Availability' \
        --output text 2>/dev/null || echo "ERROR")
    
    if [ "$AVAILABILITY" = "AVAILABLE" ]; then
        echo "✅ Domain $DOMAIN_NAME is available for registration!"
        return 0
    elif [ "$AVAILABILITY" = "UNAVAILABLE" ]; then
        echo "❌ Domain $DOMAIN_NAME is not available"
        return 1
    else
        echo "⚠️  Could not check domain availability. You may need to register it manually."
        return 2
    fi
}

# Function to register domain
register_domain() {
    echo ""
    echo "📝 Domain Registration"
    echo "====================="
    
    read -p "Do you want to register $DOMAIN_NAME? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 Starting domain registration..."
        echo "⚠️  Note: This will incur charges (typically $12-15/year for .com domains)"
        
        # Create registration command (user needs to fill in contact details)
        cat > register-domain.json << EOF
{
    "DomainName": "$DOMAIN_NAME",
    "DurationInYears": 1,
    "AutoRenew": true,
    "AdminContact": {
        "FirstName": "YOUR_FIRST_NAME",
        "LastName": "YOUR_LAST_NAME",
        "ContactType": "PERSON",
        "OrganizationName": "CartHub",
        "AddressLine1": "YOUR_ADDRESS",
        "City": "YOUR_CITY",
        "State": "YOUR_STATE",
        "CountryCode": "US",
        "ZipCode": "YOUR_ZIP",
        "PhoneNumber": "+1.YOUR_PHONE",
        "Email": "YOUR_EMAIL@example.com"
    },
    "RegistrantContact": {
        "FirstName": "YOUR_FIRST_NAME",
        "LastName": "YOUR_LAST_NAME",
        "ContactType": "PERSON",
        "OrganizationName": "CartHub",
        "AddressLine1": "YOUR_ADDRESS",
        "City": "YOUR_CITY",
        "State": "YOUR_STATE",
        "CountryCode": "US",
        "ZipCode": "YOUR_ZIP",
        "PhoneNumber": "+1.YOUR_PHONE",
        "Email": "YOUR_EMAIL@example.com"
    },
    "TechContact": {
        "FirstName": "YOUR_FIRST_NAME",
        "LastName": "YOUR_LAST_NAME",
        "ContactType": "PERSON",
        "OrganizationName": "CartHub",
        "AddressLine1": "YOUR_ADDRESS",
        "City": "YOUR_CITY",
        "State": "YOUR_STATE",
        "CountryCode": "US",
        "ZipCode": "YOUR_ZIP",
        "PhoneNumber": "+1.YOUR_PHONE",
        "Email": "YOUR_EMAIL@example.com"
    },
    "PrivacyProtectAdminContact": true,
    "PrivacyProtectRegistrantContact": true,
    "PrivacyProtectTechContact": true
}
EOF
        
        echo "📝 Created register-domain.json template"
        echo "✏️  Please edit register-domain.json with your contact information"
        echo "🚀 Then run: aws route53domains register-domain --cli-input-json file://register-domain.json"
        echo ""
        echo "⏳ Domain registration typically takes 15-30 minutes"
        
    else
        echo "⏭️  Skipping domain registration"
    fi
}

# Function to deploy infrastructure
deploy_infrastructure() {
    echo ""
    echo "🏗️  Infrastructure Deployment"
    echo "============================"
    
    echo "📦 Installing CDK dependencies..."
    cd infrastructure_cdk
    pip install -r requirements.txt
    
    echo "🔧 Bootstrapping CDK..."
    cdk bootstrap --app "python app_domain.py" \
        --context domain_name="$DOMAIN_NAME"
    
    echo "🚀 Deploying domain infrastructure..."
    cdk deploy CartHubDomainStack \
        --app "python app_domain.py" \
        --context domain_name="$DOMAIN_NAME" \
        --require-approval never
    
    echo "✅ Infrastructure deployed successfully!"
    
    # Get outputs
    echo ""
    echo "📋 Deployment Information"
    echo "========================"
    
    WEBSITE_URL=$(aws cloudformation describe-stacks \
        --stack-name CartHubDomainStack \
        --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
        --output text)
    
    NAME_SERVERS=$(aws cloudformation describe-stacks \
        --stack-name CartHubDomainStack \
        --query 'Stacks[0].Outputs[?OutputKey==`NameServers`].OutputValue' \
        --output text)
    
    echo "🌐 Website URL: $WEBSITE_URL"
    echo "🔗 Name Servers: $NAME_SERVERS"
    
    cd ..
}

# Function to update domain nameservers
update_nameservers() {
    echo ""
    echo "🔧 Domain Configuration"
    echo "======================"
    
    echo "📋 Getting Route 53 name servers..."
    
    NAME_SERVERS=$(aws cloudformation describe-stacks \
        --stack-name CartHubDomainStack \
        --query 'Stacks[0].Outputs[?OutputKey==`NameServers`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$NAME_SERVERS" ]; then
        echo "🔗 Route 53 Name Servers:"
        echo "$NAME_SERVERS" | tr ',' '\n' | sed 's/^/   /'
        echo ""
        
        read -p "Update domain nameservers automatically? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔄 Updating domain nameservers..."
            
            # Convert comma-separated to JSON array
            NS_JSON=$(echo "$NAME_SERVERS" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/' | sed 's/^/[/' | sed 's/$/]/')
            
            aws route53domains update-domain-nameservers \
                --domain-name "$DOMAIN_NAME" \
                --nameservers "$NS_JSON" || {
                echo "⚠️  Could not update nameservers automatically"
                echo "📝 Please update them manually in your domain registrar"
            }
        else
            echo "📝 Please update your domain nameservers manually:"
            echo "$NAME_SERVERS" | tr ',' '\n' | sed 's/^/   /'
        fi
    else
        echo "⚠️  Could not retrieve nameservers. Check CloudFormation stack outputs."
    fi
}

# Function to test deployment
test_deployment() {
    echo ""
    echo "🧪 Testing Deployment"
    echo "===================="
    
    WEBSITE_URL=$(aws cloudformation describe-stacks \
        --stack-name CartHubDomainStack \
        --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$WEBSITE_URL" ]; then
        echo "🔍 Testing website accessibility..."
        
        if curl -s -o /dev/null -w "%{http_code}" "$WEBSITE_URL" | grep -q "200\|301\|302"; then
            echo "✅ Website is accessible at: $WEBSITE_URL"
        else
            echo "⚠️  Website may not be ready yet. DNS propagation can take up to 48 hours."
            echo "🔗 URL: $WEBSITE_URL"
        fi
    else
        echo "⚠️  Could not retrieve website URL"
    fi
}

# Main execution
main() {
    echo "🚀 Starting CartHub domain setup for: $DOMAIN_NAME"
    echo ""
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Please install it first."
        exit 1
    fi
    
    # Check CDK
    if ! command -v cdk &> /dev/null; then
        echo "📦 Installing AWS CDK..."
        npm install -g aws-cdk
    fi
    
    # Step 1: Check domain availability
    check_domain_availability
    DOMAIN_STATUS=$?
    
    # Step 2: Register domain if available
    if [ $DOMAIN_STATUS -eq 0 ]; then
        register_domain
    fi
    
    # Step 3: Deploy infrastructure
    deploy_infrastructure
    
    # Step 4: Update nameservers
    update_nameservers
    
    # Step 5: Test deployment
    test_deployment
    
    echo ""
    echo "🎉 CartHub domain setup complete!"
    echo "================================="
    echo ""
    echo "📋 Next Steps:"
    echo "1. Wait for DNS propagation (up to 48 hours)"
    echo "2. Test your application at: https://app.$DOMAIN_NAME"
    echo "3. Set up monitoring and backups"
    echo "4. Configure custom email (optional)"
    echo ""
    echo "🔗 Useful Commands:"
    echo "   aws route53 list-hosted-zones"
    echo "   aws cloudfront list-distributions"
    echo "   aws s3 ls | grep carthub"
    echo ""
}

# Run main function
main "$@"
