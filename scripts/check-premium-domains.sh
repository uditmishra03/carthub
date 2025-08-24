#!/bin/bash

# Check availability of premium CartHub domains

echo "🛒 CartHub Premium Domain Availability Check"
echo "==========================================="
echo ""

DOMAINS=("carthub.shop" "carthub.in" "carthub.dev")

for domain in "${DOMAINS[@]}"; do
    echo "🔍 Checking: $domain"
    
    # Check domain availability
    AVAILABILITY=$(aws route53domains check-domain-availability \
        --domain-name "$domain" \
        --query 'Availability' \
        --output text 2>/dev/null)
    
    if [ "$AVAILABILITY" = "AVAILABLE" ]; then
        echo "   ✅ AVAILABLE - Ready to register!"
        
        # Get pricing info
        PRICE=$(aws route53domains list-prices \
            --tld "${domain##*.}" \
            --query 'Prices[0].RegistrationPrice.Price' \
            --output text 2>/dev/null || echo "N/A")
        
        if [ "$PRICE" != "N/A" ]; then
            echo "   💰 Price: \$${PRICE}/year"
        fi
        
    elif [ "$AVAILABILITY" = "UNAVAILABLE" ]; then
        echo "   ❌ UNAVAILABLE - Already registered"
        
        # Check if we own it
        HOSTED_ZONE=$(aws route53 list-hosted-zones-by-name \
            --dns-name "$domain" \
            --query "HostedZones[?Name=='${domain}.'].Id" \
            --output text 2>/dev/null)
        
        if [ -n "$HOSTED_ZONE" ]; then
            echo "   ℹ️  Found in your Route 53 - You may already own this!"
        fi
        
    elif [ "$AVAILABILITY" = "DONT_KNOW" ]; then
        echo "   ⚠️  Status unknown - May require special registration"
    else
        echo "   ⚠️  Could not check availability (check AWS permissions)"
    fi
    
    echo ""
done

echo "📋 Domain Recommendations:"
echo "========================="
echo ""
echo "🏆 BEST CHOICE: carthub.shop"
echo "   • Perfect for e-commerce branding"
echo "   • SEO benefits for shopping sites"
echo "   • Premium domain recognition"
echo "   • Cost: ~\$30-40/year"
echo ""
echo "🥈 GREAT CHOICE: carthub.in"
echo "   • Global appeal, popular in India"
echo "   • Cost-effective option"
echo "   • Short and memorable"
echo "   • Cost: ~\$15-25/year"
echo ""
echo "🥉 GOOD CHOICE: carthub.dev"
echo "   • Perfect for developer audience"
echo "   • Modern and trendy"
echo "   • HTTPS required (we have this)"
echo "   • Cost: ~\$12-20/year"
echo ""
echo "🚀 To register and deploy:"
echo "   ./scripts/setup-domain.sh carthub.shop"
echo "   ./scripts/setup-domain.sh carthub.in"
echo "   ./scripts/setup-domain.sh carthub.dev"
