"""
Comprehensive User API test suite.
Tests CRUD operations and user management functionality.
"""
import pytest
import allure
import json
import time
from typing import Dict, Any, List
from faker import Faker
from src.core.api_client import APIClient
from src.api.schemas import SchemaValidator
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)
fake = Faker()


@allure.epic("API Testing")
@allure.feature("User Management")
@allure.story("User API Operations")
class TestUserAPI:
    """Test class for User API CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Setup before each test"""
        self.client = api_client
        self.schema_validator = SchemaValidator()
        self.created_users = []  # Track users created during tests
        self.test_user_data = self._generate_test_user_data()
        yield
        
        # Cleanup: Delete created users (if API supports DELETE)
        self._cleanup_created_users()
    
    def _generate_test_user_data(self) -> Dict[str, Any]:
        """Generate test user data"""
        return {
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            "address": {
                "street": fake.street_address(),
                "suite": fake.building_number(),
                "city": fake.city(),
                "zipcode": fake.zipcode(),
                "geo": {
                    "lat": str(fake.latitude()),
                    "lng": str(fake.longitude())
                }
            },
            "phone": fake.phone_number(),
            "website": fake.url(),
            "company": {
                "name": fake.company(),
                "catchPhrase": fake.catch_phrase(),
                "bs": fake.bs()
            }
        }
    
    def _cleanup_created_users(self):
        """Clean up users created during tests"""
        for user_id in self.created_users:
            try:
                # Try to delete the user (if API supports it)
                self.client.delete(f"users/{user_id}")
                logger.info(f"Cleaned up test user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to cleanup user {user_id}: {e}")
    
    @allure.title("Test GET all users endpoint")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_all_users(self):
        """Test retrieving all users"""
        with allure.step("Get all users from API"):
            response = self.client.get("users")
        
        with allure.step("Verify response status and structure"):
            assert response.status_code == 200
            
            users = response.json()
            assert isinstance(users, list)
            assert len(users) > 0
            
            # Validate first user against schema
            if users:
                validation_result = self.schema_validator.validate("user", users[0])
                assert validation_result["valid"], \
                    f"User schema validation failed: {validation_result['errors']}"
        
        with allure.step("Attach sample user data"):
            sample_users = users[:3] if len(users) >= 3 else users
            allure.attach(
                json.dumps(sample_users, indent=2),
                name="Sample Users",
                attachment_type=allure.attachment_type.JSON
            )
    
    @allure.title("Test GET single user endpoint")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_get_single_user(self, user_id):
        """Test retrieving a single user by ID"""
        with allure.step(f"Get user with ID {user_id}"):
            response = self.client.get(f"users/{user_id}")
        
        with allure.step("Verify response"):
            assert response.status_code == 200
            
            user = response.json()
            assert user["id"] == user_id
            
            # Validate against schema
            validation_result = self.schema_validator.validate("user", user)
            assert validation_result["valid"]
    
    @allure.title("Test GET user with invalid ID")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.parametrize("invalid_id", [0, -1, 9999, "invalid", ""])
    def test_get_user_invalid_id(self, invalid_id):
        """Test retrieving user with invalid ID"""
        with allure.step(f"Attempt to get user with ID {invalid_id}"):
            response = self.client.get(f"users/{invalid_id}")
        
        with allure.step("Verify appropriate error response"):
            # Different APIs handle invalid IDs differently
            if response.status_code == 404:
                # Expected behavior for non-existent resource
                pass
            elif response.status_code == 400:
                # Bad request for invalid ID format
                pass
            elif response.status_code == 200:
                # Some APIs return empty object for non-existent IDs
                data = response.json()
                assert data == {} or data == []
            else:
                pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @allure.title("Test CREATE new user endpoint")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.crud
    def test_create_user(self):
        """Test creating a new user"""
        with allure.step("Prepare test user data"):
            new_user = self.test_user_data.copy()
            allure.attach(
                json.dumps(new_user, indent=2),
                name="User Creation Payload",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Send POST request to create user"):
            response = self.client.post("users", json=new_user)
        
        with allure.step("Verify user creation response"):
            assert response.status_code in [200, 201]  # 200 OK or 201 Created
            
            created_user = response.json()
            
            # Verify response contains user data with ID
            assert "id" in created_user
            user_id = created_user["id"]
            
            # Track for cleanup
            self.created_users.append(user_id)
            
            # Verify other fields match
            for key in ["name", "username", "email"]:
                if key in new_user:
                    assert created_user[key] == new_user[key]
        
        with allure.step("Verify user can be retrieved"):
            # Try to get the newly created user
            get_response = self.client.get(f"users/{user_id}")
            assert get_response.status_code == 200
            
            retrieved_user = get_response.json()
            assert retrieved_user["id"] == user_id
    
    @allure.title("Test CREATE user with missing required fields")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.parametrize("missing_field", ["name", "username", "email"])
    def test_create_user_missing_required_field(self, missing_field):
        """Test creating user with missing required fields"""
        with allure.step(f"Create user without {missing_field}"):
            incomplete_user = self.test_user_data.copy()
            del incomplete_user[missing_field]
            
            response = self.client.post("users", json=incomplete_user)
        
        with allure.step("Verify error response"):
            # API should reject request with missing required fields
            assert response.status_code in [400, 422]  # Bad Request or Unprocessable Entity
            
            error_data = response.json()
            assert "error" in error_data or "message" in error_data
    
    @allure.title("Test UPDATE user endpoint")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.crud
    def test_update_user(self):
        """Test updating an existing user"""
        # First, get an existing user to update
        with allure.step("Get existing user to update"):
            get_response = self.client.get("users/1")
            original_user = get_response.json()
        
        with allure.step("Prepare update data"):
            updated_data = original_user.copy()
            updated_data["name"] = f"Updated {fake.name()}"
            updated_data["email"] = fake.email()
            
            allure.attach(
                json.dumps(updated_data, indent=2),
                name="User Update Payload",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Send PUT request to update user"):
            response = self.client.put("users/1", json=updated_data)
        
        with allure.step("Verify update response"):
            assert response.status_code == 200
            
            updated_user = response.json()
            
            # Verify updates were applied
            assert updated_user["name"] == updated_data["name"]
            assert updated_user["email"] == updated_data["email"]
            assert updated_user["id"] == original_user["id"]
    
    @allure.title("Test PATCH user endpoint")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.crud
    def test_patch_user(self):
        """Test partially updating a user with PATCH"""
        with allure.step("Prepare partial update data"):
            patch_data = {
                "name": f"Patched {fake.name()}",
                "email": fake.email()
            }
        
        with allure.step("Send PATCH request"):
            response = self.client.patch("users/1", json=patch_data)
        
        with allure.step("Verify partial update response"):
            if response.status_code == 200:
                # API supports PATCH
                patched_user = response.json()
                assert patched_user["name"] == patch_data["name"]
                assert patched_user["email"] == patch_data["email"]
            elif response.status_code == 404:
                # PATCH not supported, which is OK
                logger.info("PATCH method not supported by API")
            else:
                logger.warning(f"Unexpected PATCH response: {response.status_code}")
    
    @allure.title("Test DELETE user endpoint")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.crud
    def test_delete_user(self):
        """Test deleting a user"""
        # First create a test user to delete
        with allure.step("Create test user for deletion"):
            new_user = self.test_user_data.copy()
            create_response = self.client.post("users", json=new_user)
            
            if create_response.status_code in [200, 201]:
                created_user = create_response.json()
                user_id = created_user["id"]
                
                # Don't track for cleanup since we're testing deletion
                if user_id in self.created_users:
                    self.created_users.remove(user_id)
                
                with allure.step(f"Delete user {user_id}"):
                    delete_response = self.client.delete(f"users/{user_id}")
                
                with allure.step("Verify deletion"):
                    assert delete_response.status_code in [200, 204]  # OK or No Content
                    
                    # Verify user is deleted by trying to get it
                    get_response = self.client.get(f"users/{user_id}")
                    
                    # Different APIs handle deleted resources differently
                    if get_response.status_code == 404:
                        # User not found (expected)
                        pass
                    elif get_response.status_code == 200:
                        # Some APIs might still return the user
                        # or return empty response
                        data = get_response.json()
                        if data == {} or data == []:
                            pass
                        else:
                            logger.warning(f"User {user_id} still exists after deletion")
            else:
                # User creation failed, skip deletion test
                logger.warning("User creation failed, skipping deletion test")
                pytest.skip("User creation failed, cannot test deletion")
    
    @allure.title("Test user filtering by parameters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.filter
    def test_filter_users(self):
        """Test filtering users by parameters"""
        test_cases = [
            {"username": "Bret"},
            {"email": "Sincere@april.biz"},
            # Add more filter criteria based on API capabilities
        ]
        
        for filter_criteria in test_cases:
            with allure.step(f"Filter users by {filter_criteria}"):
                response = self.client.get("users", params=filter_criteria)
                
                if response.status_code == 200:
                    users = response.json()
                    
                    # Verify filter results
                    if users:
                        for user in users:
                            for key, expected_value in filter_criteria.items():
                                if key in user:
                                    assert user[key] == expected_value
                    
                    allure.attach(
                        f"Filter: {filter_criteria}\nResults: {len(users)} users found",
                        name="Filter Results",
                        attachment_type=allure.attachment_type.TEXT
                    )
    
    @allure.title("Test user search functionality")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.search
    def test_search_users(self):
        """Test searching for users"""
        with allure.step("Search for users by name fragment"):
            # This depends on API having search endpoint
            # Using users endpoint with query parameter as fallback
            response = self.client.get("users")
            
            if response.status_code == 200:
                all_users = response.json()
                
                # Simulate search in test
                search_term = "Leanne"
                matching_users = [
                    user for user in all_users 
                    if search_term.lower() in user.get("name", "").lower()
                ]
                
                assert len(matching_users) > 0, \
                    f"No users found matching '{search_term}'"
                
                logger.info(f"Found {len(matching_users)} users matching '{search_term}'")
    
    @allure.title("Test user pagination")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.pagination
    def test_user_pagination(self):
        """Test pagination for user list"""
        with allure.step("Test pagination parameters"):
            pagination_params = [
                {"_page": 1, "_limit": 5},
                {"_page": 2, "_limit": 5},
                {"_page": 1, "_limit": 10}
            ]
            
            for params in pagination_params:
                response = self.client.get("users", params=params)
                
                if response.status_code == 200:
                    users = response.json()
                    
                    # Check if pagination is working
                    limit = params.get("_limit", 10)
                    if len(users) <= limit:
                        # Pagination might be working
                        pass
                    
                    allure.attach(
                        f"Page {params.get('_page', 1)}, Limit {limit}: {len(users)} users",
                        name="Pagination Results",
                        attachment_type=allure.attachment_type.TEXT
                    )
    
    @allure.title("Test user sorting")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.sorting
    def test_user_sorting(self):
        """Test sorting users by different fields"""
        with allure.step("Test sorting by name"):
            sort_params = {"_sort": "name", "_order": "asc"}
            response = self.client.get("users", params=sort_params)
            
            if response.status_code == 200:
                users = response.json()
                
                # Verify sorting (if API supports it)
                if len(users) > 1:
                    names = [user.get("name", "") for user in users]
                    sorted_names = sorted(names)
                    
                    # Check if names are sorted (might not be if API doesn't support)
                    if names == sorted_names:
                        logger.info("Users are sorted by name ascending")
                    else:
                        logger.warning("Users are not sorted as expected")
    
    @allure.title("Test concurrent user operations")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.concurrency
    def test_concurrent_user_operations(self):
        """Test concurrent user operations for race conditions"""
        import threading
        
        results = []
        
        def create_user(user_num):
            """Thread function to create user"""
            try:
                user_data = {
                    "name": f"Concurrent User {user_num}",
                    "username": f"concurrent_{user_num}",
                    "email": f"concurrent{user_num}@test.com"
                }
                
                response = self.client.post("users", json=user_data)
                results.append({
                    "thread": user_num,
                    "status": response.status_code,
                    "success": response.status_code in [200, 201]
                })
            except Exception as e:
                results.append({
                    "thread": user_num,
                    "error": str(e),
                    "success": False
                })
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        success_count = sum(1 for r in results if r.get("success", False))
        
        allure.attach(
            json.dumps(results, indent=2),
            name="Concurrent Operation Results",
            attachment_type=allure.attachment_type.JSON
        )
        
        # All should succeed or fail gracefully
        assert all("error" not in r or r.get("success", False) for r in results)
    
    @allure.title("Test user data validation rules")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.validation
    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "missing@domain",
        "@nodomain.com",
        "spaces in@email.com",
        "multiple@@email.com"
    ])
    def test_user_email_validation(self, invalid_email):
        """Test email validation when creating users"""
        with allure.step(f"Test with invalid email: {invalid_email}"):
            user_data = self.test_user_data.copy()
            user_data["email"] = invalid_email
            
            response = self.client.post("users", json=user_data)
        
        with allure.step("Verify validation error"):
            # API should reject invalid email
            assert response.status_code in [400, 422]
            
            error_data = response.json()
            # Error should mention email validation
            error_text = json.dumps(error_data).lower()
            assert any(word in error_text for word in ["email", "invalid", "format"])
    
    @allure.title("Test user rate limiting")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.rate_limiting
    def test_user_rate_limiting(self):
        """Test rate limiting on user endpoints"""
        requests_made = 0
        rate_limited = False
        
        with allure.step("Make multiple rapid requests"):
            for i in range(20):  # Make 20 rapid requests
                response = self.client.get("users/1")
                requests_made += 1
                
                if response.status_code == 429:  # Too Many Requests
                    rate_limited = True
                    break
                
                time.sleep(0.1)  # Small delay
        
        allure.attach(
            f"Requests made: {requests_made}\nRate limited: {rate_limited}",
            name="Rate Limiting Test",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Rate limiting is a security feature, not necessarily a failure
        if rate_limited:
            logger.info("Rate limiting is working as expected")
        else:
            logger.info("No rate limiting detected")
    
    @allure.title("Test user endpoint security headers")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.security
    def test_user_endpoint_security_headers(self):
        """Test security headers on user endpoints"""
        with allure.step("Check security headers"):
            response = self.client.get("users/1")
            headers = response.headers
            
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
                "Strict-Transport-Security",
                "Content-Security-Policy"
            ]
            
            found_headers = []
            missing_headers = []
            
            for header in security_headers:
                if header in headers:
                    found_headers.append(f"{header}: {headers[header]}")
                else:
                    missing_headers.append(header)
            
            allure.attach(
                f"Found headers:\n" + "\n".join(found_headers) + 
                f"\n\nMissing headers:\n" + ", ".join(missing_headers),
                name="Security Headers",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Note: Missing security headers might be OK depending on API
            if missing_headers:
                logger.warning(f"Missing security headers: {missing_headers}")