"""
Login Page Object Model with advanced authentication scenarios
"""
from typing import Tuple
from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)

class LoginPage(BasePage):
    """Login Page with comprehensive test scenarios"""
    
    # Locators
    USERNAME_INPUT = (By.ID, "uid")
    PASSWORD_INPUT = (By.ID, "passw")
    LOGIN_BUTTON = (By.NAME, "btnSubmit")
    ERROR_MESSAGE = (By.ID, "_ctl0__ctl0_Content_Main_message")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot password?")
    REMEMBER_ME_CHECKBOX = (By.ID, "rememberMe")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success")
    
    # Page URL
    URL = "/login.aspx"
    
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
    
    def navigate(self, base_url: str):
        """Navigate to login page"""
        full_url = f"{base_url.rstrip('/')}{self.URL}"
        self.driver.get(full_url)
        logger.info(f"Navigated to login page: {full_url}")
    
    def login(self, username: str, password: str, remember_me: bool = False):
        """Perform login with given credentials"""
        logger.info(f"Attempting login with username: {username}")
        
        self.send_keys(self.USERNAME_INPUT, username)
        self.send_keys(self.PASSWORD_INPUT, password)
        
        if remember_me:
            checkbox = self.find_element(self.REMEMBER_ME_CHECKBOX)
            if not checkbox.is_selected():
                checkbox.click()
        
        self.click(self.LOGIN_BUTTON)
        
        # Wait for page to load
        time.sleep(2)  # In real framework, use proper wait conditions
    
    def get_error_message(self) -> str:
        """Get error message if login fails"""
        if self.is_element_present(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    
    def is_login_successful(self) -> bool:
        """Check if login was successful"""
        # Check URL change or presence of dashboard element
        return "main.aspx" in self.driver.current_url
    
    def click_forgot_password(self):
        """Click forgot password link"""
        self.click(self.FORGOT_PASSWORD_LINK)
    
    def clear_login_form(self):
        """Clear login form fields"""
        username_field = self.find_element(self.USERNAME_INPUT)
        password_field = self.find_element(self.PASSWORD_INPUT)
        
        username_field.clear()
        password_field.clear()
    
    def get_form_validation_errors(self) -> dict:
        """Get form validation errors"""
        errors = {}
        
        # Check for HTML5 validation
        username_field = self.find_element(self.USERNAME_INPUT)
        password_field = self.find_element(self.PASSWORD_INPUT)
        
        if username_field.get_attribute("required"):
            errors['username'] = "Username is required"
        
        if password_field.get_attribute("required"):
            errors['password'] = "Password is required"
        
        # Check for custom validation messages
        validation_messages = self.find_elements((By.CLASS_NAME, "validation-error"))
        for msg in validation_messages:
            field = msg.get_attribute("data-field")
            errors[field] = msg.text
        
        return errors
    
    def test_sql_injection(self, malicious_input: str) -> bool:
        """Test for SQL injection vulnerability"""
        self.send_keys(self.USERNAME_INPUT, malicious_input)
        self.send_keys(self.PASSWORD_INPUT, malicious_input)
        self.click(self.LOGIN_BUTTON)
        
        # Check for database error messages
        page_source = self.get_page_source().lower()
        sql_error_indicators = [
            "sql", "syntax", "database", "query", "mysql", "postgresql",
            "ora-", "invalid column", "unclosed quotation"
        ]
        
        for indicator in sql_error_indicators:
            if indicator in page_source:
                logger.warning(f"Possible SQL injection vulnerability detected: {indicator}")
                return True
        
        return False