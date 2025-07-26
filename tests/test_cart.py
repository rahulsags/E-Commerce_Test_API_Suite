"""
Test cases for shopping cart functionality.
Covers positive, negative, and boundary test scenarios for cart operations.
"""

import pytest
import time
from faker import Faker
from utils.api_helpers import (
    APIClient, AuthHelper, CartHelper, ResponseValidator, 
    TestDataLoader, setup_logging
)


# Setup logging for tests
setup_logging()

# Initialize Faker for generating test data
fake = Faker()


class TestCart:
    """Test class for shopping cart functionality."""
    
    @classmethod
    def setup_class(cls):
        """Setup test class with common test data and API client."""
        cls.test_data = TestDataLoader.load_test_data()
        cls.base_url = cls.test_data.get('base_url', 'https://api.ecommerce-demo.com')
        cls.api_client = APIClient(cls.base_url)
        cls.auth_helper = AuthHelper(cls.api_client)
        cls.cart_helper = CartHelper(cls.api_client)
        
        # Endpoints
        cls.cart_endpoint = cls.test_data.get('endpoints', {}).get('cart', '/cart')
        cls.cart_items_endpoint = cls.test_data.get('endpoints', {}).get('cart_items', '/cart/items')

    def setup_method(self):
        """Setup method run before each test - login and clear cart."""
        # Login with standard user
        user_data = self.test_data['valid_users']['standard_user']
        success, _ = self.auth_helper.login(user_data['email'], user_data['password'])
        assert success, "Login should succeed before cart tests"
        
        # Clear cart to start with clean state
        self.cart_helper.clear_cart(self.cart_endpoint)

    def teardown_method(self):
        """Cleanup method run after each test."""
        # Clear cart after test
        self.cart_helper.clear_cart(self.cart_endpoint)

    @pytest.mark.smoke
    @pytest.mark.cart
    @pytest.mark.positive
    def test_add_item_to_cart(self):
        """Test adding a valid item to cart."""
        # Test data
        product = self.test_data['products']['laptop']
        cart_data = self.test_data['cart_scenarios']['valid_item']
        
        # Add item to cart
        response = self.cart_helper.add_item_to_cart(
            product['id'], 
            cart_data['quantity'],
            self.cart_items_endpoint
        )
        
        # Assertions
        assert response.status_code in [200, 201], "Adding item to cart should succeed"
        assert ResponseValidator.validate_json_response(response), "Response should be valid JSON"
        
        response_data = response.json()
        assert 'item' in response_data or 'product_id' in response_data, \
            "Response should contain item information"

    @pytest.mark.cart
    @pytest.mark.positive
    def test_add_multiple_items_to_cart(self):
        """Test adding multiple different items to cart."""
        products = [
            (self.test_data['products']['laptop'], 1),
            (self.test_data['products']['smartphone'], 2),
            (self.test_data['products']['book'], 3)
        ]
        
        # Add multiple items
        for product, quantity in products:
            response = self.cart_helper.add_item_to_cart(
                product['id'], 
                quantity,
                self.cart_items_endpoint
            )
            assert response.status_code in [200, 201], \
                f"Adding {product['name']} should succeed"
        
        # Verify cart contents
        cart_response = self.cart_helper.get_cart_contents(self.cart_endpoint)
        assert cart_response.status_code == 200, "Getting cart contents should succeed"
        
        cart_data = cart_response.json()
        assert 'items' in cart_data, "Cart should contain items"
        assert len(cart_data['items']) == len(products), \
            f"Cart should contain {len(products)} different items"

    @pytest.mark.cart
    @pytest.mark.positive
    def test_update_cart_item_quantity(self):
        """Test updating quantity of item in cart."""
        # First add an item
        product = self.test_data['products']['laptop']
        initial_quantity = 1
        
        add_response = self.cart_helper.add_item_to_cart(
            product['id'], 
            initial_quantity,
            self.cart_items_endpoint
        )
        assert add_response.status_code in [200, 201], "Adding item should succeed"
        
        # Update quantity
        new_quantity = 3
        update_response = self.cart_helper.update_cart_item(
            product['id'], 
            new_quantity,
            self.cart_items_endpoint
        )
        
        # Assertions
        assert update_response.status_code == 200, "Updating item quantity should succeed"
        
        # Verify updated quantity
        cart_response = self.cart_helper.get_cart_contents(self.cart_endpoint)
        cart_data = cart_response.json()
        
        updated_item = None
        for item in cart_data.get('items', []):
            if item.get('product_id') == product['id']:
                updated_item = item
                break
        
        assert updated_item is not None, "Updated item should be found in cart"
        assert updated_item.get('quantity') == new_quantity, \
            f"Item quantity should be updated to {new_quantity}"

    @pytest.mark.cart
    @pytest.mark.positive
    def test_remove_item_from_cart(self):
        """Test removing an item from cart."""
        # First add an item
        product = self.test_data['products']['laptop']
        
        add_response = self.cart_helper.add_item_to_cart(
            product['id'], 
            1,
            self.cart_items_endpoint
        )
        assert add_response.status_code in [200, 201], "Adding item should succeed"
        
        # Remove the item
        remove_response = self.cart_helper.remove_item_from_cart(
            product['id'],
            self.cart_items_endpoint
        )
        
        # Assertions
        assert remove_response.status_code in [200, 204], "Removing item should succeed"
        
        # Verify item is removed
        cart_response = self.cart_helper.get_cart_contents(self.cart_endpoint)
        cart_data = cart_response.json()
        
        items = cart_data.get('items', [])
        item_exists = any(item.get('product_id') == product['id'] for item in items)
        assert not item_exists, "Removed item should not be in cart"

    @pytest.mark.cart
    @pytest.mark.positive
    def test_clear_entire_cart(self):
        """Test clearing all items from cart."""
        # Add multiple items first
        products = [
            self.test_data['products']['laptop'],
            self.test_data['products']['smartphone']
        ]
        
        for product in products:
            response = self.cart_helper.add_item_to_cart(
                product['id'], 
                1,
                self.cart_items_endpoint
            )
            assert response.status_code in [200, 201], f"Adding {product['name']} should succeed"
        
        # Clear cart
        clear_response = self.cart_helper.clear_cart(self.cart_endpoint)
        assert clear_response.status_code in [200, 204], "Clearing cart should succeed"
        
        # Verify cart is empty
        cart_response = self.cart_helper.get_cart_contents(self.cart_endpoint)
        cart_data = cart_response.json()
        
        items = cart_data.get('items', [])
        assert len(items) == 0, "Cart should be empty after clearing"

    @pytest.mark.cart
    @pytest.mark.positive
    def test_get_cart_contents(self):
        """Test retrieving cart contents."""
        # Add an item first
        product = self.test_data['products']['laptop']
        quantity = 2
        
        self.cart_helper.add_item_to_cart(
            product['id'], 
            quantity,
            self.cart_items_endpoint
        )
        
        # Get cart contents
        response = self.cart_helper.get_cart_contents(self.cart_endpoint)
        
        # Assertions
        assert response.status_code == 200, "Getting cart contents should succeed"
        assert ResponseValidator.validate_json_response(response), "Response should be valid JSON"
        
        cart_data = response.json()
        required_fields = ['items', 'total']
        assert ResponseValidator.validate_response_schema(response, required_fields), \
            f"Cart response should contain: {required_fields}"
        
        # Verify item details
        items = cart_data['items']
        assert len(items) == 1, "Cart should contain one item"
        
        item = items[0]
        assert item['product_id'] == product['id'], "Product ID should match"
        assert item['quantity'] == quantity, "Quantity should match"

    @pytest.mark.cart
    @pytest.mark.negative
    def test_add_invalid_product_to_cart(self):
        """Test adding non-existent product to cart."""
        invalid_scenario = self.test_data['cart_scenarios']['invalid_product_id']
        
        response = self.cart_helper.add_item_to_cart(
            invalid_scenario['product_id'], 
            invalid_scenario['quantity'],
            self.cart_items_endpoint
        )
        
        # Assertions
        assert response.status_code in [400, 404], \
            "Adding invalid product should return error status"
        assert ResponseValidator.validate_error_response(response), \
            "Error response should be properly formatted"

    @pytest.mark.cart
    @pytest.mark.negative
    def test_add_zero_quantity_to_cart(self):
        """Test adding item with zero quantity."""
        zero_scenario = self.test_data['cart_scenarios']['zero_quantity']
        
        response = self.cart_helper.add_item_to_cart(
            zero_scenario['product_id'], 
            zero_scenario['quantity'],
            self.cart_items_endpoint
        )
        
        # Assertions
        assert response.status_code == 400, \
            "Adding zero quantity should return bad request"
        assert ResponseValidator.validate_error_response(response), \
            "Error response should be properly formatted"

    @pytest.mark.cart
    @pytest.mark.negative
    def test_add_negative_quantity_to_cart(self):
        """Test adding item with negative quantity."""
        negative_scenario = self.test_data['cart_scenarios']['negative_quantity']
        
        response = self.cart_helper.add_item_to_cart(
            negative_scenario['product_id'], 
            negative_scenario['quantity'],
            self.cart_items_endpoint
        )
        
        # Assertions
        assert response.status_code == 400, \
            "Adding negative quantity should return bad request"
        assert ResponseValidator.validate_error_response(response), \
            "Error response should be properly formatted"

    @pytest.mark.cart
    @pytest.mark.boundary
    def test_add_maximum_quantity_to_cart(self):
        """Test adding item with maximum allowed quantity."""
        max_quantity = self.test_data['test_boundaries']['max_cart_quantity']
        product = self.test_data['products']['laptop']
        
        response = self.cart_helper.add_item_to_cart(
            product['id'], 
            max_quantity,
            self.cart_items_endpoint
        )
        
        # Should either succeed or fail gracefully
        if response.status_code in [200, 201]:
            # If successful, verify quantity
            cart_response = self.cart_helper.get_cart_contents(self.cart_endpoint)
            cart_data = cart_response.json()
            
            cart_item = None
            for item in cart_data.get('items', []):
                if item.get('product_id') == product['id']:
                    cart_item = item
                    break
            
            assert cart_item is not None, "Item should be in cart"
            assert cart_item['quantity'] <= max_quantity, \
                "Quantity should not exceed maximum"
        else:
            # If failed, should return appropriate error
            assert response.status_code == 400, \
                "Should return bad request for exceeding maximum quantity"

    @pytest.mark.cart
    @pytest.mark.boundary
    def test_add_large_quantity_to_cart(self):
        """Test adding item with very large quantity."""
        large_scenario = self.test_data['cart_scenarios']['large_quantity']
        
        response = self.cart_helper.add_item_to_cart(
            large_scenario['product_id'], 
            large_scenario['quantity'],
            self.cart_items_endpoint
        )
        
        # Should handle large quantity gracefully
        assert response.status_code in [200, 201, 400], \
            "Should handle large quantity with appropriate response"
        
        if response.status_code == 400:
            assert ResponseValidator.validate_error_response(response), \
                "Error response should be properly formatted"

    @pytest.mark.cart
    @pytest.mark.negative
    def test_add_out_of_stock_item(self):
        """Test adding out of stock item to cart."""
        out_of_stock = self.test_data['products']['out_of_stock']
        
        response = self.cart_helper.add_item_to_cart(
            out_of_stock['id'], 
            1,
            self.cart_items_endpoint
        )
        
        # Should handle out of stock appropriately
        if response.status_code in [400, 409]:  # Bad request or conflict
            assert ResponseValidator.validate_error_response(response), \
                "Out of stock error should be properly formatted"
            
            response_data = response.json()
            error_message = response_data.get('error', '') + response_data.get('message', '')
            assert 'stock' in error_message.lower() or 'available' in error_message.lower(), \
                "Error message should indicate stock issue"

    @pytest.mark.cart
    @pytest.mark.negative
    def test_remove_non_existent_item(self):
        """Test removing item that doesn't exist in cart."""
        non_existent_product_id = 99999
        
        response = self.cart_helper.remove_item_from_cart(
            non_existent_product_id,
            self.cart_items_endpoint
        )
        
        # Should handle gracefully
        assert response.status_code in [404, 400, 204], \
            "Removing non-existent item should return appropriate status"

    @pytest.mark.cart
    @pytest.mark.negative
    def test_update_non_existent_item(self):
        """Test updating quantity of item not in cart."""
        non_existent_product_id = 99999
        
        response = self.cart_helper.update_cart_item(
            non_existent_product_id, 
            5,
            self.cart_items_endpoint
        )
        
        # Should return appropriate error
        assert response.status_code in [404, 400], \
            "Updating non-existent item should return error"
        assert ResponseValidator.validate_error_response(response), \
            "Error response should be properly formatted"

    @pytest.mark.cart
    @pytest.mark.negative
    def test_cart_operations_without_authentication(self):
        """Test cart operations without authentication."""
        # Clear authentication
        self.api_client.clear_auth_token()
        
        product = self.test_data['products']['laptop']
        
        # Try to add item without auth
        response = self.cart_helper.add_item_to_cart(
            product['id'], 
            1,
            self.cart_items_endpoint
        )
        
        # Should require authentication
        assert response.status_code == 401, \
            "Cart operations should require authentication"
        assert ResponseValidator.validate_error_response(response), \
            "Unauthorized response should be properly formatted"

    @pytest.mark.cart
    @pytest.mark.regression
    def test_cart_total_calculation(self):
        """Test that cart total is calculated correctly."""
        # Add items with known prices
        items_to_add = [
            (self.test_data['products']['laptop'], 2),  # 1299.99 * 2 = 2599.98
            (self.test_data['products']['book'], 1)     # 39.99 * 1 = 39.99
        ]
        
        expected_total = 0
        for product, quantity in items_to_add:
            self.cart_helper.add_item_to_cart(
                product['id'], 
                quantity,
                self.cart_items_endpoint
            )
            expected_total += product['price'] * quantity
        
        # Get cart and verify total
        cart_response = self.cart_helper.get_cart_contents(self.cart_endpoint)
        cart_data = cart_response.json()
        
        actual_total = cart_data.get('total', 0)
        
        # Allow for small floating point differences
        assert abs(actual_total - expected_total) < 0.01, \
            f"Cart total should be {expected_total}, but got {actual_total}"

    @pytest.mark.cart
    @pytest.mark.positive
    def test_add_same_item_multiple_times(self):
        """Test adding the same item multiple times (should update quantity)."""
        product = self.test_data['products']['laptop']
        
        # Add item first time
        response1 = self.cart_helper.add_item_to_cart(
            product['id'], 
            2,
            self.cart_items_endpoint
        )
        assert response1.status_code in [200, 201], "First add should succeed"
        
        # Add same item again
        response2 = self.cart_helper.add_item_to_cart(
            product['id'], 
            3,
            self.cart_items_endpoint
        )
        assert response2.status_code in [200, 201], "Second add should succeed"
        
        # Verify final quantity
        cart_response = self.cart_helper.get_cart_contents(self.cart_endpoint)
        cart_data = cart_response.json()
        
        items = cart_data.get('items', [])
        laptop_items = [item for item in items if item.get('product_id') == product['id']]
        
        # Should either have one item with combined quantity or handle as separate line items
        if len(laptop_items) == 1:
            # Combined into one line item
            assert laptop_items[0]['quantity'] == 5, "Quantities should be combined (2+3=5)"
        else:
            # Separate line items
            total_quantity = sum(item['quantity'] for item in laptop_items)
            assert total_quantity == 5, "Total quantity should be 5"

    @pytest.mark.cart
    @pytest.mark.regression
    def test_cart_persistence_across_sessions(self):
        """Test that cart persists across login sessions."""
        product = self.test_data['products']['laptop']
        user_data = self.test_data['valid_users']['standard_user']
        
        # Add item to cart
        add_response = self.cart_helper.add_item_to_cart(
            product['id'], 
            2,
            self.cart_items_endpoint
        )
        assert add_response.status_code in [200, 201], "Adding item should succeed"
        
        # Logout
        self.auth_helper.logout()
        
        # Login again
        login_success, _ = self.auth_helper.login(user_data['email'], user_data['password'])
        assert login_success, "Re-login should succeed"
        
        # Check if cart still contains the item
        cart_response = self.cart_helper.get_cart_contents(self.cart_endpoint)
        
        if cart_response.status_code == 200:
            cart_data = cart_response.json()
            items = cart_data.get('items', [])
            
            # Cart may or may not persist depending on implementation
            # Document the expected behavior
            if items:
                # Cart persisted
                laptop_item = next((item for item in items 
                                  if item.get('product_id') == product['id']), None)
                if laptop_item:
                    assert laptop_item['quantity'] == 2, \
                        "Cart item quantity should persist across sessions"

    @pytest.mark.cart
    @pytest.mark.negative
    def test_malformed_cart_requests(self):
        """Test cart API with malformed requests."""
        malformed_payloads = [
            {},  # Empty payload
            {"product_id": "invalid"},  # Invalid product ID type
            {"quantity": "invalid"},    # Invalid quantity type
            {"product_id": 1},         # Missing quantity
            {"quantity": 1},           # Missing product ID
            {"product_id": None, "quantity": 1},  # Null product ID
            {"product_id": 1, "quantity": None}   # Null quantity
        ]
        
        for payload in malformed_payloads:
            response = self.api_client.post(self.cart_items_endpoint, json=payload)
            
            # Should return bad request for malformed data
            assert response.status_code == 400, \
                f"Malformed payload should return 400: {payload}"
            assert ResponseValidator.validate_error_response(response), \
                f"Error response should be properly formatted for payload: {payload}"
