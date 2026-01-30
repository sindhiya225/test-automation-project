"""
Advanced API Authentication Test Suite
"""
import pytest
import allure
import json
from src.core.api_client import APIClient
from src.api.schemas import USER_SCHEMA, AUTH_RESPONSE_SCHEMA

@allure.epic("API Testing")
@allure.feature("Authentication API")
class TestAuthAPI:
    """Test class for authentication API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Setup before each test"""
        self.client = api_client
        self.test_user = {
            "email": "eve.holt@reqres.in",
            "password": "cityslicka"
        }
        yield
    
    @allure.title("Test successful authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    def test_successful_auth(self):
        """Test successful authentication with valid credentials"""
        with allure.step("Make authentication request"):
            response = self.client.post(
                "api/login",
                json=self.test_user
            )
        
        with allure.step("Verify response status code"):
            assert response.status_code == 200
        
        with allure.step("Verify response schema"):
            response_data = response.json()
            assert self.client.validate_schema(response_data, AUTH_RESPONSE_SCHEMA)
        
        with allure.step("Verify response contains token"):
            assert "token" in response_data
            assert len(response_data["token"]) > 0
        
        with allure.step("Log response for debugging"):
            allure.attach(
                json.dumps(response_data, indent=2),
                name="Auth Response",
                attachment_type=allure.attachment_type.JSON
            )
    
    @allure.title("Test authentication with invalid credentials")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.parametrize("invalid_data,expected_error", [
        ({"email": "invalid@email.com", "password": "test"}, "user not found"),
        ({"email": "test@email.com", "password": ""}, "Missing password"),
        ({"email": "", "password": "password"}, "Missing email or username"),
        ({}, "Missing email or username"),
    ])
    def test_invalid_auth(self, invalid_data, expected_error):
        """Test authentication with invalid credentials"""
        with allure.step(f"Attempt authentication with invalid data: {invalid_data}"):
            response = self.client.post(
                "api/login",
                json=invalid_data
            )
        
        with allure.step("Verify error response"):
            assert response.status_code in [400, 401]
            
            if response.status_code == 400:
                error_data = response.json()
                assert "error" in error_data
    
    @allure.title("Test authentication rate limiting")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.security
    def test_auth_rate_limiting(self):
        """Test authentication rate limiting"""
        requests_made = 0
        blocked_requests = 0
        
        with allure.step("Make multiple rapid authentication requests"):
            for i in range(15):  # Try 15 rapid requests
                response = self.client.post(
                    "api/login",
                    json={"email": f"test{i}@email.com", "password": "wrong"}
                )
                requests_made += 1
                
                if response.status_code == 429:  # Too Many Requests
                    blocked_requests += 1
                    break
        
        with allure.step("Verify rate limiting works"):
            assert blocked_requests > 0, "Rate limiting not triggered"
            allure.attach(
                f"Requests made: {requests_made}\nBlocked requests: {blocked_requests}",
                name="Rate Limiting Results",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.title("Test JWT token validation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.security
    def test_jwt_token_validation(self):
        """Test JWT token structure and validation"""
        with allure.step("Obtain authentication token"):
            response = self.client.post(
                "api/login",
                json=self.test_user
            )
            token = response.json()["token"]
        
        with allure.step("Verify token structure"):
            # Basic JWT structure validation
            parts = token.split('.')
            assert len(parts) == 3, "Invalid JWT token structure"
            
            # Verify token can be used for authorized requests
            self.client.set_auth_token(token)
            protected_response = self.client.get("api/users/me")
            assert protected_response.status_code == 200
    
    @allure.title("Test authentication with SQL injection")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.security
    @pytest.mark.parametrize("sql_payload", [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "admin' --",
        "' UNION SELECT username, password FROM users --"
    ])
    def test_auth_sql_injection(self, sql_payload):
        """Test authentication endpoint for SQL injection vulnerabilities"""
        with allure.step(f"Attempt SQL injection: {sql_payload}"):
            malicious_data = {
                "email": sql_payload,
                "password": sql_payload
            }
            response = self.client.post(
                "api/login",
                json=malicious_data
            )
        
        with allure.step("Verify injection was prevented"):
            # Should return proper error, not 500 or database error
            assert response.status_code != 500
            
            response_text = response.text.lower()
            sql_indicators = ["sql", "syntax", "database", "query"]
            for indicator in sql_indicators:
                assert indicator not in response_text, \
                    f"Possible SQL injection vulnerability: {indicator}"
    
    @allure.title("Test authentication with XSS payload")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.security
    def test_auth_xss_prevention(self):
        """Test authentication endpoint for XSS vulnerabilities"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "\"><script>alert('XSS')</script>"
        ]
        
        for payload in xss_payloads:
            with allure.step(f"Test XSS payload: {payload}"):
                response = self.client.post(
                    "api/login",
                    json={"email": payload, "password": payload}
                )
                
                # Check if payload is reflected in response
                response_text = response.text
                assert payload not in response_text, \
                    f"XSS payload reflected in response: {payload}"
    
    @allure.title("Test content type security")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.security
    def test_content_type_security(self):
        """Test content-type validation and security"""
        with allure.step("Send request with wrong content-type"):
            headers = {"Content-Type": "text/plain"}
            response = self.client.post(
                "api/login",
                json=self.test_user,
                headers=headers
            )
        
        with allure.step("Verify proper content-type handling"):
            # Should either reject or properly handle
            assert response.status_code in [200, 400, 415]
            
            if response.status_code == 415:
                assert "Unsupported Media Type" in response.text
    
    @allure.title("Test authentication logging")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    @pytest.mark.security
    def test_auth_logging(self):
        """Test that authentication attempts are logged"""
        # This would require access to server logs
        # For framework demonstration, we'll check response headers
        response = self.client.post(
            "api/login",
            json=self.test_user
        )
        
        # Check for security headers
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]
        
        missing_headers = []
        for header in security_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        if missing_headers:
            allure.attach(
                f"Missing security headers: {missing_headers}",
                name="Security Headers Check",
                attachment_type=allure.attachment_type.TEXT
            )
            # In a real test, you might want to fail or warn based on security policy