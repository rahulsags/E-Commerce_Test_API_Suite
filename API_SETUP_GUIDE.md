# API Endpoint Configuration Guide

## 🔧 Setting Up Your API Endpoint

The test suite is currently configured to run in "collection mode" in CI/CD to avoid failures when the actual API endpoint is not available. Here's how to configure it for your real API:

## 📝 Configuration Steps

### 1. Update Test Data Configuration

Edit `data/test_data.json`:

```json
{
  "base_url": "https://your-actual-api.com",
  "endpoints": {
    "login": "/api/v1/auth/login",
    "logout": "/api/v1/auth/logout",
    "cart": "/api/v1/cart",
    "checkout": "/api/v1/checkout"
  },
  "valid_users": {
    "standard_user": {
      "email": "your-test-user@example.com",
      "password": "YourTestPassword123!"
    }
  }
}
```

### 2. Create Environment Configuration

Copy `.env.template` to `.env` and update:

```bash
cp .env.template .env
```

Edit `.env`:

```bash
API_BASE_URL=https://your-actual-api.com
TEST_USER_EMAIL=your-test-user@example.com
TEST_USER_PASSWORD=YourTestPassword123!
```

### 3. Enable Real Tests in GitHub Actions

When ready to test against real API, update `.github/workflows/test.yml`:

Replace the collection-only commands:

```yaml
# FROM:
pytest --collect-only -m smoke

# TO:
pytest -m smoke --html=reports/smoke_report.html --self-contained-html -v
```

### 4. Test Locally First

Before enabling in CI, test locally:

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run a single test to verify connection
pytest tests/test_login.py::TestLogin::test_login_valid_credentials -v

# Run smoke tests
pytest -m smoke -v
```

## 🔍 API Requirements

Your API should support:

### Authentication Endpoints

- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Cart Endpoints

- `GET /cart` - Get cart contents
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{id}` - Update item quantity
- `DELETE /cart/items/{id}` - Remove item from cart

### Checkout Endpoints

- `POST /checkout` - Initiate checkout
- `POST /checkout/submit` - Complete checkout
- `GET /orders/{id}` - Get order details

## 📊 Expected Response Formats

### Login Response

```json
{
  "token": "jwt-token-here",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Cart Response

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 29.99,
      "name": "Product Name"
    }
  ],
  "total": 59.98
}
```

### Checkout Response

```json
{
  "order_id": "ORD-123456",
  "status": "confirmed",
  "total": 59.98,
  "items": [...],
  "shipping_address": {...}
}
```

## 🧪 Testing Strategy

1. **Start with Collection Mode**: Verify test structure (`pytest --collect-only`)
2. **Test Individual Endpoints**: Test one endpoint at a time
3. **Run Smoke Tests**: Quick validation of core functionality
4. **Run Full Suite**: Complete test execution
5. **Enable CI/CD**: Update workflow to run real tests

## 🚨 Common Issues

### Authentication Failures

- Verify API credentials in test data
- Check token format and expiration
- Ensure API returns expected response structure

### Connection Issues

- Verify API URL is accessible
- Check network/firewall restrictions
- Validate SSL certificates

### Test Data Issues

- Ensure test users exist in the system
- Verify product IDs are valid
- Check data cleanup between tests

## 🔄 Re-enabling Full Tests

When your API is ready, revert the GitHub Actions workflow:

```bash
# Edit .github/workflows/test.yml
# Replace collection commands with actual test execution
git add .github/workflows/test.yml
git commit -m "Enable full API testing with real endpoint"
git push origin main
```

## 📞 Need Help?

- Check test logs in `test_execution.log`
- Review pytest HTML reports in `reports/`
- Verify API responses match expected formats
- Test individual endpoints with tools like Postman first
