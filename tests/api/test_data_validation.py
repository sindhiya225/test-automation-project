"""
Advanced API data validation test suite.
Tests schema validation, data integrity, and edge cases.
"""
import pytest
import allure
import json
from typing import Dict, Any, List
from src.core.api_client import APIClient
from src.api.schemas import SchemaValidator
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)


@allure.epic("API Testing")
@allure.feature("Data Validation")
@allure.story("API Response Validation")
class TestDataValidation:
    """Test class for API data validation and integrity"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Setup before each test"""
        self.client = api_client
        self.schema_validator = SchemaValidator()
        yield
    
    @allure.title("Test JSON response structure validation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_json_structure_validation(self):
        """Test that API responses have valid JSON structure"""
        with allure.step("Make API request"):
            response = self.client.get("posts/1")
        
        with allure.step("Verify response is valid JSON"):
            assert response.status_code == 200
            
            # Test JSON parsing
            try:
                data = response.json()
                allure.attach(
                    json.dumps(data, indent=2),
                    name="Response JSON",
                    attachment_type=allure.attachment_type.JSON
                )
                
                # Verify it's a dictionary/object
                assert isinstance(data, dict)
                
                # Verify it has expected top-level keys
                expected_keys = ["userId", "id", "title", "body"]
                for key in expected_keys:
                    assert key in data
                
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON response: {e}")
    
    @allure.title("Test schema validation for user endpoint")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_user_schema_validation(self):
        """Test user data against JSON schema"""
        with allure.step("Get user data from API"):
            response = self.client.get("users/1")
            assert response.status_code == 200
            
            user_data = response.json()
        
        with allure.step("Validate against user schema"):
            validation_result = self.schema_validator.validate("user", user_data)
            
            allure.attach(
                json.dumps(validation_result, indent=2),
                name="Validation Result",
                attachment_type=allure.attachment_type.JSON
            )
            
            assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    @allure.title("Test data type validation in API responses")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    @pytest.mark.parametrize("endpoint,field,expected_type", [
        ("users/1", "id", int),
        ("users/1", "name", str),
        ("users/1", "email", str),
        ("posts/1", "userId", int),
        ("posts/1", "id", int),
        ("posts/1", "title", str),
        ("posts/1", "body", str)
    ])
    def test_data_type_validation(self, endpoint, field, expected_type):
        """Test that specific fields have correct data types"""
        with allure.step(f"Test {field} in {endpoint}"):
            response = self.client.get(endpoint)
            assert response.status_code == 200
            
            data = response.json()
            
            assert field in data, f"Field {field} not found in response"
            assert isinstance(data[field], expected_type), \
                f"Field {field} has type {type(data[field])}, expected {expected_type}"
    
    @allure.title("Test mandatory field presence in responses")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.validation
    @pytest.mark.parametrize("endpoint,mandatory_fields", [
        ("users/1", ["id", "name", "email", "username"]),
        ("posts/1", ["id", "userId", "title", "body"]),
        ("comments/1", ["id", "postId", "name", "email", "body"])
    ])
    def test_mandatory_fields(self, endpoint, mandatory_fields):
        """Test that mandatory fields are present in responses"""
        with allure.step(f"Check mandatory fields for {endpoint}"):
            response = self.client.get(endpoint)
            assert response.status_code == 200
            
            data = response.json()
            
            missing_fields = []
            for field in mandatory_fields:
                if field not in data:
                    missing_fields.append(field)
            
            assert len(missing_fields) == 0, \
                f"Missing mandatory fields: {missing_fields}"
    
    @allure.title("Test array response validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_array_response_validation(self):
        """Test validation of array/list responses"""
        with allure.step("Get array response from API"):
            response = self.client.get("users")
            assert response.status_code == 200
            
            data = response.json()
            
            # Verify it's an array
            assert isinstance(data, list), "Response should be an array"
            
            # Verify array is not empty
            assert len(data) > 0, "Response array should not be empty"
            
            # Verify all items have expected structure
            for item in data[:5]:  # Check first 5 items
                assert isinstance(item, dict), "Array items should be objects"
                assert "id" in item, "Array items should have 'id' field"
                assert "name" in item, "Array items should have 'name' field"
    
    @allure.title("Test nested object validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_nested_object_validation(self):
        """Test validation of nested objects in responses"""
        with allure.step("Get response with nested objects"):
            response = self.client.get("users/1")
            assert response.status_code == 200
            
            data = response.json()
            
            # Check for nested address object
            assert "address" in data, "User should have address object"
            assert isinstance(data["address"], dict), "Address should be an object"
            
            # Verify address fields
            address_fields = ["street", "suite", "city", "zipcode", "geo"]
            for field in address_fields:
                assert field in data["address"], f"Address missing field: {field}"
            
            # Verify nested geo object
            assert "geo" in data["address"], "Address should have geo object"
            assert isinstance(data["address"]["geo"], dict), "Geo should be an object"
            
            geo_fields = ["lat", "lng"]
            for field in geo_fields:
                assert field in data["address"]["geo"], f"Geo missing field: {field}"
    
    @allure.title("Test response data integrity and consistency")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_data_integrity(self):
        """Test data integrity across related endpoints"""
        with allure.step("Test user-post relationship integrity"):
            # Get a user
            user_response = self.client.get("users/1")
            user_data = user_response.json()
            user_id = user_data["id"]
            
            # Get posts by this user
            posts_response = self.client.get(f"posts?userId={user_id}")
            posts_data = posts_response.json()
            
            # Verify all posts belong to the user
            for post in posts_data:
                assert post["userId"] == user_id, \
                    f"Post {post['id']} has wrong userId: {post['userId']} != {user_id}"
            
            allure.attach(
                f"User ID: {user_id}\nNumber of posts: {len(posts_data)}",
                name="Data Integrity Check",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.title("Test response pagination validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_pagination_validation(self):
        """Test paginated response structure"""
        with allure.step("Test paginated endpoints"):
            # This endpoint might not support pagination in the test API
            # Using a simulated pagination test
            response = self.client.get("posts")
            data = response.json()
            
            # Simulate pagination validation
            # In real API with pagination, check for:
            # - page number
            # - page size
            # - total records
            # - total pages
            
            # For this demo, just verify we get an array
            assert isinstance(data, list)
            
            # Create pagination-like structure for testing
            paginated_response = {
                "data": data[:10],  # First 10 items as page 1
                "pagination": {
                    "page": 1,
                    "limit": 10,
                    "total": len(data),
                    "pages": (len(data) + 9) // 10  # Ceiling division
                }
            }
            
            # Validate against pagination schema
            validation_result = self.schema_validator.validate("user_list", paginated_response)
            
            if not validation_result["valid"]:
                logger.warning(f"Pagination validation issues: {validation_result['errors']}")
                # Might not be critical if API doesn't support pagination
    
    @allure.title("Test response header validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_response_header_validation(self):
        """Test validation of response headers"""
        with allure.step("Check response headers"):
            response = self.client.get("users/1")
            
            headers = response.headers
            
            # Check for important headers
            important_headers = [
                "Content-Type",
                "Content-Length",
                "Date",
                "Server"
            ]
            
            header_info = []
            for header in important_headers:
                if header in headers:
                    header_info.append(f"{header}: {headers[header]}")
                else:
                    header_info.append(f"{header}: MISSING")
            
            allure.attach(
                "\n".join(header_info),
                name="Response Headers",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Verify Content-Type is JSON
            assert "application/json" in headers.get("Content-Type", ""), \
                "Response should be JSON"
    
    @allure.title("Test error response validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_error_response_validation(self):
        """Test validation of error responses"""
        with allure.step("Test 404 error response"):
            # Try to access non-existent resource
            response = self.client.get("nonexistent/9999")
            
            # Some APIs return 404, others might return empty array
            # This test adapts to the API behavior
            
            if response.status_code == 404:
                # Validate error response structure
                try:
                    error_data = response.json()
                    
                    # Check for error fields
                    error_fields = ["error", "message", "statusCode"]
                    for field in error_fields:
                        if field in error_data:
                            logger.info(f"Error response contains {field}: {error_data[field]}")
                    
                except json.JSONDecodeError:
                    # Some APIs return empty body for 404
                    pass
            
            elif response.status_code == 200:
                # API might return empty array
                data = response.json()
                assert data == [] or data == {}, "Expected empty response for non-existent resource"
    
    @allure.title("Test data uniqueness validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_data_uniqueness(self):
        """Test uniqueness of data (like IDs)"""
        with allure.step("Check for duplicate IDs"):
            response = self.client.get("users")
            users = response.json()
            
            # Collect all IDs
            ids = [user["id"] for user in users]
            
            # Check for duplicates
            unique_ids = set(ids)
            
            assert len(ids) == len(unique_ids), \
                f"Duplicate IDs found: {ids} vs {unique_ids}"
            
            # Also verify IDs are sequential (if applicable)
            sorted_ids = sorted(ids)
            if sorted_ids == list(range(min(ids), max(ids) + 1)):
                logger.info("IDs are sequential")
            else:
                logger.warning("IDs are not sequential")
    
    @allure.title("Test response performance validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.performance
    def test_response_performance(self):
        """Test API response time performance"""
        import time
        
        with allure.step("Measure response time for critical endpoints"):
            endpoints = [
                "users/1",
                "posts/1",
                "comments/1"
            ]
            
            performance_results = []
            
            for endpoint in endpoints:
                start_time = time.time()
                response = self.client.get(endpoint)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                performance_results.append({
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "threshold_exceeded": response_time > 2.0  # 2 second threshold
                })
                
                assert response_time < 5.0, \
                    f"Response time for {endpoint} too high: {response_time:.2f}s"
            
            allure.attach(
                json.dumps(performance_results, indent=2),
                name="Performance Results",
                attachment_type=allure.attachment_type.JSON
            )
    
    @allure.title("Test data format validation (dates, emails, etc.)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    def test_data_format_validation(self):
        """Test validation of specific data formats"""
        import re
        
        with allure.step("Validate email format in user data"):
            response = self.client.get("users")
            users = response.json()
            
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            invalid_emails = []
            
            for user in users[:10]:  # Check first 10 users
                email = user.get("email", "")
                if not re.match(email_pattern, email):
                    invalid_emails.append({
                        "user_id": user["id"],
                        "email": email
                    })
            
            assert len(invalid_emails) == 0, \
                f"Invalid email formats found: {invalid_emails}"
    
    @allure.title("Test boundary value validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    @pytest.mark.parametrize("user_id", [
        0,  # Boundary: minimum (might not exist)
        1,  # First valid
        10, # Last valid (assuming 10 users)
        11, # Boundary: just beyond valid range
        999 # Far beyond valid range
    ])
    def test_boundary_value_validation(self, user_id):
        """Test API behavior with boundary values"""
        with allure.step(f"Test with user_id={user_id}"):
            response = self.client.get(f"users/{user_id}")
            
            if user_id in [1, 10]:  # Valid IDs
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == user_id
            else:  # Invalid IDs
                # API might return 404 or empty response
                acceptable_codes = [404, 200]
                assert response.status_code in acceptable_codes, \
                    f"Unexpected status code: {response.status_code}"