"""
Test suite for Carthub Frontend Build Process
"""

import pytest
import os
import json
import subprocess
from pathlib import Path

class TestPackageConfiguration:
    """Test package.json configuration"""
    
    def test_package_json_exists(self):
        """Test that package.json exists"""
        package_path = Path(__file__).parent.parent / "package.json"
        assert package_path.exists(), "package.json should exist"

    def test_package_json_valid(self):
        """Test that package.json is valid JSON"""
        package_path = Path(__file__).parent.parent / "package.json"
        
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        # Check required fields
        assert "name" in package_data
        assert "version" in package_data
        assert "dependencies" in package_data
        assert "scripts" in package_data

    def test_required_dependencies(self):
        """Test that required dependencies are present"""
        package_path = Path(__file__).parent.parent / "package.json"
        
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        required_deps = ["react", "react-dom", "axios"]
        dependencies = package_data.get("dependencies", {})
        
        for dep in required_deps:
            assert dep in dependencies, f"Required dependency {dep} is missing"

    def test_required_scripts(self):
        """Test that required scripts are present"""
        package_path = Path(__file__).parent.parent / "package.json"
        
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        required_scripts = ["start", "build", "test"]
        scripts = package_data.get("scripts", {})
        
        for script in required_scripts:
            assert script in scripts, f"Required script {script} is missing"

class TestDockerConfiguration:
    """Test Docker configuration"""
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile should exist"

    def test_dockerfile_content(self):
        """Test Dockerfile content"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
        
        # Check for multi-stage build
        assert "FROM node:" in dockerfile_content, "Should use Node.js base image"
        assert "FROM nginx:" in dockerfile_content, "Should use nginx for production"
        assert "COPY --from=build" in dockerfile_content, "Should use multi-stage build"

    def test_nginx_config_exists(self):
        """Test that nginx configuration exists"""
        nginx_config_path = Path(__file__).parent.parent / "nginx.conf"
        assert nginx_config_path.exists(), "nginx.conf should exist"

    def test_nginx_config_content(self):
        """Test nginx configuration content"""
        nginx_config_path = Path(__file__).parent.parent / "nginx.conf"
        
        with open(nginx_config_path, 'r') as f:
            nginx_content = f.read()
        
        # Check for required configurations
        assert "server {" in nginx_content, "Should have server block"
        assert "listen 80" in nginx_content, "Should listen on port 80"
        assert "/health" in nginx_content, "Should have health check endpoint"
        assert "proxy_pass" in nginx_content, "Should have API proxy configuration"

class TestKubernetesManifests:
    """Test Kubernetes manifest files"""
    
    def test_k8s_directory_exists(self):
        """Test that k8s directory exists"""
        k8s_path = Path(__file__).parent.parent / "k8s"
        assert k8s_path.exists(), "k8s directory should exist"
        assert k8s_path.is_dir(), "k8s should be a directory"

    def test_required_manifests_exist(self):
        """Test that required Kubernetes manifests exist"""
        k8s_path = Path(__file__).parent.parent / "k8s"
        required_files = [
            "namespace.yaml",
            "deployment.yaml", 
            "service.yaml",
            "hpa.yaml",
            "ingress.yaml"
        ]
        
        for file_name in required_files:
            file_path = k8s_path / file_name
            assert file_path.exists(), f"Required manifest {file_name} should exist"

    def test_deployment_manifest_content(self):
        """Test deployment manifest content"""
        deployment_path = Path(__file__).parent.parent / "k8s" / "deployment.yaml"
        
        with open(deployment_path, 'r') as f:
            deployment_content = f.read()
        
        # Check for required fields
        assert "apiVersion: apps/v1" in deployment_content
        assert "kind: Deployment" in deployment_content
        assert "name: frontend-deployment" in deployment_content
        assert "IMAGE_URI_PLACEHOLDER" in deployment_content
        assert "containerPort: 80" in deployment_content

    def test_service_manifest_content(self):
        """Test service manifest content"""
        service_path = Path(__file__).parent.parent / "k8s" / "service.yaml"
        
        with open(service_path, 'r') as f:
            service_content = f.read()
        
        # Check for required fields
        assert "apiVersion: v1" in service_content
        assert "kind: Service" in service_content
        assert "name: frontend-service" in service_content
        assert "port: 80" in service_content

    def test_hpa_manifest_content(self):
        """Test HPA manifest content"""
        hpa_path = Path(__file__).parent.parent / "k8s" / "hpa.yaml"
        
        with open(hpa_path, 'r') as f:
            hpa_content = f.read()
        
        # Check for required fields
        assert "apiVersion: autoscaling/v2" in hpa_content
        assert "kind: HorizontalPodAutoscaler" in hpa_content
        assert "name: frontend-hpa" in hpa_content
        assert "minReplicas:" in hpa_content
        assert "maxReplicas:" in hpa_content

    def test_ingress_manifest_content(self):
        """Test ingress manifest content"""
        ingress_path = Path(__file__).parent.parent / "k8s" / "ingress.yaml"
        
        with open(ingress_path, 'r') as f:
            ingress_content = f.read()
        
        # Check for required fields
        assert "apiVersion: networking.k8s.io/v1" in ingress_content
        assert "kind: Ingress" in ingress_content
        assert "name: frontend-ingress" in ingress_content
        assert "alb.ingress.kubernetes.io" in ingress_content

class TestBuildSpec:
    """Test CodeBuild buildspec configuration"""
    
    def test_buildspec_exists(self):
        """Test that buildspec.yml exists"""
        buildspec_path = Path(__file__).parent.parent / "buildspec.yml"
        assert buildspec_path.exists(), "buildspec.yml should exist"

    def test_buildspec_content(self):
        """Test buildspec.yml content"""
        buildspec_path = Path(__file__).parent.parent / "buildspec.yml"
        
        with open(buildspec_path, 'r') as f:
            buildspec_content = f.read()
        
        # Check for required phases
        assert "version: 0.2" in buildspec_content
        assert "pre_build:" in buildspec_content
        assert "build:" in buildspec_content
        assert "post_build:" in buildspec_content
        
        # Check for required commands
        assert "docker build" in buildspec_content
        assert "docker push" in buildspec_content
        assert "kubectl apply" in buildspec_content
        assert "aws ecr get-login-password" in buildspec_content

class TestSourceStructure:
    """Test source code structure"""
    
    def test_src_directory_exists(self):
        """Test that src directory exists"""
        src_path = Path(__file__).parent.parent / "src"
        assert src_path.exists(), "src directory should exist"

    def test_public_directory_exists(self):
        """Test that public directory exists"""
        public_path = Path(__file__).parent.parent / "public"
        assert public_path.exists(), "public directory should exist"

    def test_index_html_exists(self):
        """Test that index.html exists"""
        index_path = Path(__file__).parent.parent / "public" / "index.html"
        assert index_path.exists(), "public/index.html should exist"

class TestEnvironmentConfiguration:
    """Test environment configuration"""
    
    def test_environment_variables_documented(self):
        """Test that environment variables are documented in README"""
        readme_path = Path(__file__).parent.parent / "README.md"
        
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                readme_content = f.read()
            
            # Check for environment variable documentation
            assert "Environment Variables" in readme_content or "REACT_APP_" in readme_content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
