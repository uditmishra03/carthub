"""
Updated Structure Tests - Validates current frontend and backend structure after refactoring
Tests for mixed JS/TS files, new cart directory structure, and updated API endpoints
"""

import pytest
import requests
import os
from pathlib import Path
import json


class TestUpdatedStructure:
    """Test suite for validating updated project structure after refactoring."""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Backend API base URL."""
        return "http://localhost:8000"
    
    def test_backend_structure_consistency(self):
        """Test that backend structure is consistent and complete."""
        backend_dir = Path("/Workshop/carthub/backend")
        
        # Check main application structure
        essential_files = [
            "app/main.py",
            "app/__init__.py",
            "app/routes/cart_routes.py",
            "app/routes/health_routes.py",
            "app/services/cart_service.py",
            "app/models/schemas.py",
            "app/models/cart_models.py",
            "app/config/database.py",
            "app/config/settings.py",
            "requirements.txt",
            "Dockerfile"
        ]
        
        for file_path in essential_files:
            full_path = backend_dir / file_path
            assert full_path.exists(), f"Backend file {file_path} not found"
            assert full_path.stat().st_size > 0, f"Backend file {file_path} is empty"
    
    def test_frontend_mixed_js_ts_structure(self):
        """Test frontend structure with mixed JS and TypeScript files."""
        frontend_dir = Path("/Workshop/carthub/frontend")
        
        # Check for both JS and TS versions of key files
        js_files = [
            "src/App.js",
            "src/index.js",
            "src/components/Cart.js",
            "src/components/CartContext.js",
            "src/components/ProductList.js",
            "src/components/Header.js",
            "src/components/Checkout.js",
            "src/services/cartService.js"
        ]
        
        ts_files = [
            "src/App.tsx",
            "src/index.tsx",
            "src/components/CartPage.tsx",
            "src/components/Header.tsx",
            "src/components/MiniCart.tsx",
            "src/components/ProductCard.tsx",
            "src/services/cartService.ts"
        ]
        
        # Check JS files exist
        for file_path in js_files:
            full_path = frontend_dir / file_path
            if full_path.exists():
                assert full_path.stat().st_size > 0, f"JS file {file_path} is empty"
        
        # Check TS files exist
        for file_path in ts_files:
            full_path = frontend_dir / file_path
            if full_path.exists():
                assert full_path.stat().st_size > 0, f"TS file {file_path} is empty"
        
        # At least one version of key components should exist
        assert (frontend_dir / "src/App.js").exists() or (frontend_dir / "src/App.tsx").exists()
        assert (frontend_dir / "src/index.js").exists() or (frontend_dir / "src/index.tsx").exists()
    
    def test_new_cart_directory_structure(self):
        """Test the new cart directory structure in frontend."""
        cart_dir = Path("/Workshop/carthub/frontend/cart")
        
        if cart_dir.exists():
            # Check cart subdirectories
            expected_subdirs = ["main", "demos", "legacy", "tests"]
            
            for subdir in expected_subdirs:
                subdir_path = cart_dir / subdir
                assert subdir_path.exists(), f"Cart subdirectory {subdir} not found"
                assert subdir_path.is_dir(), f"Cart {subdir} should be a directory"
            
            # Check for test files in cart/tests
            test_files = list((cart_dir / "tests").glob("*.html"))
            assert len(test_files) > 0, "No test files found in cart/tests directory"
    
    def test_package_json_configuration(self):
        """Test package.json configuration for mixed JS/TS setup."""
        package_json_path = Path("/Workshop/carthub/frontend/package.json")
        
        if package_json_path.exists():
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Check essential dependencies
            dependencies = package_data.get("dependencies", {})
            
            essential_deps = [
                "react",
                "react-dom",
                "react-router-dom",
                "axios"
            ]
            
            for dep in essential_deps:
                assert dep in dependencies, f"Essential dependency {dep} not found"
            
            # Check proxy configuration for backend
            assert "proxy" in package_data, "Proxy configuration for backend not found"
            assert "8000" in str(package_data["proxy"]), "Proxy should point to backend port 8000"
    
    def test_typescript_configuration(self):
        """Test TypeScript configuration if present."""
        tsconfig_path = Path("/Workshop/carthub/frontend/tsconfig.json")
        
        if tsconfig_path.exists():
            with open(tsconfig_path, 'r') as f:
                ts_config = json.load(f)
            
            # Check compiler options
            compiler_options = ts_config.get("compilerOptions", {})
            
            # Should have proper target and lib settings
            assert "target" in compiler_options, "TypeScript target not specified"
            assert "lib" in compiler_options, "TypeScript lib not specified"
            assert "allowJs" in compiler_options, "allowJs should be enabled for mixed JS/TS"
    
    def test_backend_api_endpoints_structure(self, api_base_url):
        """Test that backend API endpoints are properly structured."""
        # This test can run without services if we just check the route definitions
        backend_routes_path = Path("/Workshop/carthub/backend/app/routes/cart_routes.py")
        
        if backend_routes_path.exists():
            with open(backend_routes_path, 'r') as f:
                routes_content = f.read()
            
            # Check for essential route definitions
            expected_routes = [
                '@router.post("/items"',
                '@router.get("/{customer_id}"',
                '@router.put("/{customer_id}/items/{product_id}"',
                '@router.delete("/{customer_id}/items/{product_id}"',
                '@router.delete("/{customer_id}"',
                '@router.post("/checkout"'
            ]
            
            for route in expected_routes:
                assert route in routes_content, f"Route {route} not found in cart_routes.py"
    
    def test_frontend_service_integration(self):
        """Test frontend service integration structure."""
        service_js_path = Path("/Workshop/carthub/frontend/src/services/cartService.js")
        service_ts_path = Path("/Workshop/carthub/frontend/src/services/cartService.ts")
        
        # At least one service file should exist
        assert service_js_path.exists() or service_ts_path.exists(), "No cart service file found"
        
        # Check the JS service if it exists
        if service_js_path.exists():
            with open(service_js_path, 'r') as f:
                service_content = f.read()
            
            # Check for essential service methods
            essential_methods = [
                "getCart",
                "addItem", 
                "updateItemQuantity",
                "removeItem",
                "clearCart",
                "checkout",
                "healthCheck"
            ]
            
            for method in essential_methods:
                assert method in service_content, f"Service method {method} not found"
            
            # Check for proper API configuration
            assert "API_BASE_URL" in service_content, "API base URL configuration not found"
            assert "axios" in service_content, "Axios import not found"
    
    def test_component_structure_consistency(self):
        """Test that component structure is consistent."""
        components_dir = Path("/Workshop/carthub/frontend/src/components")
        
        if components_dir.exists():
            # Get all component files
            js_components = list(components_dir.glob("*.js"))
            ts_components = list(components_dir.glob("*.tsx"))
            
            # Should have some components
            total_components = len(js_components) + len(ts_components)
            assert total_components > 0, "No React components found"
            
            # Check for essential components (either JS or TS version)
            essential_components = ["Cart", "Header", "ProductList", "Checkout"]
            
            for component in essential_components:
                js_exists = (components_dir / f"{component}.js").exists()
                ts_exists = (components_dir / f"{component}.tsx").exists()
                
                assert js_exists or ts_exists, f"Component {component} not found in either JS or TS"
    
    def test_styling_structure(self):
        """Test styling structure and CSS files."""
        styles_dir = Path("/Workshop/carthub/frontend/src/styles")
        
        if styles_dir.exists():
            css_files = list(styles_dir.glob("*.css"))
            assert len(css_files) > 0, "No CSS files found in styles directory"
            
            # Check for main app CSS
            app_css_exists = (styles_dir / "App.css").exists()
            if app_css_exists:
                app_css_path = styles_dir / "App.css"
                assert app_css_path.stat().st_size > 0, "App.css is empty"
    
    def test_backend_models_consistency(self):
        """Test backend models are consistent and complete."""
        models_dir = Path("/Workshop/carthub/backend/app/models")
        
        if models_dir.exists():
            # Check schemas file
            schemas_path = models_dir / "schemas.py"
            if schemas_path.exists():
                with open(schemas_path, 'r') as f:
                    schemas_content = f.read()
                
                # Check for essential schema classes
                essential_schemas = [
                    "class CartItemRequest",
                    "class CartItemResponse", 
                    "class CartResponse",
                    "class CartOperationResponse",
                    "class CheckoutRequest",
                    "class CheckoutResponse",
                    "class HealthResponse"
                ]
                
                for schema in essential_schemas:
                    assert schema in schemas_content, f"Schema {schema} not found"
            
            # Check cart models file
            cart_models_path = models_dir / "cart_models.py"
            if cart_models_path.exists():
                with open(cart_models_path, 'r') as f:
                    models_content = f.read()
                
                # Check for essential model classes
                essential_models = ["class Cart", "class CartItem"]
                
                for model in essential_models:
                    assert model in models_content, f"Model {model} not found"
    
    def test_docker_configuration(self):
        """Test Docker configuration for both frontend and backend."""
        # Backend Dockerfile
        backend_dockerfile = Path("/Workshop/carthub/backend/Dockerfile")
        if backend_dockerfile.exists():
            with open(backend_dockerfile, 'r') as f:
                dockerfile_content = f.read()
            
            assert "FROM python:" in dockerfile_content, "Backend Dockerfile should use Python base image"
            assert "COPY requirements.txt" in dockerfile_content, "Should copy requirements.txt"
            assert "pip install" in dockerfile_content, "Should install Python dependencies"
        
        # Frontend Dockerfile
        frontend_dockerfile = Path("/Workshop/carthub/frontend/Dockerfile")
        if frontend_dockerfile.exists():
            with open(frontend_dockerfile, 'r') as f:
                dockerfile_content = f.read()
            
            assert "FROM node:" in dockerfile_content, "Frontend Dockerfile should use Node base image"
            assert "npm install" in dockerfile_content or "yarn install" in dockerfile_content, "Should install Node dependencies"
    
    def test_environment_configuration(self):
        """Test environment configuration and settings."""
        # Backend settings
        settings_path = Path("/Workshop/carthub/backend/app/config/settings.py")
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings_content = f.read()
            
            # Check for essential configuration
            essential_configs = [
                "DATABASE_URL",
                "ALLOWED_ORIGINS"
            ]
            
            for config in essential_configs:
                assert config in settings_content, f"Configuration {config} not found in settings"
    
    def test_test_files_structure(self):
        """Test the structure of existing test files."""
        # Check main test directory
        main_tests_dir = Path("/Workshop/carthub/tests")
        assert main_tests_dir.exists(), "Main tests directory not found"
        
        # Check for our comprehensive test files
        our_test_files = [
            "test_backend_api.py",
            "test_frontend_functionality.py",
            "test_integration_e2e.py",
            "test_performance.py",
            "conftest.py"
        ]
        
        for test_file in our_test_files:
            test_path = main_tests_dir / test_file
            assert test_path.exists(), f"Test file {test_file} not found"
            assert test_path.stat().st_size > 0, f"Test file {test_file} is empty"
        
        # Check cart test files if they exist
        cart_tests_dir = Path("/Workshop/carthub/frontend/cart/tests")
        if cart_tests_dir.exists():
            html_test_files = list(cart_tests_dir.glob("*.html"))
            js_test_files = list(cart_tests_dir.glob("*.js"))
            
            total_cart_tests = len(html_test_files) + len(js_test_files)
            assert total_cart_tests > 0, "No test files found in cart/tests directory"
    
    def test_git_structure_after_refactoring(self):
        """Test git structure after refactoring."""
        project_root = Path("/Workshop/carthub")
        
        # Check .gitignore
        gitignore_path = project_root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            # Should ignore common files
            ignore_patterns = [
                "__pycache__",
                "node_modules",
                ".env",
                "*.pyc"
            ]
            
            for pattern in ignore_patterns:
                assert pattern in gitignore_content, f"Gitignore should include {pattern}"
    
    def test_documentation_updates(self):
        """Test that documentation reflects current structure."""
        docs_dir = Path("/Workshop/carthub/docs")
        
        if docs_dir.exists():
            # Check for testing guide
            testing_guide = docs_dir / "TESTING_GUIDE.md"
            if testing_guide.exists():
                assert testing_guide.stat().st_size > 0, "Testing guide should not be empty"
        
        # Check main README
        readme_path = Path("/Workshop/carthub/README.md")
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                readme_content = f.read()
            
            # Should mention current version
            assert "2.0.0" in readme_content, "README should mention current version"
            assert "FastAPI" in readme_content, "README should mention FastAPI"
            assert "React" in readme_content, "README should mention React"
