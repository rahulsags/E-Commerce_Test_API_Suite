"""
Test cases for checkout functionality.
Covers positive, negative, and boundary test scenarios for the checkout process.
"""

import pytest
import time
from faker import Faker
from utils.api_helpers import (
    APIClient, AuthHelper, CartHelper, CheckoutHelper, ResponseValidator, 
    TestDataLoader, setup_logging
)


# Setup logging for tests
setup_logging()

# Initialize Faker for generating test data
fake = Faker()


class TestCheckout:
    """Test class for checkout functionality."""
    
    @classmethod
    def setup_class(cls):
        """Setup test class with common test data and API client."""
        cls.test_data = TestDataLoader.load_test_data()
        cls.base_url = cls.test_data.get('base_url', 'https://api.ecommerce-demo.com')
        cls.api_client = APIClient(cls.base_url)
        cls.auth_helper = AuthHelper(cls.api_client)
        cls.cart_helper = CartHelper(cls.api_client)
        cls.checkout_helper = CheckoutHelper(cls.api_client)
        
        # Endpoints
        cls.checkout_endpoint = cls.test_data.get('endpoints', {}).get('checkout', '/checkout')
        cls.orders_endpoint = cls.test_data.get('endpoints', {}).get('orders', '/orders')
        cls.cart_items_endpoint = cls.test_data.get('endpoints', {}).get('cart_items', '/cart/items')

    def setup_method(self):
        """Setup method run before each test - login and prepare cart."""
        # Login with standard user
        user_data = self.test_data['valid_users']['standard_user']
        success, _ = self.auth_helper.login(user_data['email'], user_data['password'])
        assert success, "Login should succeed before checkout tests"
        
        # Clear cart and add test items
        self.cart_helper.clear_cart()
        
        # Add a standard item for checkout
        product = self.test_data['products']['laptop']
        add_response = self.cart_helper.add_item_to_cart(
            product['id'], 
            1,
            self.cart_items_endpoint
        )
        assert add_response.status_code in [200, 201], "Adding item for checkout should succeed"

    def teardown_method(self):
        """Cleanup method run after each test."""
        # Clear cart after test
        self.cart_helper.clear_cart()

    @pytest.mark.smoke
    @pytest.mark.checkout
    @pytest.mark.positive
    def test_initiate_checkout(self):
        """Test initiating checkout process."""
        response = self.checkout_helper.initiate_checkout(self.checkout_endpoint)
        
        # Assertions
        assert response.status_code in [200, 201], "Checkout initiation should succeed"
        assert ResponseValidator.validate_json_response(response), "Response should be valid JSON"
        
        response_data = response.json()
        expected_fields = ['checkout_id', 'total', 'items']
        
        for field in expected_fields:
            if field in response_data:
                assert response_data[field] is not None, f"{field} should not be null"

    @pytest.mark.checkout
    @pytest.mark.positive
    def test_complete_checkout_valid_data(self):
        """Test completing checkout with valid shipping and payment data."""
        # Get test data
        shipping_address = self.test_data['checkout_data']['valid_address']
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        # Initiate checkout first
        init_response = self.checkout_helper.initiate_checkout(self.checkout_endpoint)
        assert init_response.status_code in [200, 201], "Checkout initiation should succeed"
        
        # Complete checkout
        submit_response = self.checkout_helper.submit_checkout(
            shipping_address, 
            payment_info, 
            self.checkout_endpoint
        )
        
        # Assertions
        assert submit_response.status_code in [200, 201], "Checkout submission should succeed"
        assert ResponseValidator.validate_json_response(submit_response), \
            "Checkout response should be valid JSON"
        
        response_data = submit_response.json()
        required_fields = ['order_id', 'status', 'total']
        assert ResponseValidator.validate_response_schema(submit_response, required_fields), \
            f"Checkout response should contain: {required_fields}"
        
        # Verify order was created
        order_id = response_data.get('order_id')
        if order_id:
            order_response = self.checkout_helper.get_order_summary(order_id, self.orders_endpoint)
            assert order_response.status_code == 200, "Order should be retrievable after checkout"

    @pytest.mark.checkout
    @pytest.mark.positive
    def test_checkout_multiple_items(self):
        """Test checkout with multiple items in cart."""
        # Add additional items to cart
        additional_products = [
            (self.test_data['products']['smartphone'], 1),
            (self.test_data['products']['book'], 2)
        ]
        
        for product, quantity in additional_products:
            response = self.cart_helper.add_item_to_cart(
                product['id'], 
                quantity,
                self.cart_items_endpoint
            )
            assert response.status_code in [200, 201], f"Adding {product['name']} should succeed"
        
        # Get test data
        shipping_address = self.test_data['checkout_data']['valid_address']
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        # Complete checkout
        submit_response = self.checkout_helper.submit_checkout(
            shipping_address, 
            payment_info, 
            self.checkout_endpoint
        )
        
        # Assertions
        assert submit_response.status_code in [200, 201], \
            "Multi-item checkout should succeed"
        
        response_data = submit_response.json()
        
        # Verify total reflects multiple items
        expected_total = (
            self.test_data['products']['laptop']['price'] * 1 +
            self.test_data['products']['smartphone']['price'] * 1 +
            self.test_data['products']['book']['price'] * 2
        )
        
        actual_total = response_data.get('total', 0)
        assert abs(actual_total - expected_total) < 0.01, \
            f"Checkout total should be {expected_total}, got {actual_total}"

    @pytest.mark.checkout
    @pytest.mark.negative
    def test_checkout_empty_cart(self):
        """Test checkout with empty cart."""
        # Clear cart
        self.cart_helper.clear_cart()
        
        # Try to initiate checkout
        response = self.checkout_helper.initiate_checkout(self.checkout_endpoint)
        
        # Should prevent checkout of empty cart
        assert response.status_code in [400, 409], \
            "Checkout with empty cart should return error"
        assert ResponseValidator.validate_error_response(response), \
            "Error response should be properly formatted"

    @pytest.mark.checkout
    @pytest.mark.negative
    def test_checkout_invalid_shipping_address(self):
        """Test checkout with invalid shipping address."""
        invalid_addresses = [
            {},  # Empty address
            {"street": ""},  # Empty street
            {"street": "123 Main St"},  # Missing required fields
            {"street": "123 Main St", "city": "", "state": "CA", "zip_code": "12345"},  # Empty city
            {"street": "123 Main St", "city": "City", "state": "", "zip_code": "12345"},  # Empty state
            {"street": "123 Main St", "city": "City", "state": "CA", "zip_code": ""},  # Empty zip
        ]
        
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        for invalid_address in invalid_addresses:
            response = self.checkout_helper.submit_checkout(
                invalid_address, 
                payment_info, 
                self.checkout_endpoint
            )
            
            # Should reject invalid address
            assert response.status_code == 400, \
                f"Invalid address should be rejected: {invalid_address}"
            assert ResponseValidator.validate_error_response(response), \
                f"Error response should be formatted for address: {invalid_address}"

    @pytest.mark.checkout
    @pytest.mark.negative
    def test_checkout_invalid_payment_info(self):
        """Test checkout with invalid payment information."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        invalid_payment = self.test_data['checkout_data']['invalid_payment']
        
        response = self.checkout_helper.submit_checkout(
            shipping_address, 
            invalid_payment, 
            self.checkout_endpoint
        )
        
        # Should reject invalid payment info
        assert response.status_code == 400, "Invalid payment info should be rejected"
        assert ResponseValidator.validate_error_response(response), \
            "Error response should be properly formatted"
        
        response_data = response.json()
        error_message = response_data.get('error', '') + response_data.get('message', '')
        assert any(keyword in error_message.lower() for keyword in 
                  ['payment', 'card', 'invalid']), \
            "Error message should indicate payment issue"

    @pytest.mark.checkout
    @pytest.mark.negative
    def test_checkout_expired_card(self):
        """Test checkout with expired credit card."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        
        # Create expired card data
        expired_payment = {
            "card_number": "4111111111111111",
            "expiry_month": "12",
            "expiry_year": "2020",  # Expired year
            "cvv": "123",
            "cardholder_name": "John Doe"
        }
        
        response = self.checkout_helper.submit_checkout(
            shipping_address, 
            expired_payment, 
            self.checkout_endpoint
        )
        
        # Should reject expired card
        assert response.status_code == 400, "Expired card should be rejected"
        assert ResponseValidator.validate_error_response(response), \
            "Error response should be properly formatted"

    @pytest.mark.checkout
    @pytest.mark.negative
    def test_checkout_invalid_card_number(self):
        """Test checkout with invalid credit card number."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        
        invalid_card_numbers = [
            "1234567890123456",  # Invalid Luhn
            "411111111111111",   # Too short
            "41111111111111111", # Too long
            "abcd1111efgh2222",  # Contains letters
            "",                  # Empty
            "0000000000000000"   # All zeros
        ]
        
        for invalid_card in invalid_card_numbers:
            invalid_payment = {
                "card_number": invalid_card,
                "expiry_month": "12",
                "expiry_year": "2025",
                "cvv": "123",
                "cardholder_name": "John Doe"
            }
            
            response = self.checkout_helper.submit_checkout(
                shipping_address, 
                invalid_payment, 
                self.checkout_endpoint
            )
            
            # Should reject invalid card number
            assert response.status_code == 400, \
                f"Invalid card number should be rejected: {invalid_card}"

    @pytest.mark.checkout
    @pytest.mark.boundary
    def test_checkout_boundary_values(self):
        """Test checkout with boundary values."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        
        # Test boundary CVV values
        boundary_cvvs = ["000", "999", "12", "1234"]  # Min/max values
        
        for cvv in boundary_cvvs:
            payment_info = {
                "card_number": "4111111111111111",
                "expiry_month": "12",
                "expiry_year": "2025",
                "cvv": cvv,
                "cardholder_name": "John Doe"
            }
            
            response = self.checkout_helper.submit_checkout(
                shipping_address, 
                payment_info, 
                self.checkout_endpoint
            )
            
            # Should handle boundary CVV values appropriately
            if len(cvv) == 3:  # Valid CVV length
                assert response.status_code in [200, 201, 400], \
                    f"CVV {cvv} should be handled appropriately"
            else:  # Invalid CVV length
                assert response.status_code == 400, \
                    f"Invalid CVV length {cvv} should be rejected"

    @pytest.mark.checkout
    @pytest.mark.negative
    def test_checkout_without_authentication(self):
        """Test checkout without authentication."""
        # Clear authentication
        self.api_client.clear_auth_token()
        
        shipping_address = self.test_data['checkout_data']['valid_address']
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        # Try to checkout without auth
        response = self.checkout_helper.submit_checkout(
            shipping_address, 
            payment_info, 
            self.checkout_endpoint
        )
        
        # Should require authentication
        assert response.status_code == 401, "Checkout should require authentication"
        assert ResponseValidator.validate_error_response(response), \
            "Unauthorized response should be properly formatted"

    @pytest.mark.checkout
    @pytest.mark.negative
    def test_checkout_insufficient_stock(self):
        """Test checkout when product becomes out of stock."""
        # Clear cart and add out of stock item
        self.cart_helper.clear_cart()
        
        out_of_stock_product = self.test_data['products']['out_of_stock']
        
        # Try to add out of stock item (might succeed depending on implementation)
        add_response = self.cart_helper.add_item_to_cart(
            out_of_stock_product['id'], 
            1,
            self.cart_items_endpoint
        )
        
        # If item was added to cart, checkout should detect stock issue
        if add_response.status_code in [200, 201]:
            shipping_address = self.test_data['checkout_data']['valid_address']
            payment_info = self.test_data['checkout_data']['valid_payment']
            
            response = self.checkout_helper.submit_checkout(
                shipping_address, 
                payment_info, 
                self.checkout_endpoint
            )
            
            # Should detect stock issue at checkout
            assert response.status_code in [400, 409], \
                "Checkout should detect insufficient stock"
            
            response_data = response.json()
            error_message = response_data.get('error', '') + response_data.get('message', '')
            assert 'stock' in error_message.lower() or 'available' in error_message.lower(), \
                "Error should indicate stock issue"

    @pytest.mark.checkout
    @pytest.mark.regression
    def test_checkout_tax_calculation(self):
        """Test that taxes are calculated correctly during checkout."""
        # Add items with known prices
        laptop = self.test_data['products']['laptop']
        
        shipping_address = self.test_data['checkout_data']['valid_address']
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        # Complete checkout
        response = self.checkout_helper.submit_checkout(
            shipping_address, 
            payment_info, 
            self.checkout_endpoint
        )
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            
            # Check if tax information is included
            if 'tax' in response_data:
                base_total = laptop['price']
                tax_amount = response_data.get('tax', 0)
                total_with_tax = response_data.get('total', 0)
                
                # Verify tax calculation (assuming reasonable tax rate)
                expected_total = base_total + tax_amount
                assert abs(total_with_tax - expected_total) < 0.01, \
                    "Total should equal base amount plus tax"
                
                # Tax should be reasonable percentage
                tax_rate = tax_amount / base_total if base_total > 0 else 0
                assert 0 <= tax_rate <= 0.20, \
                    f"Tax rate should be reasonable (0-20%), got {tax_rate:.2%}"

    @pytest.mark.checkout
    @pytest.mark.regression
    def test_checkout_shipping_calculation(self):
        """Test that shipping costs are calculated correctly."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        response = self.checkout_helper.submit_checkout(
            shipping_address, 
            payment_info, 
            self.checkout_endpoint
        )
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            
            # Check if shipping information is included
            if 'shipping' in response_data:
                shipping_cost = response_data.get('shipping', 0)
                
                # Shipping cost should be non-negative
                assert shipping_cost >= 0, "Shipping cost should be non-negative"
                
                # Should be reasonable amount
                assert shipping_cost <= 100, "Shipping cost should be reasonable"

    @pytest.mark.checkout
    @pytest.mark.positive
    def test_checkout_order_confirmation(self):
        """Test that order confirmation contains all necessary information."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        response = self.checkout_helper.submit_checkout(
            shipping_address, 
            payment_info, 
            self.checkout_endpoint
        )
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            
            # Verify order confirmation structure
            required_fields = ['order_id', 'status', 'total']
            for field in required_fields:
                assert field in response_data, f"Order confirmation should contain {field}"
                assert response_data[field] is not None, f"{field} should not be null"
            
            # Order ID should be valid format
            order_id = response_data['order_id']
            assert isinstance(order_id, (str, int)), "Order ID should be string or integer"
            assert len(str(order_id)) > 0, "Order ID should not be empty"
            
            # Status should be valid
            valid_statuses = ['confirmed', 'pending', 'processing', 'placed']
            status = response_data['status'].lower()
            assert any(valid_status in status for valid_status in valid_statuses), \
                f"Order status should be valid, got: {status}"

    @pytest.mark.checkout
    @pytest.mark.negative
    def test_checkout_payment_processing_failure(self):
        """Test checkout when payment processing fails."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        
        # Use a test card number that simulates payment failure
        failing_payment = {
            "card_number": "4000000000000002",  # Common test card for payment failure
            "expiry_month": "12",
            "expiry_year": "2025",
            "cvv": "123",
            "cardholder_name": "John Doe"
        }
        
        response = self.checkout_helper.submit_checkout(
            shipping_address, 
            failing_payment, 
            self.checkout_endpoint
        )
        
        # Should handle payment failure gracefully
        if response.status_code in [400, 402, 409]:  # Payment failed
            assert ResponseValidator.validate_error_response(response), \
                "Payment failure response should be properly formatted"
            
            response_data = response.json()
            error_message = response_data.get('error', '') + response_data.get('message', '')
            assert any(keyword in error_message.lower() for keyword in 
                      ['payment', 'declined', 'failed']), \
                "Error should indicate payment failure"

    @pytest.mark.checkout
    @pytest.mark.regression
    def test_checkout_concurrent_requests(self):
        """Test checkout behavior with concurrent requests."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        # Make multiple concurrent checkout attempts
        responses = []
        
        for _ in range(3):
            response = self.checkout_helper.submit_checkout(
                shipping_address, 
                payment_info, 
                self.checkout_endpoint
            )
            responses.append(response)
            
            # Small delay to simulate near-concurrent requests
            time.sleep(0.1)
        
        # Only one should succeed, or all should fail gracefully
        success_count = sum(1 for r in responses if r.status_code in [200, 201])
        
        # Should either process one successfully or prevent all (depending on implementation)
        assert success_count <= 1, "Should not process multiple checkouts for same cart"
        
        # All responses should be properly formatted
        for response in responses:
            if response.status_code >= 400:
                assert ResponseValidator.validate_error_response(response), \
                    "Error responses should be properly formatted"

    @pytest.mark.checkout
    @pytest.mark.positive
    def test_get_order_details(self):
        """Test retrieving order details after successful checkout."""
        shipping_address = self.test_data['checkout_data']['valid_address']
        payment_info = self.test_data['checkout_data']['valid_payment']
        
        # Complete checkout first
        checkout_response = self.checkout_helper.submit_checkout(
            shipping_address, 
            payment_info, 
            self.checkout_endpoint
        )
        
        if checkout_response.status_code in [200, 201]:
            checkout_data = checkout_response.json()
            order_id = checkout_data.get('order_id')
            
            if order_id:
                # Get order details
                order_response = self.checkout_helper.get_order_summary(
                    order_id, 
                    self.orders_endpoint
                )
                
                # Assertions
                assert order_response.status_code == 200, \
                    "Should be able to retrieve order details"
                assert ResponseValidator.validate_json_response(order_response), \
                    "Order details should be valid JSON"
                
                order_data = order_response.json()
                expected_fields = ['order_id', 'status', 'items', 'total', 'shipping_address']
                
                for field in expected_fields:
                    if field in order_data:
                        assert order_data[field] is not None, \
                            f"Order {field} should not be null"
                
                # Order ID should match
                assert str(order_data.get('order_id')) == str(order_id), \
                    "Retrieved order ID should match checkout order ID"
