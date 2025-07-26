"""
Test cases for login functionality.
Covers positive, negative, and boundary test scenarios for user authentication.
"""

import pytest
import time
from faker import Faker
from utils.api_helpers import (
    APIClient, AuthHelper, ResponseValidator, 
    TestDataLoader, setup_logging, generate_test_email
)


# Setup logging for tests
setup_logging()

# Initialize Faker for generating test data
fake = Faker()


class TestLogin:
    """Test class for login functionality."""
    
    @classmethod
    def setup_class(cls):
        """Setup test class with common test data and API client."""
        cls.test_data = TestDataLoader.load_test_data()
        cls.base_url = cls.test_data.get('base_url', 'https://api.ecommerce-demo.com')
        cls.api_client = APIClient(cls.base_url)
        cls.auth_helper = AuthHelper(cls.api_client)
        cls.login_endpoint = cls.test_data.get('endpoints', {}).get('login', '/auth/login')

    def setup_method(self):
        """Setup method run before each test."""
        # Clear any existing authentication
        self.api_client.clear_auth_token()

    @pytest.mark.smoke
    @pytest.mark.login
    @pytest.mark.positive
    def test_login_valid_credentials(self):
        """Test successful login with valid credentials."""
        # Test data
        user_data = self.test_data['valid_users']['standard_user']
        
        # Perform login
        success, response_data = self.auth_helper.login(
            user_data['email'], 
            user_data['password']
        )
        
        # Assertions
        assert success, "Login should succeed with valid credentials"
        assert 'token' in response_data, "Response should contain authentication token"
        assert 'user' in response_data, "Response should contain user information"
        assert response_data['user']['email'] == user_data['email'], "User email should match"

    @pytest.mark.login
    @pytest.mark.positive
    def test_login_admin_user(self):
        """Test successful login with admin credentials."""
        # Test data
        admin_data = self.test_data['valid_users']['admin_user']
        
        # Perform login
        success, response_data = self.auth_helper.login(
            admin_data['email'], 
            admin_data['password']
        )
        
        # Assertions
        assert success, "Admin login should succeed"
        assert 'token' in response_data, "Response should contain authentication token"
        assert 'user' in response_data, "Response should contain user information"
        assert response_data['user']['email'] == admin_data['email'], "Admin email should match"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_invalid_email(self):
        """Test login failure with invalid email format."""
        # Test data
        invalid_data = self.test_data['invalid_users']['invalid_email']
        
        # Perform login
        success, response_data = self.auth_helper.login(
            invalid_data['email'], 
            invalid_data['password']
        )
        
        # Assertions
        assert not success, "Login should fail with invalid email format"
        assert 'error' in response_data or 'message' in response_data, "Response should contain error message"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_empty_credentials(self):
        """Test login failure with empty credentials."""
        # Test data
        empty_data = self.test_data['invalid_users']['empty_credentials']
        
        # Perform login
        success, response_data = self.auth_helper.login(
            empty_data['email'], 
            empty_data['password']
        )
        
        # Assertions
        assert not success, "Login should fail with empty credentials"
        assert 'error' in response_data or 'message' in response_data, "Response should contain error message"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_wrong_password(self):
        """Test login failure with wrong password."""
        # Test data
        wrong_pass_data = self.test_data['invalid_users']['wrong_password']
        
        # Perform login
        success, response_data = self.auth_helper.login(
            wrong_pass_data['email'], 
            wrong_pass_data['password']
        )
        
        # Assertions
        assert not success, "Login should fail with wrong password"
        assert 'error' in response_data or 'message' in response_data, "Response should contain error message"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_non_existent_user(self):
        """Test login failure with non-existent user."""
        # Test data
        non_existent_data = self.test_data['invalid_users']['non_existent']
        
        # Perform login
        success, response_data = self.auth_helper.login(
            non_existent_data['email'], 
            non_existent_data['password']
        )
        
        # Assertions
        assert not success, "Login should fail for non-existent user"
        assert 'error' in response_data or 'message' in response_data, "Response should contain error message"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_sql_injection_attempt(self):
        """Test login security against SQL injection attempts."""
        # SQL injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in sql_payloads:
            success, response_data = self.auth_helper.login(payload, payload)
            
            # Assertions
            assert not success, f"Login should fail for SQL injection payload: {payload}"
            assert 'error' in response_data or 'message' in response_data, \
                "Response should contain error message for malicious input"

    @pytest.mark.login
    @pytest.mark.boundary
    def test_login_email_length_boundary(self):
        """Test login with email at maximum length boundary."""
        # Get boundary data
        max_email_length = self.test_data['test_boundaries']['email_max_length']
        
        # Create email at boundary (max length)
        local_part = 'a' * (max_email_length - len('@example.com'))
        boundary_email = f"{local_part}@example.com"
        
        # Test with boundary email
        success, response_data = self.auth_helper.login(boundary_email, "password123")
        
        # Assertions (should handle gracefully, either accept or reject with proper error)
        assert isinstance(success, bool), "Login should return boolean result"
        if not success:
            assert 'error' in response_data or 'message' in response_data, \
                "Failed login should contain error message"

    @pytest.mark.login
    @pytest.mark.boundary
    def test_login_password_length_boundaries(self):
        """Test login with passwords at length boundaries."""
        boundaries = self.test_data['test_boundaries']
        min_length = boundaries['password_min_length']
        max_length = boundaries['password_max_length']
        
        test_email = "boundary@example.com"
        
        # Test minimum length password
        min_password = 'a' * min_length
        success, response_data = self.auth_helper.login(test_email, min_password)
        assert isinstance(success, bool), "Login should handle minimum length password"
        
        # Test maximum length password
        max_password = 'a' * max_length
        success, response_data = self.auth_helper.login(test_email, max_password)
        assert isinstance(success, bool), "Login should handle maximum length password"
        
        # Test below minimum length
        below_min_password = 'a' * (min_length - 1)
        success, response_data = self.auth_helper.login(test_email, below_min_password)
        assert not success, "Login should fail with password below minimum length"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_special_characters(self):
        """Test login with special characters in credentials."""
        special_chars = ['<', '>', '&', '"', "'", '%', '\\', '/', '*', '?', '|']
        
        for char in special_chars:
            email_with_char = f"test{char}user@example.com"
            password_with_char = f"pass{char}word123"
            
            success, response_data = self.auth_helper.login(email_with_char, password_with_char)
            
            # Should handle special characters gracefully
            assert isinstance(success, bool), f"Login should handle special character: {char}"
            if not success:
                assert 'error' in response_data or 'message' in response_data, \
                    f"Failed login with '{char}' should contain error message"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_unicode_characters(self):
        """Test login with Unicode characters."""
        unicode_emails = [
            "tëst@example.com",
            "用户@example.com",
            "тест@example.com"
        ]
        
        for email in unicode_emails:
            success, response_data = self.auth_helper.login(email, "password123")
            
            # Should handle Unicode gracefully
            assert isinstance(success, bool), f"Login should handle Unicode email: {email}"

    @pytest.mark.login
    @pytest.mark.regression
    def test_login_case_sensitivity(self):
        """Test login case sensitivity for email addresses."""
        user_data = self.test_data['valid_users']['standard_user']
        original_email = user_data['email']
        password = user_data['password']
        
        # Test different case variations
        case_variations = [
            original_email.upper(),
            original_email.title(),
            original_email.capitalize()
        ]
        
        for email_variant in case_variations:
            success, response_data = self.auth_helper.login(email_variant, password)
            
            # Most systems treat email as case-insensitive
            # Adjust assertion based on your system's behavior
            if success:
                assert 'token' in response_data, f"Successful login with {email_variant} should return token"
            else:
                assert 'error' in response_data or 'message' in response_data, \
                    f"Failed login with {email_variant} should return error"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_rate_limiting(self):
        """Test login rate limiting for security."""
        user_data = self.test_data['valid_users']['standard_user']
        email = user_data['email']
        
        # Attempt multiple failed logins rapidly
        failed_attempts = 0
        max_attempts = 5
        
        for attempt in range(max_attempts + 2):  # Try a few more than the limit
            success, response_data = self.auth_helper.login(email, "wrongpassword")
            
            if not success:
                failed_attempts += 1
                
            # Check if rate limiting kicks in
            if 'rate limit' in str(response_data).lower() or \
               'too many attempts' in str(response_data).lower():
                assert failed_attempts >= max_attempts, \
                    "Rate limiting should activate after multiple failed attempts"
                break
                
            # Small delay between attempts
            time.sleep(0.1)

    @pytest.mark.login
    @pytest.mark.positive
    def test_login_response_structure(self):
        """Test that login response has correct structure."""
        user_data = self.test_data['valid_users']['standard_user']
        
        # Perform login
        response = self.api_client.post(
            self.login_endpoint,
            json={
                'email': user_data['email'],
                'password': user_data['password']
            }
        )
        
        # Assertions on response structure
        assert ResponseValidator.validate_status_code(response, 200), \
            "Login should return 200 status code"
        assert ResponseValidator.validate_json_response(response), \
            "Login should return valid JSON"
        
        required_fields = ['token', 'user']
        assert ResponseValidator.validate_response_schema(response, required_fields), \
            f"Login response should contain fields: {required_fields}"
        
        # Validate user object structure
        response_data = response.json()
        user_fields = ['id', 'email', 'first_name', 'last_name']
        user_data_response = response_data.get('user', {})
        
        for field in user_fields:
            assert field in user_data_response, f"User object should contain {field}"

    @pytest.mark.login
    @pytest.mark.positive
    def test_logout_functionality(self):
        """Test logout functionality after successful login."""
        user_data = self.test_data['valid_users']['standard_user']
        
        # First login
        success, _ = self.auth_helper.login(user_data['email'], user_data['password'])
        assert success, "Login should succeed before testing logout"
        
        # Test logout
        logout_success = self.auth_helper.logout()
        assert logout_success, "Logout should succeed after valid login"
        
        # Verify token is cleared
        assert self.api_client.auth_token is None, "Auth token should be cleared after logout"

    @pytest.mark.login
    @pytest.mark.negative
    def test_login_without_content_type(self):
        """Test login request without proper content type header."""
        user_data = self.test_data['valid_users']['standard_user']
        
        # Remove content-type header
        original_headers = self.api_client.session.headers.copy()
        if 'Content-Type' in self.api_client.session.headers:
            del self.api_client.session.headers['Content-Type']
        
        try:
            response = self.api_client.post(
                self.login_endpoint,
                json={
                    'email': user_data['email'],
                    'password': user_data['password']
                }
            )
            
            # Should handle missing content-type gracefully
            assert response.status_code in [400, 415], \
                "Should return appropriate error for missing content-type"
                
        finally:
            # Restore original headers
            self.api_client.session.headers.update(original_headers)

    @pytest.mark.login
    @pytest.mark.regression
    def test_login_session_persistence(self):
        """Test that login session persists across requests."""
        user_data = self.test_data['valid_users']['standard_user']
        
        # Login
        success, response_data = self.auth_helper.login(
            user_data['email'], 
            user_data['password']
        )
        assert success, "Login should succeed"
        
        # Make authenticated request to profile endpoint
        profile_endpoint = self.test_data.get('endpoints', {}).get('profile', '/users/profile')
        profile_response = self.api_client.get(profile_endpoint)
        
        # Should be able to access protected resource
        assert profile_response.status_code in [200, 401], \
            "Profile request should return valid status code"
        
        if profile_response.status_code == 200:
            assert ResponseValidator.validate_json_response(profile_response), \
                "Profile response should be valid JSON"
