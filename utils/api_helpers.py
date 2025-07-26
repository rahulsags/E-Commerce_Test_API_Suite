"""
API Helper utilities for E-commerce test suite.
Provides common functionality for API testing including authentication,
request handling, and response validation.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:
    """Main API client for handling HTTP requests with authentication and retry logic."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.auth_token = None
        self.logger = logging.getLogger(__name__)
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'EcommerceTestSuite/1.0'
        })

    def set_auth_token(self, token: str) -> None:
        """Set authentication token for requests."""
        self.auth_token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
        self.logger.info("Authentication token set")

    def clear_auth_token(self) -> None:
        """Clear authentication token."""
        self.auth_token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        self.logger.info("Authentication token cleared")

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with error handling and logging.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        
        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
            
        # Log request details
        self.logger.info(f"Making {method} request to: {url}")
        if 'json' in kwargs:
            self.logger.debug(f"Request payload: {kwargs['json']}")
            
        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.info(f"Response status: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request."""
        return self.request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PUT request."""
        return self.request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        return self.request('DELETE', endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PATCH request."""
        return self.request('PATCH', endpoint, **kwargs)


class AuthHelper:
    """Helper class for authentication operations."""
    
    def __init__(self, api_client: APIClient, login_endpoint: str = '/auth/login'):
        self.api_client = api_client
        self.login_endpoint = login_endpoint
        self.logger = logging.getLogger(__name__)

    def login(self, email: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Perform user login.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, response_data)
        """
        payload = {
            'email': email,
            'password': password
        }
        
        try:
            response = self.api_client.post(self.login_endpoint, json=payload)
            response_data = response.json() if response.content else {}
            
            if response.status_code == 200 and 'token' in response_data:
                self.api_client.set_auth_token(response_data['token'])
                self.logger.info(f"Login successful for user: {email}")
                return True, response_data
            else:
                self.logger.warning(f"Login failed for user: {email}")
                return False, response_data
                
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False, {'error': str(e)}

    def logout(self, logout_endpoint: str = '/auth/logout') -> bool:
        """
        Perform user logout.
        
        Args:
            logout_endpoint: Logout API endpoint
            
        Returns:
            Success status
        """
        try:
            response = self.api_client.post(logout_endpoint)
            self.api_client.clear_auth_token()
            self.logger.info("Logout successful")
            return response.status_code in [200, 204]
        except Exception as e:
            self.logger.error(f"Logout error: {str(e)}")
            return False


class ResponseValidator:
    """Helper class for validating API responses."""
    
    @staticmethod
    def validate_status_code(response: requests.Response, expected_status: int) -> bool:
        """Validate response status code."""
        return response.status_code == expected_status

    @staticmethod
    def validate_json_response(response: requests.Response) -> bool:
        """Validate that response contains valid JSON."""
        try:
            response.json()
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def validate_response_schema(response: requests.Response, required_fields: list) -> bool:
        """
        Validate that response contains required fields.
        
        Args:
            response: HTTP response object
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present
        """
        try:
            data = response.json()
            return all(field in data for field in required_fields)
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def validate_error_response(response: requests.Response) -> bool:
        """Validate error response format."""
        if response.status_code >= 400:
            try:
                data = response.json()
                return 'error' in data or 'message' in data
            except json.JSONDecodeError:
                return False
        return True


class TestDataLoader:
    """Helper class for loading test data."""
    
    @staticmethod
    def load_test_data(file_path: str = None) -> Dict[str, Any]:
        """
        Load test data from JSON file.
        
        Args:
            file_path: Path to test data file
            
        Returns:
            Test data dictionary
        """
        if file_path is None:
            # Default path relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(os.path.dirname(current_dir), 'data', 'test_data.json')
        
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error(f"Test data file not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in test data file: {file_path}")
            return {}

    @staticmethod
    def get_user_data(user_type: str, file_path: str = None) -> Dict[str, Any]:
        """Get user data by type."""
        test_data = TestDataLoader.load_test_data(file_path)
        return test_data.get('valid_users', {}).get(user_type, {})

    @staticmethod
    def get_product_data(product_type: str, file_path: str = None) -> Dict[str, Any]:
        """Get product data by type."""
        test_data = TestDataLoader.load_test_data(file_path)
        return test_data.get('products', {}).get(product_type, {})


class CartHelper:
    """Helper class for cart operations."""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    def add_item_to_cart(self, product_id: int, quantity: int, 
                        cart_endpoint: str = '/cart/items') -> requests.Response:
        """Add item to cart."""
        payload = {
            'product_id': product_id,
            'quantity': quantity
        }
        return self.api_client.post(cart_endpoint, json=payload)

    def remove_item_from_cart(self, product_id: int, 
                             cart_endpoint: str = '/cart/items') -> requests.Response:
        """Remove item from cart."""
        return self.api_client.delete(f"{cart_endpoint}/{product_id}")

    def update_cart_item(self, product_id: int, quantity: int, 
                        cart_endpoint: str = '/cart/items') -> requests.Response:
        """Update cart item quantity."""
        payload = {'quantity': quantity}
        return self.api_client.put(f"{cart_endpoint}/{product_id}", json=payload)

    def get_cart_contents(self, cart_endpoint: str = '/cart') -> requests.Response:
        """Get current cart contents."""
        return self.api_client.get(cart_endpoint)

    def clear_cart(self, cart_endpoint: str = '/cart') -> requests.Response:
        """Clear all items from cart."""
        return self.api_client.delete(cart_endpoint)


class CheckoutHelper:
    """Helper class for checkout operations."""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    def initiate_checkout(self, checkout_endpoint: str = '/checkout') -> requests.Response:
        """Initiate checkout process."""
        return self.api_client.post(checkout_endpoint)

    def submit_checkout(self, shipping_address: Dict[str, Any], 
                       payment_info: Dict[str, Any], 
                       checkout_endpoint: str = '/checkout') -> requests.Response:
        """Submit checkout with shipping and payment info."""
        payload = {
            'shipping_address': shipping_address,
            'payment_info': payment_info
        }
        return self.api_client.post(f"{checkout_endpoint}/submit", json=payload)

    def get_order_summary(self, order_id: str, 
                         orders_endpoint: str = '/orders') -> requests.Response:
        """Get order summary by ID."""
        return self.api_client.get(f"{orders_endpoint}/{order_id}")


# Utility functions
def setup_logging(level: str = 'INFO') -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_execution.log')
        ]
    )


def generate_test_email() -> str:
    """Generate unique test email."""
    import time
    timestamp = int(time.time())
    return f"test_user_{timestamp}@example.com"


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: list = None) -> Dict[str, Any]:
    """Mask sensitive data in logs."""
    if sensitive_fields is None:
        sensitive_fields = ['password', 'token', 'card_number', 'cvv']
    
    masked_data = data.copy()
    for field in sensitive_fields:
        if field in masked_data:
            masked_data[field] = '*' * len(str(masked_data[field]))
    
    return masked_data
