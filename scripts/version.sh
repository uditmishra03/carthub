#!/bin/bash

# Version Management Script for Shopping Cart API
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

# Function to get current version
get_current_version() {
    if [ -f "VERSION" ]; then
        cat VERSION
    else
        echo "0.0.0"
    fi
}

# Function to validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_error "Invalid version format. Use semantic versioning (e.g., 1.0.0)"
        return 1
    fi
    return 0
}

# Function to update version in files
update_version_files() {
    local new_version=$1
    
    # Update VERSION file
    echo "$new_version" > VERSION
    
    # Update package.json if it exists
    if [ -f "frontend/package.json" ]; then
        sed -i "s/\"version\": \".*\"/\"version\": \"$new_version\"/" frontend/package.json
    fi
    
    # Update backend version if it exists
    if [ -f "backend/app/main.py" ]; then
        sed -i "s/version=\".*\"/version=\"$new_version\"/" backend/app/main.py
    fi
    
    # Update CDK version if it exists
    if [ -f "infrastructure_cdk/app.py" ]; then
        # Add version comment if not exists
        if ! grep -q "# Version:" infrastructure_cdk/app.py; then
            sed -i "1i# Version: $new_version" infrastructure_cdk/app.py
        else
            sed -i "s/# Version: .*/# Version: $new_version/" infrastructure_cdk/app.py
        fi
    fi
}

# Function to create git tag
create_git_tag() {
    local version=$1
    local message=$2
    
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git tag -a "v$version" -m "$message"
        print_success "Created git tag: v$version"
    else
        print_warning "Not a git repository. Skipping tag creation."
    fi
}

# Function to bump version
bump_version() {
    local bump_type=$1
    local current_version=$(get_current_version)
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $bump_type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid bump type. Use: major, minor, or patch"
            return 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Main script logic
case "${1:-}" in
    "current")
        echo "Current version: $(get_current_version)"
        ;;
    "bump")
        if [ -z "${2:-}" ]; then
            print_error "Usage: $0 bump [major|minor|patch]"
            exit 1
        fi
        
        current_version=$(get_current_version)
        new_version=$(bump_version $2)
        
        print_status "Bumping version from $current_version to $new_version"
        
        update_version_files $new_version
        create_git_tag $new_version "Version bump: $2"
        
        print_success "Version bumped to $new_version"
        ;;
    "set")
        if [ -z "${2:-}" ]; then
            print_error "Usage: $0 set <version>"
            exit 1
        fi
        
        new_version=$2
        if ! validate_version $new_version; then
            exit 1
        fi
        
        current_version=$(get_current_version)
        print_status "Setting version from $current_version to $new_version"
        
        update_version_files $new_version
        create_git_tag $new_version "Version set to $new_version"
        
        print_success "Version set to $new_version"
        ;;
    "tag")
        current_version=$(get_current_version)
        message="${2:-Release version $current_version}"
        create_git_tag $current_version "$message"
        ;;
    "release")
        current_version=$(get_current_version)
        print_status "Preparing release for version $current_version"
        
        # Check if working directory is clean
        if git rev-parse --git-dir > /dev/null 2>&1; then
            if [ -n "$(git status --porcelain)" ]; then
                print_error "Working directory is not clean. Commit changes first."
                exit 1
            fi
        fi
        
        # Create release tag
        create_git_tag $current_version "Release version $current_version"
        
        print_success "Release $current_version prepared"
        print_status "Next steps:"
        echo "1. Push tags: git push origin --tags"
        echo "2. Create GitHub release"
        echo "3. Deploy to environments"
        ;;
    "help"|"--help"|"-h"|"")
        echo "Version Management Script"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  current              Show current version"
        echo "  bump <type>          Bump version (major|minor|patch)"
        echo "  set <version>        Set specific version"
        echo "  tag [message]        Create git tag for current version"
        echo "  release              Prepare release (create tag)"
        echo "  help                 Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 current           # Show current version"
        echo "  $0 bump patch        # Bump patch version (1.0.0 -> 1.0.1)"
        echo "  $0 bump minor        # Bump minor version (1.0.0 -> 1.1.0)"
        echo "  $0 bump major        # Bump major version (1.0.0 -> 2.0.0)"
        echo "  $0 set 2.1.0         # Set version to 2.1.0"
        echo "  $0 release           # Prepare release"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
