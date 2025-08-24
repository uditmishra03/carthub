"""
Test Structure Validation - Tests that can run without services
Validates test files, configuration, and basic structure
"""

import pytest
import os
import json
import importlib.util
from pathlib import Path


class TestStructureValidation:
    """Test suite for validating test structure and configuration."""
    
    def test_test_files_exist(self):
        """Test that all required test files exist."""
        test_dir = Path(__file__).parent
        
        required_test_files = [
            "test_backend_api.py",
            "test_frontend_functionality.py", 
            "test_integration_e2e.py",
            "test_performance.py",
            "conftest.py"
        ]
        
        for test_file in required_test_files:
            file_path = test_dir / test_file
            assert file_path.exists(), f"Required test file {test_file} not found"
            assert file_path.stat().st_size > 0, f"Test file {test_file} is empty"
    
    def test_test_files_syntax(self):
        """Test that all test files have valid Python syntax."""
        test_dir = Path(__file__).parent
        
        test_files = [
            "test_backend_api.py",
            "test_frontend_functionality.py",
            "test_integration_e2e.py", 
            "test_performance.py",
            "conftest.py"
        ]
        
        for test_file in test_files:
            file_path = test_dir / test_file
            if file_path.exists():
                # Try to compile the file to check syntax
                with open(file_path, 'r') as f:
                    content = f.read()
                
                try:
                    compile(content, str(file_path), 'exec')
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {test_file}: {e}")
    
    def test_pytest_configuration(self):
        """Test pytest configuration files."""
        project_root = Path(__file__).parent.parent
        
        # Check pytest.ini
        pytest_ini = project_root / "pytest.ini"
        if pytest_ini.exists():
            with open(pytest_ini, 'r') as f:
                content = f.read()
                assert "[tool:pytest]" in content or "[pytest]" in content
    
    def test_backend_test_structure(self):
        """Test backend test file structure."""
        test_dir = Path(__file__).parent
        backend_test = test_dir / "test_backend_api.py"
        
        if backend_test.exists():
            with open(backend_test, 'r') as f:
                content = f.read()
            
            # Check for essential test methods
            essential_tests = [
                "test_health_check",
                "test_add_item",
                "test_get_cart",
                "test_checkout"
            ]
            
            for test_name in essential_tests:
                assert test_name in content, f"Backend test {test_name} not found"
    
    def test_frontend_test_structure(self):
        """Test frontend test file structure."""
        test_dir = Path(__file__).parent
        frontend_test = test_dir / "test_frontend_functionality.py"
        
        if frontend_test.exists():
            with open(frontend_test, 'r') as f:
                content = f.read()
            
            # Check for essential frontend tests
            essential_tests = [
                "test_page_load",
                "test_responsive_design",
                "test_add_to_cart"
            ]
            
            for test_name in essential_tests:
                assert test_name in content, f"Frontend test {test_name} not found"
    
    def test_integration_test_structure(self):
        """Test integration test file structure."""
        test_dir = Path(__file__).parent
        integration_test = test_dir / "test_integration_e2e.py"
        
        if integration_test.exists():
            with open(integration_test, 'r') as f:
                content = f.read()
            
            # Check for essential integration tests
            essential_tests = [
                "test_backend_frontend_connectivity",
                "test_complete_shopping_workflow"
            ]
            
            for test_name in essential_tests:
                assert test_name in content, f"Integration test {test_name} not found"
    
    def test_performance_test_structure(self):
        """Test performance test file structure."""
        test_dir = Path(__file__).parent
        performance_test = test_dir / "test_performance.py"
        
        if performance_test.exists():
            with open(performance_test, 'r') as f:
                content = f.read()
            
            # Check for essential performance tests
            essential_tests = [
                "test_response_time",
                "test_concurrent_requests",
                "test_performance"
            ]
            
            found_tests = sum(1 for test in essential_tests if test in content)
            assert found_tests >= 2, "Performance tests should include response time and load testing"
    
    def test_test_imports(self):
        """Test that test files can import required modules."""
        test_dir = Path(__file__).parent
        
        # Test basic imports that should work
        try:
            import pytest
            import requests
            import time
            import uuid
            import json
        except ImportError as e:
            pytest.fail(f"Required module not available: {e}")
    
    def test_project_structure(self):
        """Test overall project structure for testing."""
        project_root = Path(__file__).parent.parent
        
        # Check for essential directories
        essential_dirs = [
            "backend",
            "frontend", 
            "tests"
        ]
        
        for dir_name in essential_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Essential directory {dir_name} not found"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"
    
    def test_backend_structure(self):
        """Test backend application structure."""
        project_root = Path(__file__).parent.parent
        backend_dir = project_root / "backend"
        
        if backend_dir.exists():
            # Check for essential backend files
            essential_files = [
                "app/main.py",
                "requirements.txt"
            ]
            
            for file_path in essential_files:
                full_path = backend_dir / file_path
                if not full_path.exists():
                    print(f"Warning: Backend file {file_path} not found")
    
    def test_frontend_structure(self):
        """Test frontend application structure."""
        project_root = Path(__file__).parent.parent
        frontend_dir = project_root / "frontend"
        
        if frontend_dir.exists():
            # Check for essential frontend files
            essential_files = [
                "package.json",
                "src"
            ]
            
            for file_path in essential_files:
                full_path = frontend_dir / file_path
                if not full_path.exists():
                    print(f"Warning: Frontend file/directory {file_path} not found")
    
    def test_documentation_structure(self):
        """Test documentation structure."""
        project_root = Path(__file__).parent.parent
        
        # Check for documentation files
        doc_files = [
            "README.md",
            "docs"
        ]
        
        for doc_file in doc_files:
            doc_path = project_root / doc_file
            if doc_path.exists():
                if doc_path.is_file():
                    assert doc_path.stat().st_size > 0, f"Documentation file {doc_file} is empty"
    
    def test_test_categories(self):
        """Test that tests are properly categorized."""
        test_dir = Path(__file__).parent
        
        # Define test categories and their expected files
        categories = {
            "backend": ["test_backend_api.py"],
            "frontend": ["test_frontend_functionality.py"],
            "integration": ["test_integration_e2e.py"],
            "performance": ["test_performance.py"]
        }
        
        for category, files in categories.items():
            for file_name in files:
                file_path = test_dir / file_name
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check that file contains appropriate test class
                    class_patterns = [
                        f"class Test{category.title()}",
                        f"class Test{category.upper()}",
                        "class Test"
                    ]
                    
                    has_test_class = any(pattern in content for pattern in class_patterns)
                    assert has_test_class, f"Test file {file_name} should contain a test class"
    
    def test_requirements_files(self):
        """Test that requirements files exist and are valid."""
        project_root = Path(__file__).parent.parent
        
        # Check main requirements
        main_req = project_root / "requirements.txt"
        if main_req.exists():
            with open(main_req, 'r') as f:
                content = f.read()
                assert len(content.strip()) > 0, "Main requirements.txt should not be empty"
        
        # Check backend requirements
        backend_req = project_root / "backend" / "requirements.txt"
        if backend_req.exists():
            with open(backend_req, 'r') as f:
                content = f.read()
                assert len(content.strip()) > 0, "Backend requirements.txt should not be empty"
        
        # Check frontend package.json
        frontend_pkg = project_root / "frontend" / "package.json"
        if frontend_pkg.exists():
            with open(frontend_pkg, 'r') as f:
                try:
                    pkg_data = json.load(f)
                    assert "name" in pkg_data, "package.json should have a name field"
                except json.JSONDecodeError:
                    pytest.fail("Frontend package.json is not valid JSON")
    
    def test_git_structure(self):
        """Test git repository structure."""
        project_root = Path(__file__).parent.parent
        
        # Check for .gitignore
        gitignore = project_root / ".gitignore"
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
                
                # Should ignore common files
                ignore_patterns = ["__pycache__", "*.pyc", "node_modules"]
                for pattern in ignore_patterns:
                    if pattern not in content:
                        print(f"Warning: .gitignore should include {pattern}")
    
    def test_environment_setup(self):
        """Test environment setup files."""
        project_root = Path(__file__).parent.parent
        
        # Check for environment-related files
        env_files = [
            ".env.example",
            "docker-compose.yml",
            "Dockerfile"
        ]
        
        found_env_files = []
        for env_file in env_files:
            if (project_root / env_file).exists():
                found_env_files.append(env_file)
        
        # Should have at least some environment setup
        if not found_env_files:
            print("Warning: No environment setup files found")
    
    def test_test_data_structure(self):
        """Test test data and fixtures structure."""
        test_dir = Path(__file__).parent
        
        # Check conftest.py for fixtures
        conftest = test_dir / "conftest.py"
        if conftest.exists():
            with open(conftest, 'r') as f:
                content = f.read()
            
            # Should have fixture definitions
            fixture_patterns = ["@pytest.fixture", "def pytest_configure"]
            has_fixtures = any(pattern in content for pattern in fixture_patterns)
            assert has_fixtures, "conftest.py should contain pytest fixtures or configuration"
