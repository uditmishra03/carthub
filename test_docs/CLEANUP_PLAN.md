# 🧹 CARTHUB APPLICATION CLEANUP PLAN

## Current Status Assessment
- ✅ Application is running and accessible
- ✅ Kubernetes deployment operational
- ✅ CI/CD pipelines partially working
- ⚠️ Multiple duplicate directories and files
- ⚠️ Inconsistent structure across components
- ⚠️ Old test files and unused assets

## Cleanup Objectives
1. **Consolidate Architecture**: Remove duplicate directories and standardize structure
2. **Clean Dependencies**: Remove unused node_modules and virtual environments
3. **Organize Documentation**: Centralize and clean up documentation
4. **Streamline CI/CD**: Fix pipeline issues and remove redundant scripts
5. **Optimize File Structure**: Remove temporary files and organize assets

## Cleanup Actions

### 1. Directory Structure Consolidation
- **Keep**: `/microservices/` (primary architecture)
- **Remove**: `/frontend/`, `/backend/` (duplicates)
- **Keep**: `/infrastructure_cdk/` (CDK infrastructure)
- **Clean**: `/docs/` (organize and deduplicate)

### 2. Dependency Cleanup
- **Remove**: Large node_modules directories
- **Remove**: Python virtual environments
- **Keep**: package.json and requirements.txt files

### 3. Documentation Organization
- **Consolidate**: Multiple README files
- **Remove**: Duplicate documentation
- **Organize**: Screenshots and images

### 4. CI/CD Optimization
- **Fix**: Pipeline failures
- **Remove**: Redundant deployment scripts
- **Standardize**: Build configurations

### 5. Asset Management
- **Remove**: Temporary files and caches
- **Organize**: Images and screenshots
- **Clean**: Test artifacts

## Files to Remove
- `/frontend/node_modules/` (870 directories)
- `/microservices/frontend/node_modules/` (duplicate)
- `/screenshot_env/` (temporary virtual environment)
- `/tests/venv/` (test virtual environment)
- `/.pytest_cache/` (test cache)
- Duplicate buildspec files
- Old deployment scripts

## Files to Keep and Organize
- Core microservices architecture
- CDK infrastructure code
- Essential documentation
- Working CI/CD configurations
- Production-ready Kubernetes manifests

## Expected Outcomes
- Reduced repository size by ~80%
- Clear, single-source architecture
- Working CI/CD pipelines
- Organized documentation
- Production-ready codebase
