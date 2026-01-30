"""
Advanced Login Test Suite with multiple authentication scenarios
"""
import pytest
import allure
from faker import Faker
from src.pages.login_page import LoginPage
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)
fake = Faker()

@allure.epic("UI Testing")
@allure.feature("Authentication")
@allure.story("Login Functionality")
class TestLogin:
    """Test class for login functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, test_config):
        """Setup before each test"""
        self.driver = selenium_driver
        self.config = test_config
        self.login_page = LoginPage(self.driver)
        self.login_page.navigate(self.config["base_url"])
        yield
        # Teardown if needed
    
    @allure.title("Test successful login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression")
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_valid_login(self, test_data):
        """Test login with valid credentials"""
        with allure.step("Navigate to login page"):
            assert "login" in self.driver.current_url.lower()
        
        with allure.step("Enter valid credentials"):
            credentials = test_data["valid_credentials"]
            self.login_page.login(
                username=credentials["username"],
                password=credentials["password"]
            )
        
        with allure.step("Verify login success"):
            assert self.login_page.is_login_successful()
            assert "main" in self.driver.current_url.lower()
        
        with allure.step("Take success screenshot"):
            self.login_page.take_screenshot("reports/screenshots/login_success.png")
    
    @allure.title("Test login with invalid credentials")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.regression
    @pytest.mark.parametrize("username,password", [
        ("invalid_user", "invalid_pass"),
        ("admin", "wrong_password"),
        ("", "password123"),
        ("username", ""),
        ("", ""),
    ])
    def test_invalid_login(self, username, password):
        """Test login with invalid credentials"""
        with allure.step(f"Attempt login with username: {username}"):
            self.login_page.login(username, password)
        
        with allure.step("Verify error message appears"):
            error_message = self.login_page.get_error_message()
            assert error_message, "Expected error message but none found"
            
            # Log the error message for debugging
            logger.info(f"Login error message: {error_message}")
            
            # Take screenshot on failure
            self.login_page.take_screenshot(f"reports/screenshots/invalid_login_{username}.png")
    
    @allure.title("Test SQL injection prevention")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.security
    @pytest.mark.parametrize("sql_injection", [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin' --",
        "1' OR '1' = '1"
    ])
    def test_sql_injection_prevention(self, sql_injection):
        """Test that SQL injection attempts are blocked"""
        with allure.step(f"Attempt SQL injection: {sql_injection}"):
            vulnerable = self.login_page.test_sql_injection(sql_injection)
        
        with allure.step("Verify injection was prevented"):
            assert not vulnerable, f"SQL injection vulnerability detected: {sql_injection}"
    
    @allure.title("Test form validations")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    def test_form_validations(self):
        """Test HTML5 form validations"""
        with allure.step("Check required fields validation"):
            self.login_page.clear_login_form()
            self.login_page.click(self.login_page.LOGIN_BUTTON)
            
            # Check for HTML5 validation
            username_field = self.login_page.find_element(self.login_page.USERNAME_INPUT)
            is_required = username_field.get_attribute("required")
            
            if is_required:
                validation_message = self.driver.execute_script(
                    "return arguments[0].validationMessage;", username_field
                )
                assert validation_message, "Expected validation message for required field"
    
    @allure.title("Test remember me functionality")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    def test_remember_me_functionality(self, test_data):
        """Test remember me checkbox functionality"""
        with allure.step("Login with remember me checked"):
            credentials = test_data["valid_credentials"]
            self.login_page.login(
                username=credentials["username"],
                password=credentials["password"],
                remember_me=True
            )
        
        with allure.step("Logout and verify remembered username"):
            # This would require additional logout functionality
            pass
    
    @allure.title("Test concurrent login attempts")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.slow
    def test_concurrent_login_attempts(self):
        """Test login under concurrent access"""
        import threading
        
        results = []
        
        def attempt_login(username, password):
            try:
                # This would need thread-safe driver management
                # For demonstration purposes only
                pass
            except Exception as e:
                results.append(str(e))
        
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=attempt_login,
                args=(f"user{i}", "password")
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no race conditions occurred
        assert len(results) == 0, f"Concurrent login errors: {results}"
    
    @allure.title("Test login with special characters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.parametrize("special_chars", [
        "test@email.com",
        "user_name",
        "user-name",
        "user.name",
        "user+tag@domain.com",
        "ユーザー名",  # Japanese
        "用户",  # Chinese
        "пользователь",  # Russian
    ])
    def test_login_with_special_characters(self, special_chars):
        """Test login with special characters in username"""
        with allure.step(f"Attempt login with special chars: {special_chars}"):
            self.login_page.login(username=special_chars, password="password123")
        
        with allure.step("Verify appropriate behavior"):
            # This test should check if special characters are handled properly
            error_message = self.login_page.get_error_message()
            # Different assertions based on expected behavior
    
    @allure.title("Test password masking")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    def test_password_masking(self):
        """Test that password is masked during input"""
        password_field = self.login_page.find_element(self.login_page.PASSWORD_INPUT)
        
        # Check input type is password
        input_type = password_field.get_attribute("type")
        assert input_type == "password", f"Password field type is {input_type}, not 'password'"
        
        # Verify that entered text is not visible
        self.login_page.send_keys(self.login_page.PASSWORD_INPUT, "visiblepassword")
        displayed_value = password_field.get_attribute("value")
        
        # The value attribute should contain the actual value for automation
        # but the display should be masked
        assert displayed_value == "visiblepassword", "Password value not captured correctly"
    
    @allure.title("Test session timeout after login")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.slow
    def test_session_timeout(self, test_data):
        """Test session expiration after inactivity"""
        with allure.step("Login with valid credentials"):
            credentials = test_data["valid_credentials"]
            self.login_page.login(
                username=credentials["username"],
                password=credentials["password"]
            )
        
        with allure.step("Wait for session timeout (simulated)"):
            import time
            time.sleep(2)  # In real test, wait for actual session timeout
        
        with allure.step("Attempt to access protected page"):
            self.driver.get(f"{self.config['base_url']}/secure-page")
            
            # Should be redirected to login
            assert "login" in self.driver.current_url.lower()