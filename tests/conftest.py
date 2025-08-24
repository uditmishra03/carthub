"""
Pytest configuration and shared fixtures for shopping cart tests
"""

import pytest
import requests
import time
import uuid
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "frontend: marks tests as frontend tests"
    )
    config.addinivalue_line(
        "markers", "backend: marks tests as backend API tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for backend API."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def frontend_url():
    """Base URL for frontend application."""
    return os.getenv("FRONTEND_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def test_timeout():
    """Default timeout for test operations."""
    return 30


@pytest.fixture(scope="session")
def wait_for_services(api_base_url, frontend_url):
    """Wait for backend and frontend services to be available."""
    max_retries = 30
    retry_delay = 2
    
    # Wait for backend
    for i in range(max_retries):
        try:
            response = requests.get(f"{api_base_url}/health/", timeout=5)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        
        if i == max_retries - 1:
            pytest.skip(f"Backend service not available at {api_base_url}")
        
        time.sleep(retry_delay)
    
    # Wait for frontend
    for i in range(max_retries):
        try:
            response = requests.get(frontend_url, timeout=5)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        
        if i == max_retries - 1:
            pytest.skip(f"Frontend service not available at {frontend_url}")
        
        time.sleep(retry_delay)
    
    return True


@pytest.fixture(scope="function")
def unique_customer_id():
    """Generate unique customer ID for each test."""
    return f"test-customer-{uuid.uuid4().hex[:12]}"


@pytest.fixture(scope="function")
def sample_product():
    """Sample product data for testing."""
    return {
        "product_id": f"test-product-{uuid.uuid4().hex[:8]}",
        "product_name": "Test Product",
        "price": "99.99",
        "quantity": 1
    }


@pytest.fixture(scope="function")
def chrome_driver():
    """Chrome WebDriver for frontend testing."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    except Exception as e:
        pytest.skip(f"Chrome WebDriver not available: {str(e)}")


@pytest.fixture(scope="function")
def clean_cart(api_base_url, unique_customer_id):
    """Ensure cart is clean before and after test."""
    # Clean before test
    try:
        requests.delete(f"{api_base_url}/api/v1/cart/{unique_customer_id}")
    except:
        pass
    
    yield unique_customer_id
    
    # Clean after test
    try:
        requests.delete(f"{api_base_url}/api/v1/cart/{unique_customer_id}")
    except:
        pass


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file names."""
    for item in items:
        # Add markers based on test file names
        if "test_backend" in item.fspath.basename:
            item.add_marker(pytest.mark.backend)
        elif "test_frontend" in item.fspath.basename:
            item.add_marker(pytest.mark.frontend)
        elif "test_integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        elif "test_performance" in item.fspath.basename:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def test_environment_check():
    """Check test environment before running tests."""
    # Check if required environment variables are set
    required_env_vars = []  # Add any required env vars here
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        pytest.skip(f"Missing required environment variables: {missing_vars}")


# Pytest hooks for better test reporting
def pytest_runtest_setup(item):
    """Setup hook for each test."""
    # Add any per-test setup here
    pass


def pytest_runtest_teardown(item, nextitem):
    """Teardown hook for each test."""
    # Add any per-test cleanup here
    pass


# Custom pytest markers for test categorization
pytestmark = [
    pytest.mark.filterwarnings("ignore::urllib3.exceptions.InsecureRequestWarning"),
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]
