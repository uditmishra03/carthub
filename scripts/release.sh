#!/bin/bash

# Release Management Script for Shopping Cart API
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

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not a git repository"
        exit 1
    fi
}

# Function to check if working directory is clean
check_clean_working_dir() {
    if [ -n "$(git status --porcelain)" ]; then
        print_error "Working directory is not clean. Please commit or stash changes."
        git status --short
        exit 1
    fi
}

# Function to check if we're on main branch
check_main_branch() {
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        print_warning "Not on main branch (currently on: $current_branch)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    if command -v python &> /dev/null; then
        python -m pytest tests/ -v
        if [ $? -ne 0 ]; then
            print_error "Tests failed"
            exit 1
        fi
    else
        print_warning "Python not found, skipping tests"
    fi
}

# Function to update changelog
update_changelog() {
    local version=$1
    local date=$(date +%Y-%m-%d)
    
    print_status "Updating CHANGELOG.md..."
    
    # Create backup
    cp CHANGELOG.md CHANGELOG.md.bak
    
    # Update changelog
    sed -i "s/## \[Unreleased\]/## [Unreleased]\n\n## [$version] - $date/" CHANGELOG.md
    
    print_success "CHANGELOG.md updated"
}

# Function to create release commit
create_release_commit() {
    local version=$1
    
    print_status "Creating release commit..."
    
    git add VERSION CHANGELOG.md
    git add frontend/package.json 2>/dev/null || true
    git add backend/app/main.py 2>/dev/null || true
    git add infrastructure_cdk/app.py 2>/dev/null || true
    
    git commit -m "Release version $version

- Updated version to $version
- Updated CHANGELOG.md
- Updated version in application files"
    
    print_success "Release commit created"
}

# Function to create and push tag
create_and_push_tag() {
    local version=$1
    
    print_status "Creating and pushing tag v$version..."
    
    git tag -a "v$version" -m "Release version $version"
    git push origin "v$version"
    
    print_success "Tag v$version created and pushed"
}

# Function to push changes
push_changes() {
    print_status "Pushing changes to remote..."
    git push origin main
    print_success "Changes pushed to remote"
}

# Function to create GitHub release (if gh CLI is available)
create_github_release() {
    local version=$1
    
    if command -v gh &> /dev/null; then
        print_status "Creating GitHub release..."
        
        # Extract changelog for this version
        local changelog_section=$(awk "/## \[$version\]/,/## \[/{if(/## \[/ && !/## \[$version\]/) exit; if(!/## \[$version\]/) print}" CHANGELOG.md)
        
        gh release create "v$version" \
            --title "Release $version" \
            --notes "$changelog_section" \
            --latest
            
        print_success "GitHub release created"
    else
        print_warning "GitHub CLI not found. Please create release manually at:"
        echo "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/' | sed 's/\.git$//')/releases/new?tag=v$version"
    fi
}

# Main release function
perform_release() {
    local release_type=$1
    
    print_status "🚀 Starting release process..."
    
    # Pre-flight checks
    check_git_repo
    check_clean_working_dir
    check_main_branch
    
    # Get current version and calculate new version
    local current_version=$(./scripts/version.sh current | cut -d' ' -f3)
    local new_version
    
    if [ "$release_type" = "custom" ]; then
        read -p "Enter new version: " new_version
        if [[ ! $new_version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            print_error "Invalid version format. Use semantic versioning (e.g., 1.0.0)"
            exit 1
        fi
    else
        new_version=$(./scripts/version.sh bump $release_type | tail -n1 | cut -d' ' -f4)
    fi
    
    print_status "Releasing version $new_version (from $current_version)"
    
    # Confirm release
    read -p "Continue with release? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Release cancelled"
        exit 0
    fi
    
    # Run tests
    run_tests
    
    # Update version files
    ./scripts/version.sh set $new_version
    
    # Update changelog
    update_changelog $new_version
    
    # Create release commit
    create_release_commit $new_version
    
    # Create and push tag
    create_and_push_tag $new_version
    
    # Push changes
    push_changes
    
    # Create GitHub release
    create_github_release $new_version
    
    print_success "🎉 Release $new_version completed successfully!"
    
    echo ""
    echo "Next steps:"
    echo "1. Monitor CI/CD pipeline for deployment"
    echo "2. Verify deployment in staging environment"
    echo "3. Promote to production if tests pass"
    echo "4. Update documentation if needed"
    echo "5. Announce release to team"
}

# Script usage
case "${1:-}" in
    "patch")
        perform_release "patch"
        ;;
    "minor")
        perform_release "minor"
        ;;
    "major")
        perform_release "major"
        ;;
    "custom")
        perform_release "custom"
        ;;
    "help"|"--help"|"-h"|"")
        echo "Release Management Script"
        echo ""
        echo "Usage: $0 <release-type>"
        echo ""
        echo "Release Types:"
        echo "  patch    Patch release (1.0.0 -> 1.0.1)"
        echo "  minor    Minor release (1.0.0 -> 1.1.0)"
        echo "  major    Major release (1.0.0 -> 2.0.0)"
        echo "  custom   Custom version (prompts for version)"
        echo "  help     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 patch     # Create patch release"
        echo "  $0 minor     # Create minor release"
        echo "  $0 major     # Create major release"
        echo "  $0 custom    # Create custom version release"
        echo ""
        echo "Prerequisites:"
        echo "  - Clean working directory"
        echo "  - On main branch (recommended)"
        echo "  - All tests passing"
        echo "  - GitHub CLI (optional, for automatic release creation)"
        ;;
    *)
        print_error "Unknown release type: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
