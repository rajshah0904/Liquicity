# Python Backend Testing Guide

This guide covers how to test the Python backend for the Liquicity Bridge crypto payment system.

## 🚀 Quick Start

### Prerequisites

1. **Python Environment**: Ensure you have Python 3.10+ installed
2. **Virtual Environment**: Activate your virtual environment
3. **Dependencies**: Install all required packages

```bash
# Navigate to the backend directory
cd python_backend

# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r test_requirements.txt
```

### Run All Tests

```bash
# Option 1: Use the test runner script
python run_tests.py

# Option 2: Use pytest directly
pytest tests/ -v --cov=core --cov=api --cov-report=html
```

## 📋 Test Structure

```
python_backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── test_security.py         # Security module tests
│   ├── test_bridge_api_client.py # Bridge API client tests
│   ├── test_usdc_payment_service.py # USDC payment service tests
│   ├── test_walletconnect_v2_service.py # WalletConnect v2 tests
│   └── test_api_routes.py       # FastAPI route tests
├── test_requirements.txt        # Test dependencies
├── pytest.ini                  # Pytest configuration
└── run_tests.py                # Test runner script
```

## 🧪 Test Categories

### 1. Unit Tests (`-m unit`)
- **Purpose**: Test individual functions and classes in isolation
- **Coverage**: Core business logic, data validation, utility functions
- **Speed**: Fast execution (< 1 second per test)

### 2. Security Tests (`-m security`)
- **Purpose**: Test authentication, authorization, and security features
- **Coverage**: JWT tokens, password hashing, risk scoring, fraud detection
- **Speed**: Fast execution

### 3. API Tests (`-m api`)
- **Purpose**: Test FastAPI endpoints and HTTP responses
- **Coverage**: Route handlers, request/response validation, error handling
- **Speed**: Medium execution

### 4. Integration Tests (`-m integration`)
- **Purpose**: Test component interactions and end-to-end flows
- **Coverage**: Service integration, database operations, external API calls
- **Speed**: Slower execution (may involve network calls)

### 5. Slow Tests (`-m slow`)
- **Purpose**: Tests that take longer to execute
- **Coverage**: Network operations, complex scenarios
- **Speed**: Slow execution (> 5 seconds per test)

## 🔧 Running Specific Tests

### Run by Category
```bash
# Unit tests only
pytest tests/ -m unit

# Security tests only
pytest tests/ -m security

# API tests only
pytest tests/ -m api

# Integration tests only
pytest tests/ -m integration

# Exclude slow tests
pytest tests/ -m "not slow"
```

### Run by File
```bash
# Test specific module
pytest tests/test_security.py

# Test specific class
pytest tests/test_security.py::TestAuthentication

# Test specific function
pytest tests/test_security.py::TestAuthentication::test_hash_password
```

### Run with Coverage
```bash
# Basic coverage
pytest tests/ --cov=core --cov=api

# Detailed coverage report
pytest tests/ --cov=core --cov=api --cov-report=term-missing --cov-report=html

# Coverage threshold (fail if below 80%)
pytest tests/ --cov=core --cov=api --cov-fail-under=80
```

## 🛠️ Test Configuration

### Pytest Configuration (`pytest.ini`)
- **Test Discovery**: Automatically finds test files
- **Coverage**: Generates HTML and XML reports
- **Markers**: Defines test categories
- **Async Support**: Handles async/await tests

### Test Fixtures (`conftest.py`)
- **Mock Services**: Pre-configured mocks for external dependencies
- **Test Data**: Sample data for testing
- **Database**: Test database setup/teardown
- **Authentication**: Mock user contexts

## 📊 Coverage Reports

### HTML Report
```bash
pytest tests/ --cov=core --cov=api --cov-report=html
# Open htmlcov/index.html in your browser
```

### Terminal Report
```bash
pytest tests/ --cov=core --cov=api --cov-report=term-missing
```

### XML Report (for CI/CD)
```bash
pytest tests/ --cov=core --cov=api --cov-report=xml
```

## 🔍 Code Quality Checks

### Linting
```bash
# Flake8 (style and error checking)
flake8 core api tests --max-line-length=100

# Black (code formatting)
black --check core api tests

# isort (import sorting)
isort --check-only core api tests
```

### Type Checking
```bash
# MyPy type checking
mypy core api
```

## 🧪 Writing Tests

### Test File Structure
```python
"""
Tests for the [module_name] module
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from core.module_name import ClassName, function_name

class TestClassName:
    """Test ClassName class"""
    
    @pytest.fixture
    def instance(self):
        """Create test instance"""
        return ClassName()
    
    def test_method_success(self, instance):
        """Test successful method execution"""
        result = instance.method()
        assert result == expected_value
    
    @pytest.mark.asyncio
    async def test_async_method_success(self, instance):
        """Test successful async method execution"""
        result = await instance.async_method()
        assert result == expected_value
    
    def test_method_failure(self, instance):
        """Test method failure handling"""
        with pytest.raises(ValueError) as exc_info:
            instance.method(invalid_input)
        assert "error message" in str(exc_info.value)
```

### Test Markers
```python
@pytest.mark.unit
def test_unit_function():
    """Unit test"""
    pass

@pytest.mark.security
def test_security_function():
    """Security test"""
    pass

@pytest.mark.api
def test_api_endpoint():
    """API test"""
    pass

@pytest.mark.integration
def test_integration_flow():
    """Integration test"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow test"""
    pass
```

### Mocking External Dependencies
```python
@patch('module.external_service')
def test_with_mock(mock_service):
    """Test with mocked external service"""
    mock_service.return_value = "mocked_result"
    result = function_under_test()
    assert result == "mocked_result"

@pytest.mark.asyncio
async def test_async_with_mock():
    """Test async function with mock"""
    with patch('module.async_service', new_callable=AsyncMock) as mock_service:
        mock_service.return_value = "mocked_result"
        result = await async_function_under_test()
        assert result == "mocked_result"
```

## 🚨 Common Issues & Solutions

### Import Errors
```bash
# Add the backend directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# or
python -m pytest tests/
```

### Async Test Issues
```python
# Use pytest-asyncio for async tests
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Database Connection Issues
```python
# Use test database or mocks
@pytest.fixture
def mock_db():
    with patch('module.database') as mock:
        yield mock
```

### Network Timeout Issues
```python
# Mock external API calls
@patch('module.external_api_call')
def test_without_network(mock_api):
    mock_api.return_value = {"success": True}
    # Test continues without network
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Python Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r test_requirements.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=core --cov=api --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 🎯 Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Test Data
- Use fixtures for reusable test data
- Create realistic test scenarios
- Avoid hardcoded values

### 3. Mocking
- Mock external dependencies
- Use appropriate mock types (AsyncMock for async)
- Verify mock calls when relevant

### 4. Assertions
- Use specific assertions
- Test both success and failure cases
- Check error messages and types

### 5. Performance
- Keep tests fast
- Use appropriate markers for slow tests
- Mock expensive operations

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Async Documentation](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

## 🆘 Getting Help

If you encounter issues:

1. Check the test output for specific error messages
2. Verify your Python environment and dependencies
3. Ensure you're in the correct directory
4. Check the test configuration in `pytest.ini`
5. Review the test fixtures in `conftest.py`

For additional support, refer to the main project documentation or create an issue in the repository. 