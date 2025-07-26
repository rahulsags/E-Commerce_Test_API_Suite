# E-commerce API Test Suite

A comprehensive automated testing framework for E-commerce APIs using Python, PyTest, and GitHub Actions. This test suite covers login, cart management, and checkout functionality with positive, negative, and boundary test scenarios.

## 🚀 Features

- **Comprehensive Test Coverage**: Login, Cart, and Checkout functionality
- **Multiple Test Types**: Smoke, Regression, API, Positive, Negative, and Boundary tests
- **Automated Reporting**: HTML reports with pytest-html and JSON reports
- **CI/CD Integration**: GitHub Actions workflow with multiple Python versions
- **Security Testing**: Integrated security scans with Safety and Bandit
- **Performance Testing**: Benchmark tests for performance monitoring
- **Modular Design**: Reusable utilities and helpers for API testing

## 📁 Project Structure

```
ecommerce_api_test_suite/
├── tests/                          # Test files
│   ├── __init__.py
│   ├── test_login.py              # Login functionality tests
│   ├── test_cart.py               # Shopping cart tests
│   └── test_checkout.py           # Checkout process tests
├── data/                          # Test data files
│   └── test_data.json            # JSON test data
├── utils/                         # Utility modules
│   ├── __init__.py
│   └── api_helpers.py            # API client and helper functions
├── reports/                       # Generated test reports
│   └── pytest_report.html       # HTML test report
├── requirements.txt              # Python dependencies
├── pytest.ini                   # PyTest configuration
└── .github/workflows/           # CI/CD workflows
    └── test.yml                 # GitHub Actions workflow
```

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Local Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd ecommerce_api_test_suite
   ```

2. **Create virtual environment** (recommended)

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure test environment**

   Update the `base_url` in `data/test_data.json` to point to your API endpoint:

   ```json
   {
     "base_url": "https://your-api-endpoint.com",
     ...
   }
   ```

## 🧪 Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with HTML report
pytest --html=reports/pytest_report.html --self-contained-html

# Run specific test file
pytest tests/test_login.py

# Run with verbose output
pytest -v
```

### Test Categories

```bash
# Run smoke tests (quick validation)
pytest -m smoke

# Run regression tests (comprehensive)
pytest -m regression

# Run API tests
pytest -m api

# Run positive scenario tests
pytest -m positive

# Run negative scenario tests
pytest -m negative

# Run boundary condition tests
pytest -m boundary

# Run specific functionality tests
pytest -m login
pytest -m cart
pytest -m checkout
```

### Advanced Test Execution

```bash
# Run tests in parallel
pytest -n auto

# Run with coverage report
pytest --cov=utils --cov-report=html

# Run with JSON report
pytest --json-report --json-report-file=reports/report.json

# Run tests and stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

## 📊 Test Reports

The test suite generates multiple types of reports:

### HTML Reports

- **Location**: `reports/pytest_report.html`
- **Features**: Interactive HTML report with test results, logs, and screenshots
- **Usage**: Open in web browser for detailed test analysis

### JSON Reports

- **Location**: `reports/report.json`
- **Features**: Machine-readable test results for integration with other tools
- **Usage**: Parse programmatically for custom reporting

### Coverage Reports

- **Location**: `reports/coverage/`
- **Features**: Code coverage analysis for utility modules
- **Usage**: Identify untested code paths

## 🔧 Configuration

### PyTest Configuration (`pytest.ini`)

The test suite is configured with the following markers:

- `smoke`: Quick validation tests
- `regression`: Comprehensive test coverage
- `api`: API-specific tests
- `login`: Login functionality tests
- `cart`: Shopping cart tests
- `checkout`: Checkout process tests
- `positive`: Positive scenario tests
- `negative`: Negative scenario tests
- `boundary`: Boundary condition tests

### Test Data Configuration (`data/test_data.json`)

Update test data to match your API:

```json
{
  "base_url": "https://your-api-endpoint.com",
  "endpoints": {
    "login": "/auth/login",
    "cart": "/cart",
    "checkout": "/checkout"
  },
  "valid_users": {
    "standard_user": {
      "email": "user@example.com",
      "password": "SecurePass123!"
    }
  }
}
```

## 🤖 CI/CD Integration

### GitHub Actions

The test suite includes a comprehensive GitHub Actions workflow:

**Features:**

- Multi-version Python testing (3.8, 3.9, 3.10, 3.11)
- Multiple test suite execution (smoke, regression, api)
- Code linting and formatting checks
- Security scanning with Safety and Bandit
- Performance testing with pytest-benchmark
- Automated report generation and publishing
- Artifact upload for test reports and logs

**Triggers:**

- Push to main/develop branches
- Pull requests
- Daily scheduled runs
- Manual workflow dispatch

### Configuration

Set up the following in your GitHub repository:

1. **Enable GitHub Pages** for report publishing
2. **Configure branch protection** rules
3. **Set up notifications** for test failures

## 📝 Test Cases Coverage

### Login Tests (`test_login.py`)

- ✅ Valid credential login
- ✅ Invalid email format
- ✅ Empty credentials
- ✅ Wrong password
- ✅ Non-existent user
- ✅ SQL injection protection
- ✅ Email length boundaries
- ✅ Password length boundaries
- ✅ Special characters handling
- ✅ Unicode characters support
- ✅ Case sensitivity
- ✅ Rate limiting
- ✅ Response structure validation
- ✅ Session persistence
- ✅ Logout functionality

### Cart Tests (`test_cart.py`)

- ✅ Add item to cart
- ✅ Add multiple items
- ✅ Update item quantity
- ✅ Remove item from cart
- ✅ Clear entire cart
- ✅ Get cart contents
- ✅ Invalid product handling
- ✅ Zero/negative quantity validation
- ✅ Maximum quantity boundaries
- ✅ Out of stock handling
- ✅ Cart total calculation
- ✅ Session persistence
- ✅ Authentication requirements
- ✅ Malformed request handling

### Checkout Tests (`test_checkout.py`)

- ✅ Initiate checkout process
- ✅ Complete checkout with valid data
- ✅ Multiple items checkout
- ✅ Empty cart validation
- ✅ Invalid shipping address
- ✅ Invalid payment information
- ✅ Expired card handling
- ✅ Invalid card number validation
- ✅ Boundary value testing
- ✅ Authentication requirements
- ✅ Stock validation at checkout
- ✅ Tax calculation
- ✅ Shipping cost calculation
- ✅ Order confirmation
- ✅ Payment processing failure
- ✅ Concurrent request handling
- ✅ Order details retrieval

## 🛡️ Security Testing

The test suite includes security-focused tests:

- **SQL Injection Protection**: Tests for SQL injection vulnerabilities
- **Input Validation**: Validates proper handling of malicious inputs
- **Authentication Testing**: Ensures proper authentication enforcement
- **Rate Limiting**: Tests for brute force protection
- **Data Sanitization**: Validates proper handling of special characters

## 📈 Performance Testing

Integrated performance testing capabilities:

- **Response Time Monitoring**: Tracks API response times
- **Benchmark Tests**: Establishes performance baselines
- **Load Testing**: Validates system behavior under load
- **Resource Usage**: Monitors memory and CPU usage during tests

## 🔍 Debugging and Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   # Solution: Install dependencies
   pip install -r requirements.txt
   ```

2. **API Connection Issues**

   ```bash
   # Solution: Check base_url in test_data.json
   # Ensure API endpoint is accessible
   ```

3. **Authentication Failures**
   ```bash
   # Solution: Verify user credentials in test_data.json
   # Check if test users exist in the system
   ```

### Logging

The test suite provides comprehensive logging:

- **Console Output**: Real-time test execution logs
- **File Logging**: Detailed logs in `test_execution.log`
- **HTTP Request Logging**: API request/response details
- **Error Tracking**: Detailed error information and stack traces

### Debug Mode

Run tests in debug mode for detailed information:

```bash
# Enable debug logging
pytest --log-cli-level=DEBUG

# Run single test for debugging
pytest tests/test_login.py::TestLogin::test_login_valid_credentials -v

# Keep test artifacts for inspection
pytest --keep-duplicates
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-test`
3. **Add tests** following existing patterns
4. **Run test suite**: `pytest`
5. **Update documentation** if needed
6. **Submit pull request**

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where applicable
- Write descriptive test names and docstrings
- Maintain test independence (no test dependencies)
- Use appropriate pytest markers

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues:

1. **Check existing issues** on GitHub
2. **Create new issue** with detailed description
3. **Include test logs** and error messages
4. **Specify environment details** (Python version, OS, etc.)

## 🔄 Maintenance

### Regular Updates

- **Dependencies**: Update requirements.txt monthly
- **Test Data**: Review and update test scenarios quarterly
- **Documentation**: Keep README and docs current
- **Security**: Regular security scans and updates

### Monitoring

- **CI/CD Status**: Monitor GitHub Actions results
- **Test Coverage**: Maintain high test coverage (>90%)
- **Performance**: Track test execution times
- **Reliability**: Monitor test flakiness and stability
