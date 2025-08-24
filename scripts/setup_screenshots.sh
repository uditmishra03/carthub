#!/bin/bash

# Setup script for automated screenshot generation
# Installs Chrome, ChromeDriver, and Python dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Setting up automated screenshot generation..."

# Check if running on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Detected Linux system"
    
    # Update package list
    print_status "Updating package list..."
    sudo apt-get update -qq
    
    # Install Chrome
    print_status "Installing Google Chrome..."
    if ! command -v google-chrome &> /dev/null; then
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update -qq
        sudo apt-get install -y google-chrome-stable
        print_success "Google Chrome installed"
    else
        print_success "Google Chrome already installed"
    fi
    
    # Install ChromeDriver using webdriver-manager (Python will handle this)
    print_status "ChromeDriver will be managed by webdriver-manager"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Detected macOS system"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew not found. Please install Homebrew first:"
        print_error "https://brew.sh/"
        exit 1
    fi
    
    # Install Chrome
    print_status "Installing Google Chrome..."
    if ! command -v google-chrome &> /dev/null; then
        brew install --cask google-chrome
        print_success "Google Chrome installed"
    else
        print_success "Google Chrome already installed"
    fi
    
    # Install ChromeDriver
    print_status "Installing ChromeDriver..."
    if ! command -v chromedriver &> /dev/null; then
        brew install chromedriver
        print_success "ChromeDriver installed"
    else
        print_success "ChromeDriver already installed"
    fi
    
else
    print_warning "Unsupported operating system: $OSTYPE"
    print_warning "Please install Google Chrome and ChromeDriver manually"
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r scripts/requirements-screenshots.txt
print_success "Python dependencies installed"

# Create output directory
print_status "Creating output directory..."
mkdir -p docs/images
print_success "Output directory created: docs/images"

# Make screenshot script executable
chmod +x scripts/take_screenshots.py

print_success "Setup completed successfully!"
print_status "You can now run screenshots with:"
print_status "  python scripts/take_screenshots.py"
print_status ""
print_status "Available options:"
print_status "  --url http://localhost:3000    # Frontend URL"
print_status "  --api-url http://localhost:8000 # Backend API URL"
print_status "  --output docs/images           # Output directory"
print_status "  --no-headless                  # Show browser window"
print_status "  --no-api                       # Skip API screenshots"
