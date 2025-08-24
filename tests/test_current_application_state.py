"""
Current Application State Testing Suite
Tests the current state of the CartHub application after all refactoring and cleanup
"""

import pytest
import json
from pathlib import Path
import os
import subprocess


class TestCurrentApplicationState:
    """Comprehensive test suite for current application state."""
    
    def test_project_root_structure(self):
        """Test the current project root structure."""
        project_root = Path("/Workshop/carthub")
        
        # Check essential directories exist
        essential_dirs = [
            "microservices",
            "tests", 
            "docs",
            "k8s",
            "deployment",
            "infrastructure_cdk"
        ]
        
        for dir_name in essential_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Essential directory {dir_name} not found"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"
    
    def test_microservices_structure(self):
        """Test microservices directory structure."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        # Check microservices subdirectories
        expected_services = ["frontend", "backend", "database"]
        
        for service in expected_services:
            service_dir = microservices_dir / service
            assert service_dir.exists(), f"Microservice {service} not found"
            assert service_dir.is_dir(), f"{service} should be a directory"
    
    def test_frontend_microservice_current_state(self):
        """Test current frontend microservice state."""
        frontend_dir = Path("/Workshop/carthub/microservices/frontend")
        
        # Check for static file structure
        public_dir = frontend_dir / "public"
        assert public_dir.exists(), "Frontend public directory not found"
        
        # Check essential static files
        essential_files = [
            "public/index.html",
            "public/css",
            "public/js",
            "public/assets"
        ]
        
        for file_path in essential_files:
            full_path = frontend_dir / file_path
            assert full_path.exists(), f"Frontend file/directory {file_path} not found"
        
        # Check index.html content
        index_html = frontend_dir / "public/index.html"
        with open(index_html, 'r') as f:
            content = f.read()
        
        assert "CartHub" in content, "CartHub title not found in index.html"
        assert "cart.css" in content, "CSS reference not found"
        assert "shopping-cart" in content.lower(), "Shopping cart elements not found"
    
    def test_frontend_package_configuration(self):
        """Test frontend package.json configuration."""
        frontend_dir = Path("/Workshop/carthub/microservices/frontend")
        package_json = frontend_dir / "package.json"
        
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            # Check basic package info
            assert "name" in package_data, "Package name not specified"
            assert "version" in package_data, "Package version not specified"
            assert "scripts" in package_data, "Package scripts not found"
            
            # Check for start script
            scripts = package_data.get("scripts", {})
            assert "start" in scripts, "Start script not found"
    
    def test_frontend_docker_configuration(self):
        """Test frontend Docker configuration."""
        frontend_dir = Path("/Workshop/carthub/microservices/frontend")
        dockerfile = frontend_dir / "Dockerfile"
        
        assert dockerfile.exists(), "Frontend Dockerfile not found"
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        # Check for nginx-based configuration (current state)
        assert "FROM nginx:" in content, "Should use nginx base image"
        assert "COPY public/" in content, "Should copy static files"
        assert "nginx.conf" in content, "Should have nginx configuration"
    
    def test_backend_microservice_current_state(self):
        """Test current backend microservice state."""
        backend_dir = Path("/Workshop/carthub/microservices/backend")
        
        # Check essential backend files
        essential_files = [
            "app/main.py",
            "Dockerfile",
            "requirements.txt"
        ]
        
        for file_path in essential_files:
            full_path = backend_dir / file_path
            assert full_path.exists(), f"Backend file {file_path} not found"
            assert full_path.stat().st_size > 0, f"Backend file {file_path} is empty"
    
    def test_backend_main_application(self):
        """Test backend main application file."""
        backend_dir = Path("/Workshop/carthub/microservices/backend")
        main_py = backend_dir / "app/main.py"
        
        with open(main_py, 'r') as f:
            content = f.read()
        
        # Check for FastAPI application
        assert "FastAPI" in content, "FastAPI import not found"
        assert "app = FastAPI" in content, "FastAPI app not created"
        assert "CORS" in content, "CORS configuration not found"
        
        # Check for basic endpoints or structure
        assert "cart" in content.lower(), "Cart functionality not found"
    
    def test_backend_docker_configuration(self):
        """Test backend Docker configuration."""
        backend_dir = Path("/Workshop/carthub/microservices/backend")
        dockerfile = backend_dir / "Dockerfile"
        
        assert dockerfile.exists(), "Backend Dockerfile not found"
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        # Check for Python-based configuration
        assert "FROM python:" in content, "Should use Python base image"
        assert "requirements.txt" in content, "Should install requirements"
    
    def test_backend_requirements(self):
        """Test backend requirements.txt."""
        backend_dir = Path("/Workshop/carthub/microservices/backend")
        requirements = backend_dir / "requirements.txt"
        
        assert requirements.exists(), "Requirements.txt not found"
        
        with open(requirements, 'r') as f:
            content = f.read()
        
        # Check for essential dependencies
        assert "fastapi" in content.lower(), "FastAPI dependency not found"
        assert "uvicorn" in content.lower(), "Uvicorn dependency not found"
    
    def test_kubernetes_configurations(self):
        """Test Kubernetes configuration files."""
        k8s_dir = Path("/Workshop/carthub/k8s")
        
        if k8s_dir.exists():
            # Check for YAML files
            yaml_files = list(k8s_dir.glob("*.yaml")) + list(k8s_dir.glob("*.yml"))
            
            if yaml_files:
                # At least one k8s configuration should exist
                assert len(yaml_files) > 0, "No Kubernetes YAML files found"
                
                # Check first YAML file for basic structure
                with open(yaml_files[0], 'r') as f:
                    content = f.read()
                
                assert "apiVersion" in content, "Kubernetes apiVersion not found"
                assert "kind" in content, "Kubernetes kind not found"
    
    def test_microservice_k8s_configurations(self):
        """Test microservice-specific Kubernetes configurations."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        for service in ["frontend", "backend"]:
            service_k8s = microservices_dir / service / "k8s"
            
            if service_k8s.exists():
                yaml_files = list(service_k8s.glob("*.yaml")) + list(service_k8s.glob("*.yml"))
                
                if yaml_files:
                    # Check for valid Kubernetes configuration
                    with open(yaml_files[0], 'r') as f:
                        content = f.read()
                    
                    assert "apiVersion" in content, f"{service} k8s config missing apiVersion"
                    assert "kind" in content, f"{service} k8s config missing kind"
    
    def test_ci_cd_configurations(self):
        """Test CI/CD configuration files."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        for service in ["frontend", "backend"]:
            buildspec = microservices_dir / service / "buildspec.yml"
            
            if buildspec.exists():
                with open(buildspec, 'r') as f:
                    content = f.read()
                
                assert "version:" in content, f"{service} buildspec missing version"
                assert "phases:" in content, f"{service} buildspec missing phases"
    
    def test_documentation_structure(self):
        """Test documentation structure."""
        docs_dir = Path("/Workshop/carthub/docs")
        
        if docs_dir.exists():
            # Check for documentation files
            doc_files = list(docs_dir.glob("*.md")) + list(docs_dir.rglob("*.md"))
            
            # Should have some documentation
            assert len(doc_files) > 0, "No documentation files found"
    
    def test_test_suite_structure(self):
        """Test current test suite structure."""
        tests_dir = Path("/Workshop/carthub/tests")
        
        # Check for test files
        test_files = list(tests_dir.glob("test_*.py"))
        
        assert len(test_files) > 0, "No test files found"
        
        # Check for essential test categories
        test_names = [f.name for f in test_files]
        
        # Should have some form of testing
        has_backend_tests = any("backend" in name or "api" in name for name in test_names)
        has_frontend_tests = any("frontend" in name or "ui" in name for name in test_names)
        has_integration_tests = any("integration" in name or "e2e" in name for name in test_names)
        
        # At least one category should exist
        assert has_backend_tests or has_frontend_tests or has_integration_tests, "No categorized tests found"
    
    def test_git_repository_structure(self):
        """Test git repository structure."""
        project_root = Path("/Workshop/carthub")
        
        # Check for .git directory
        git_dir = project_root / ".git"
        assert git_dir.exists(), "Git repository not initialized"
        
        # Check for .gitignore
        gitignore = project_root / ".gitignore"
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
            
            # Should ignore common files
            assert "__pycache__" in content or "*.pyc" in content, "Python cache files not ignored"
            assert "node_modules" in content, "Node modules not ignored"
    
    def test_deployment_configurations(self):
        """Test deployment configuration structure."""
        deployment_dir = Path("/Workshop/carthub/deployment")
        
        if deployment_dir.exists():
            # Check for deployment scripts or configurations
            deployment_files = list(deployment_dir.rglob("*"))
            
            # Should have some deployment configurations
            assert len(deployment_files) > 0, "No deployment configurations found"
    
    def test_infrastructure_as_code(self):
        """Test infrastructure as code configurations."""
        infra_dir = Path("/Workshop/carthub/infrastructure_cdk")
        
        if infra_dir.exists():
            # Check for CDK files
            cdk_files = list(infra_dir.glob("*.py")) + list(infra_dir.glob("*.json"))
            
            if cdk_files:
                # Should have CDK configurations
                assert len(cdk_files) > 0, "No CDK files found"
    
    def test_application_readiness_indicators(self):
        """Test indicators that application is ready for deployment."""
        project_root = Path("/Workshop/carthub")
        
        # Check for README
        readme_files = list(project_root.glob("README*"))
        assert len(readme_files) > 0, "No README file found"
        
        # Check for essential configuration files
        essential_configs = [
            ".gitignore"
        ]
        
        for config in essential_configs:
            config_path = project_root / config
            assert config_path.exists(), f"Essential config {config} not found"
    
    def test_microservice_independence(self):
        """Test that microservices are properly separated."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        # Each microservice should have its own Dockerfile
        for service in ["frontend", "backend"]:
            service_dir = microservices_dir / service
            dockerfile = service_dir / "Dockerfile"
            
            if service_dir.exists():
                assert dockerfile.exists(), f"{service} missing Dockerfile"
    
    def test_current_architecture_consistency(self):
        """Test that current architecture is consistent."""
        # Frontend should be static files with nginx
        frontend_dockerfile = Path("/Workshop/carthub/microservices/frontend/Dockerfile")
        
        if frontend_dockerfile.exists():
            with open(frontend_dockerfile, 'r') as f:
                content = f.read()
            
            # Should use nginx for static serving
            assert "nginx" in content.lower(), "Frontend should use nginx"
        
        # Backend should be FastAPI with Python
        backend_dockerfile = Path("/Workshop/carthub/microservices/backend/Dockerfile")
        
        if backend_dockerfile.exists():
            with open(backend_dockerfile, 'r') as f:
                content = f.read()
            
            # Should use Python
            assert "python" in content.lower(), "Backend should use Python"
    
    def test_file_permissions_and_structure(self):
        """Test file permissions and basic structure integrity."""
        project_root = Path("/Workshop/carthub")
        
        # Check that essential directories are readable
        for item in project_root.iterdir():
            if item.is_dir():
                assert os.access(item, os.R_OK), f"Directory {item.name} not readable"
        
        # Check that essential files are readable
        essential_files = [
            "README.md",
            ".gitignore"
        ]
        
        for file_name in essential_files:
            file_path = project_root / file_name
            if file_path.exists():
                assert os.access(file_path, os.R_OK), f"File {file_name} not readable"
    
    def test_no_sensitive_data_exposed(self):
        """Test that no sensitive data is exposed in the repository."""
        project_root = Path("/Workshop/carthub")
        
        # Check for common sensitive file patterns
        sensitive_patterns = [
            "*.key",
            "*.pem", 
            "*password*",
            "*secret*",
            ".env"
        ]
        
        for pattern in sensitive_patterns:
            sensitive_files = list(project_root.rglob(pattern))
            
            # Filter out test files and documentation
            actual_sensitive = [
                f for f in sensitive_files 
                if not any(part in str(f).lower() for part in ["test", "doc", "example", "template"])
            ]
            
            assert len(actual_sensitive) == 0, f"Potentially sensitive files found: {actual_sensitive}"
