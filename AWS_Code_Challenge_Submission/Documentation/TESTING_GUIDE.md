# CartHub Testing Guide

## Overview

This guide provides comprehensive instructions for testing the CartHub Shopping Cart Application across all architectural patterns (Serverless, ECS Microservices, and EKS Kubernetes).

## Test Suite Architecture

### Test Categories

1. **Backend API Tests** - REST API endpoint validation
2. **Frontend Functionality Tests** - UI/UX and component testing  
3. **Integration E2E Tests** - End-to-end workflow validation
4. **Performance Tests** - Load, stress, and scalability testing
5. **Structure Validation Tests** - Code quality and structure checks

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
cd /Workshop/carthub
source tests/venv/bin/activate
pip install -r tests/requirements.txt

# Install Chrome for frontend testing (Ubuntu/Debian)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable

# Install ChromeDriver
sudo apt install chromium-chromedriver
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/ -m backend -v          # Backend API tests
pytest tests/ -m frontend -v         # Frontend UI tests
pytest tests/ -m integration -v      # E2E integration tests
pytest tests/ -m performance -v      # Performance tests

# Run with coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term -v

# Generate HTML test report
pytest tests/ --html=test-report.html --self-contained-html -v
```

## Test Configuration

### Environment Variables

```bash
# Backend API URL (default: http://localhost:8000)
export API_BASE_URL="http://localhost:8000"

# Frontend URL (default: http://localhost:3000)  
export FRONTEND_URL="http://localhost:3000"

# Test timeout (default: 30 seconds)
export TEST_TIMEOUT=30
```

### Service Requirements

Before running tests, ensure services are running:

```bash
# Backend service (FastAPI)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend service (React)
cd frontend  
npm start
```

## Test Details

### Backend API Tests (`test_backend_api.py`)

Tests all REST API endpoints with comprehensive validation:

**Health Check Tests:**
- `test_health_check_endpoint()` - Validates health endpoint response
- `test_readiness_check_endpoint()` - Kubernetes readiness probe
- `test_liveness_check_endpoint()` - Kubernetes liveness probe

**Cart Operations:**
- `test_add_item_to_cart_success()` - Add items with valid data
- `test_add_item_invalid_price()` - Validation error handling
- `test_get_cart_success()` - Retrieve cart contents
- `test_update_item_quantity_success()` - Update item quantities
- `test_remove_item_from_cart_success()` - Remove items
- `test_clear_cart_success()` - Clear entire cart

**Checkout Process:**
- `test_checkout_success()` - Complete checkout workflow
- `test_checkout_empty_cart()` - Empty cart validation

**Advanced Scenarios:**
- `test_concurrent_cart_operations()` - Multi-user operations
- `test_api_response_time()` - Performance validation
- `test_add_multiple_quantities()` - Parameterized testing

### Frontend Functionality Tests (`test_frontend_functionality.py`)

Comprehensive UI/UX testing using Selenium WebDriver:

**Page Load and Performance:**
- `test_page_load_performance()` - Page load time < 5 seconds
- `test_page_title_and_structure()` - Basic page structure
- `test_javascript_functionality()` - JS execution validation
- `test_css_styling_loaded()` - CSS loading verification

**Responsive Design:**
- `test_responsive_design()` - Multi-device compatibility
  - Desktop: 1920x1080
  - Tablet: 1024x768  
  - Mobile: 375x667

**User Interactions:**
- `test_add_to_cart_functionality()` - Add to cart buttons
- `test_cart_display_functionality()` - Cart content display
- `test_quantity_update_functionality()` - Quantity controls
- `test_remove_item_functionality()` - Remove item buttons
- `test_checkout_button_presence()` - Checkout workflow

**Accessibility:**
- `test_accessibility_features()` - WCAG compliance checks
- Alt text validation for images
- Form label associations
- Proper heading structure

### Integration E2E Tests (`test_integration_e2e.py`)

End-to-end workflow testing across frontend and backend:

**Service Connectivity:**
- `test_backend_frontend_connectivity()` - Service communication
- `test_api_cors_configuration()` - CORS validation

**Complete Workflows:**
- `test_complete_shopping_workflow_api()` - Full cart workflow:
  1. Start with empty cart
  2. Add multiple items
  3. Update quantities
  4. Remove items
  5. Complete checkout
  6. Verify cart cleared

**Data Integrity:**
- `test_data_persistence_across_requests()` - Session persistence
- `test_database_transaction_integrity()` - ACID compliance
- `test_concurrent_user_operations()` - Multi-user isolation

**Error Handling:**
- `test_error_handling_workflow()` - Cross-layer error propagation

### Performance Tests (`test_performance.py`)

Comprehensive performance and scalability testing:

**Response Time Testing:**
- `test_health_check_response_time()` - < 0.5s average
- `test_add_item_response_time()` - < 0.2s average
- `test_get_cart_response_time()` - Scalable with cart size

**Load Testing:**
- `test_concurrent_requests_performance()` - 10+ concurrent threads
- `test_database_performance_under_load()` - Sustained operations
- `test_api_rate_limiting_behavior()` - Rate limiting validation

**Scalability Testing:**
- `test_large_cart_performance()` - 100+ items per cart
- `test_memory_usage_stability()` - Memory leak detection
- `test_checkout_performance()` - Checkout operation timing

**Performance Benchmarks:**
```
Health Check: < 0.5s average response time
Add Item: < 0.2s average response time
Concurrent Load: 95%+ success rate
Large Cart Retrieval: < 1.0s
Database Throughput: > 10 operations/second
```

## Test Data Management

### Fixtures and Test Data

The test suite uses pytest fixtures for consistent test data:

```python
@pytest.fixture
def unique_customer_id():
    """Generate unique customer ID for each test."""
    return f"test-customer-{uuid.uuid4().hex[:12]}"

@pytest.fixture  
def sample_product():
    """Sample product data for testing."""
    return {
        "product_id": f"test-product-{uuid.uuid4().hex[:8]}",
        "product_name": "Test Product",
        "price": "99.99", 
        "quantity": 1
    }

@pytest.fixture
def clean_cart(api_base_url, unique_customer_id):
    """Ensure cart is clean before and after test."""
    # Cleanup logic
```

### Data Isolation

- Each test uses unique customer IDs
- Automatic cleanup after test completion
- No shared state between tests
- Concurrent test execution support

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tests/requirements.txt
    
    - name: Start services
      run: |
        # Start backend
        cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        
        # Start frontend  
        cd frontend && npm install && npm start &
        
        # Wait for services
        sleep 30
    
    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml --junitxml=test-results.xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pip install -r tests/requirements.txt'
            }
        }
        
        stage('Start Services') {
            parallel {
                stage('Backend') {
                    steps {
                        sh 'cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &'
                    }
                }
                stage('Frontend') {
                    steps {
                        sh 'cd frontend && npm install && npm start &'
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                sh 'pytest tests/ --junitxml=test-results.xml --cov=. --cov-report=xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }
}
```

## Troubleshooting

### Common Issues

**1. Chrome/ChromeDriver Issues**
```bash
# Install Chrome
sudo apt update
sudo apt install google-chrome-stable

# Install ChromeDriver
sudo apt install chromium-chromedriver

# Or download manually
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
```

**2. Service Connection Issues**
```bash
# Check if services are running
curl http://localhost:8000/health/
curl http://localhost:3000

# Check port availability
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
```

**3. Database Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
psql -h localhost -U postgres -d shopping_cart -c "SELECT 1;"
```

**4. Permission Issues**
```bash
# Fix Chrome sandbox issues
google-chrome --no-sandbox --disable-dev-shm-usage

# Fix file permissions
chmod +x tests/run_tests.sh
```

### Debug Mode

Enable debug logging for detailed test output:

```bash
# Set debug environment
export PYTEST_DEBUG=1
export LOG_LEVEL=DEBUG

# Run with verbose output
pytest tests/ -v -s --tb=long

# Run single test with debugging
pytest tests/test_backend_api.py::TestBackendAPI::test_add_item_to_cart_success -v -s
```

## Test Reporting

### Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html

# Generate terminal coverage report
pytest tests/ --cov=. --cov-report=term-missing
```

### Performance Reports

```bash
# Run performance tests with timing
pytest tests/test_performance.py -v --durations=10

# Generate performance benchmark report
pytest tests/test_performance.py --benchmark-only --benchmark-json=benchmark.json
```

### Test Result Formats

```bash
# JUnit XML (for CI/CD)
pytest tests/ --junitxml=test-results.xml

# HTML report
pytest tests/ --html=test-report.html --self-contained-html

# JSON report
pytest tests/ --json-report --json-report-file=test-report.json
```

## Best Practices

### Test Writing Guidelines

1. **Test Isolation:** Each test should be independent
2. **Descriptive Names:** Use clear, descriptive test method names
3. **Single Responsibility:** One assertion per test when possible
4. **Data Cleanup:** Always clean up test data
5. **Error Handling:** Test both success and failure scenarios

### Performance Testing Guidelines

1. **Baseline Metrics:** Establish performance baselines
2. **Realistic Load:** Use realistic user scenarios
3. **Resource Monitoring:** Monitor CPU, memory, and database
4. **Gradual Load:** Increase load gradually
5. **Failure Analysis:** Analyze failure points and bottlenecks

### Maintenance Guidelines

1. **Regular Updates:** Keep test dependencies updated
2. **Test Review:** Regular review of test effectiveness
3. **Flaky Test Management:** Identify and fix unstable tests
4. **Documentation:** Keep test documentation current
5. **Metrics Tracking:** Track test execution metrics over time

## Advanced Testing

### Contract Testing

```python
# API contract validation using OpenAPI
def test_api_contract_compliance():
    spec = load_openapi_spec("api-spec.yaml")
    validate_response_against_spec(response, spec)
```

### Security Testing

```python
# SQL injection testing
def test_sql_injection_protection():
    malicious_input = "'; DROP TABLE carts; --"
    response = add_item_with_product_name(malicious_input)
    assert response.status_code != 500
```

### Chaos Testing

```python
# Network failure simulation
def test_network_resilience():
    with network_partition():
        response = make_api_request()
        assert response.status_code in [200, 503, 504]
```

## Resources

### Documentation Links
- [Pytest Documentation](https://docs.pytest.org/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

### Tools and Libraries
- **pytest** - Test framework
- **selenium** - Web browser automation
- **requests** - HTTP client library
- **pytest-cov** - Coverage reporting
- **pytest-html** - HTML test reports
- **pytest-xdist** - Parallel test execution

### Community Resources
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [API Testing Guide](https://assertible.com/blog/api-testing-guide)
- [Frontend Testing Strategies](https://kentcdodds.com/blog/write-tests)

---

**Last Updated:** August 21, 2025  
**Version:** 2.0.0  
**Maintainer:** QA Team
