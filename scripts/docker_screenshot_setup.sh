#!/bin/bash

# Docker-based screenshot setup for microservices architecture
# Addresses product image loading issues in containerized environment

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Docker-based Screenshot Setup for Microservices${NC}"
echo "================================================================"
echo -e "${YELLOW}🛍️  Fixing product image boxes and placeholder issues${NC}"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  docker-compose not found. Using docker compose instead.${NC}"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${BLUE}📦 Setting up microservices environment...${NC}"

# Create docker-compose file for screenshot testing
cat > docker-compose.screenshot.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build:
      context: ./microservices/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - carthub-network

  backend:
    build:
      context: ./microservices/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@database:5432/carthub
    depends_on:
      - database
    networks:
      - carthub-network

  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=carthub
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - carthub-network

  screenshot-service:
    build:
      context: .
      dockerfile: Dockerfile.screenshot
    volumes:
      - ./docs/images:/app/screenshots
      - ./scripts:/app/scripts
    depends_on:
      - frontend
      - backend
    networks:
      - carthub-network
    environment:
      - FRONTEND_URL=http://frontend:80
      - BACKEND_URL=http://backend:8000

networks:
  carthub-network:
    driver: bridge

volumes:
  postgres_data:
EOF

# Create Dockerfile for screenshot service
cat > Dockerfile.screenshot << 'EOF'
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
WORKDIR /app
COPY requirements.screenshot.txt .
RUN pip install --no-cache-dir -r requirements.screenshot.txt

# Copy scripts
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "🐳 Starting screenshot service..."\n\
echo "⏳ Waiting for services to be ready..."\n\
sleep 30\n\
echo "📸 Taking enhanced screenshots..."\n\
python scripts/take_screenshots_microservices.py\n\
echo "✅ Screenshots completed!"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
EOF

# Create requirements file for screenshot service
cat > requirements.screenshot.txt << 'EOF'
selenium==4.15.2
webdriver-manager==4.0.1
Pillow==10.1.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
EOF

echo -e "${BLUE}🔧 Building and starting microservices...${NC}"

# Build and start services
$COMPOSE_CMD -f docker-compose.screenshot.yml build

echo -e "${BLUE}🚀 Starting services...${NC}"
$COMPOSE_CMD -f docker-compose.screenshot.yml up -d frontend backend database

echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 20

# Check if services are running
echo -e "${BLUE}🔍 Checking service health...${NC}"
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend service is running${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend service not ready, will use file-based screenshots${NC}"
fi

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend service is running${NC}"
else
    echo -e "${YELLOW}⚠️  Backend service not ready, will use mock data${NC}"
fi

echo -e "${BLUE}📸 Running enhanced screenshot generation...${NC}"

# Run screenshot generation
if [ -f "screenshot_env/bin/activate" ]; then
    source screenshot_env/bin/activate
fi

python scripts/take_screenshots_microservices.py

echo -e "${BLUE}🧹 Cleaning up services...${NC}"
$COMPOSE_CMD -f docker-compose.screenshot.yml down

echo -e "${GREEN}✅ Enhanced screenshot generation completed!${NC}"
echo -e "${BLUE}📁 Screenshots saved to: docs/images/${NC}"
echo -e "${YELLOW}🛍️  Product image boxes should now be fixed with realistic data${NC}"
