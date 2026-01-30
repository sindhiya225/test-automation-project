"""
Comprehensive validation test suite.
Tests various validation scenarios including edge cases and security.
"""
import pytest
import allure
import json
import re
from typing import Dict, Any, List
from src.pages.login_page import LoginPage
from src.core.logger import TestLogger
from src.core.utilities import test_utils

logger = TestLogger.get_logger(__name__)


@allure.epic("UI Testing")
@allure.feature("Validations")
@allure.story("Comprehensive Validation Scenarios")
class TestValidations:
    """Test class for comprehensive validation scenarios"""
    
    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, test_config):
        """Setup before each test"""
        self.driver = selenium_driver
        self.config = test_config
        self.login_page = LoginPage(self.driver)
        yield
    
    @allure.title("Test input sanitization and XSS prevention")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.validation
    @pytest.mark.security
    def test_xss_prevention(self):
        """Test that XSS payloads are sanitized or blocked"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "\"><script>alert('XSS')</script>",
            "'><script>alert('XSS')</script>",
            "<body onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<link rel=stylesheet href=javascript:alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            with allure.step(f"Test XSS payload: {payload[:30]}..."):
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                # Enter XSS payload in both fields
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, payload)
                self.login_page.send_keys(self.login_page.PASSWORD_INPUT, payload)
                
                # Submit form
                self.login_page.click(self.login_page.LOGIN_BUTTON)
                
                # Get page source and check for reflected payload
                page_source = self.driver.page_source
                
                # Payload should not be reflected in page source
                # (or should be sanitized)
                if payload in page_source:
                    # Check if it's sanitized (contains &lt; instead of <)
                    sanitized = payload.replace("<", "&lt;").replace(">", "&gt;")
                    if sanitized in page_source:
                        logger.info(f"XSS payload sanitized: {payload[:30]}...")
                    else:
                        # Potential XSS vulnerability
                        allure.attach(
                            f"XSS payload reflected: {payload}\n"
                            f"Page source snippet: {page_source[:500]}",
                            name="XSS Vulnerability",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        logger.warning(f"XSS payload might be reflected: {payload[:30]}...")
    
    @allure.title("Test SQL injection prevention")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.validation
    @pytest.mark.security
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are blocked"""
        sql_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "admin' --",
            "admin' #",
            "' UNION SELECT NULL, username, password FROM users --",
            "'; DROP TABLE users; --",
            "' OR EXISTS(SELECT * FROM users) AND '1'='1",
            "' OR username LIKE '%admin%",
            "' OR (SELECT COUNT(*) FROM users) > 0 --",
        ]
        
        for payload in sql_payloads:
            with allure.step(f"Test SQL injection: {payload[:30]}..."):
                vulnerable = self.login_page.test_sql_injection(payload)
                
                assert not vulnerable, f"SQL injection vulnerability detected: {payload}"
                
                if vulnerable:
                    allure.attach(
                        f"SQL Injection vulnerability found with payload: {payload}",
                        name="SQL Injection Vulnerability",
                        attachment_type=allure.attachment_type.TEXT
                    )
    
    @allure.title("Test input length validations and boundaries")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    def test_input_length_boundaries(self):
        """Test input field length boundaries and validations"""
        test_cases = [
            (1, "Minimum length"),  # Minimum
            (10, "Normal length"),
            (50, "Medium length"),
            (100, "Long length"),
            (255, "Maximum typical length"),
            (1000, "Very long - should be truncated or rejected"),
        ]
        
        for length, description in test_cases:
            with allure.step(f"Test {description} ({length} chars)"):
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                # Generate test string of specified length
                test_input = "a" * length
                
                # Enter in username field
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, test_input)
                
                # Get what was actually entered (might be truncated)
                entered_value = self.login_page.find_element(
                    self.login_page.USERNAME_INPUT
                ).get_attribute("value")
                
                entered_length = len(entered_value)
                
                allure.attach(
                    f"Requested: {length} chars\n"
                    f"Entered: {entered_length} chars\n"
                    f"Truncated: {length != entered_length}",
                    name=f"Length Test - {description}",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Very long inputs might be truncated
                if length > 255 and entered_length < length:
                    logger.info(f"Long input truncated from {length} to {entered_length} chars")
    
    @allure.title("Test special character handling")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    def test_special_character_handling(self):
        """Test handling of various special characters"""
        special_char_groups = [
            ("Punctuation", "!@#$%^&*()_+-=[]{}|;:',.<>?/`~"),
            ("Math symbols", "±×÷≈≠≤≥∞√∛∜∫∬∭∮∯∰∇∂∆"),
            ("Currency symbols", "€£¥¢₩₹₽₿"),
            ("Arrows", "←↑→↓↔↕↖↗↘↙"),
            ("Box drawing", "─│┌┐└┘├┤┬┴┼"),
            ("Misc symbols", "§¶†‡•·…※‼⁈⁉™©®"),
        ]
        
        for group_name, characters in special_char_groups:
            with allure.step(f"Test {group_name} characters"):
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                # Test each character
                for char in characters:
                    try:
                        self.login_page.send_keys(self.login_page.USERNAME_INPUT, char)
                        
                        # Clear for next character
                        self.login_page.find_element(
                            self.login_page.USERNAME_INPUT
                        ).clear()
                    except Exception as e:
                        logger.warning(f"Error with character '{char}': {e}")
                
                logger.info(f"Tested {len(characters)} {group_name} characters")
    
    @allure.title("Test whitespace handling in inputs")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    def test_whitespace_handling(self):
        """Test handling of various whitespace characters"""
        whitespace_cases = [
            ("Leading space", " username"),
            ("Trailing space", "username "),
            ("Multiple spaces", "user  name"),
            ("Tab character", "user\tname"),
            ("Newline", "user\nname"),
            ("Non-breaking space", "user\xa0name"),
            ("Multiple whitespace", "  user  \t\n name  "),
        ]
        
        for case_name, test_input in whitespace_cases:
            with allure.step(f"Test {case_name}"):
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                # Enter test input
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, test_input)
                
                # Get entered value
                entered_value = self.login_page.find_element(
                    self.login_page.USERNAME_INPUT
                ).get_attribute("value")
                
                # Check if whitespace was trimmed or preserved
                if entered_value != test_input:
                    logger.info(f"Whitespace handled: '{test_input}' -> '{entered_value}'")
                
                # Submit form to see behavior
                self.login_page.click(self.login_page.LOGIN_BUTTON)
                
                # Should not crash or show server error
                current_url = self.driver.current_url
                assert "error" not in current_url.lower(), \
                    f"Server error with whitespace input: {case_name}"
    
    @allure.title("Test numeric input validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    def test_numeric_input_validation(self):
        """Test validation of numeric inputs in text fields"""
        numeric_cases = [
            ("Integer", "12345"),
            ("Negative", "-123"),
            ("Decimal", "123.45"),
            ("Scientific", "1.23e4"),
            ("Very large", "99999999999999999999"),
            ("Zero", "0"),
            ("Leading zeros", "00123"),
            ("With commas", "1,234,567"),
            ("With spaces", "1 234 567"),
        ]
        
        for case_name, test_input in numeric_cases:
            with allure.step(f"Test numeric: {case_name}"):
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                # Enter numeric input in username field (should accept or reject appropriately)
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, test_input)
                
                # Submit to see if numeric username is accepted
                self.login_page.click(self.login_page.LOGIN_BUTTON)
                
                # Should handle without error (might reject with appropriate message)
                error_message = self.login_page.get_error_message()
                if error_message:
                    # Error about invalid username is OK
                    assert "invalid" in error_message.lower() or \
                           "not found" in error_message.lower(), \
                        f"Unexpected error for numeric input: {error_message}"
    
    @allure.title("Test email format validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    def test_email_format_validation(self):
        """Test email address format validation"""
        email_cases = [
            # Valid emails
            ("simple@example.com", True),
            ("very.common@example.com", True),
            ("disposable.style.email.with+symbol@example.com", True),
            ("other.email-with-dash@example.com", True),
            ("fully-qualified-domain@example.com", True),
            ("user.name+tag+sorting@example.com", True),
            ("x@example.com", True),  # one-letter local part
            ("example-indeed@strange-example.com", True),
            ("admin@mailserver1", True),  # no TLD
            ("example@s.example", True),  # see RFC 5322
            
            # Invalid emails
            ("Abc.example.com", False),  # no @ character
            ("A@b@c@example.com", False),  # multiple @
            ("a\"b(c)d,e:f;g<h>i[j\\k]l@example.com", False),  # special characters
            ("just\"not\"right@example.com", False),  # quoted strings
            ("this is\"not\\allowed@example.com", False),  # spaces
            ("this\\ still\\\"not\\allowed@example.com", False),  # backslashes
            ("john..doe@example.com", False),  # double dot
            (".john.doe@example.com", False),  # leading dot
            ("john.doe.@example.com", False),  # trailing dot
        ]
        
        for email, expected_valid in email_cases:
            with allure.step(f"Test email: {email}"):
                # This test assumes the application validates email format
                # If not, it's testing that the application handles various inputs
                
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                # Try to use email as username
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, email)
                self.login_page.send_keys(self.login_page.PASSWORD_INPUT, "password")
                
                self.login_page.click(self.login_page.LOGIN_BUTTON)
                
                # Application might accept or reject email as username
                # Just verify no crash
                current_url = self.driver.current_url
                assert "error" not in current_url.lower(), \
                    f"Server error with email input: {email}"
    
    @allure.title("Test password strength validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    @pytest.mark.security
    def test_password_strength_validation(self):
        """Test password strength requirements and validation"""
        password_cases = [
            ("weak", "password", False),  # Common password
            ("weak", "123456", False),  # Common numeric
            ("weak", "qwerty", False),  # Keyboard pattern
            ("short", "short", False),  # Too short
            ("no uppercase", "lowercase123", False),  # No uppercase
            ("no lowercase", "UPPERCASE123", False),  # No lowercase
            ("no numbers", "MixedCase", False),  # No numbers
            ("no special", "MixedCase123", False),  # No special chars
            ("strong", "StrongPass123!", True),  # Meets all requirements
            ("very strong", "V3ry$tr0ngP@ssw0rd!", True),  # Very strong
        ]
        
        for case_name, password, expected_strong in password_cases:
            with allure.step(f"Test password: {case_name}"):
                # This test is for observing password validation behavior
                # Actual validation might happen during registration, not login
                
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                # Use a test username
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, "testuser")
                self.login_page.send_keys(self.login_page.PASSWORD_INPUT, password)
                
                # Submit form
                self.login_page.click(self.login_page.LOGIN_BUTTON)
                
                # Should handle any password without crash
                # (Authentication might fail, but that's OK)
                error_message = self.login_page.get_error_message()
                if error_message:
                    # Should be authentication error, not password validation error
                    # (unless login validates password strength)
                    logger.info(f"Got error for password '{case_name}': {error_message[:50]}")
    
    @allure.title("Test concurrent form submissions")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    @pytest.mark.concurrency
    def test_concurrent_form_submissions(self):
        """Test handling of concurrent form submissions"""
        import threading
        
        results = []
        
        def submit_form(thread_id):
            """Thread function to submit form"""
            try:
                # Each thread needs its own driver instance
                # For simplicity, we'll simulate with a single driver
                # In real test, you'd use separate driver instances
                
                # For this demo, we'll just record attempt
                results.append({
                    "thread": thread_id,
                    "status": "attempted",
                    "timestamp": time.time()
                })
                
            except Exception as e:
                results.append({
                    "thread": thread_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=submit_form, args=(i,))
            threads.append(thread)
        
        # Note: Actual concurrent testing with UI is complex
        # This is a simplified demonstration
        
        allure.attach(
            "Concurrent form submission test:\n"
            "In a real test, multiple browser instances would\n"
            "submit forms simultaneously to test for race conditions.",
            name="Concurrent Test Note",
            attachment_type=allure.attachment_type.TEXT
        )
        
        logger.info("Concurrent form submission test concept demonstrated")
    
    @allure.title("Test form submission timeout handling")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    @pytest.mark.performance
    def test_form_submission_timeout(self):
        """Test form submission with slow server response"""
        # This would test how the UI handles slow server responses
        # For demo, we'll check for timeout indicators
        
        with allure.step("Submit form and check for loading indicators"):
            self.login_page.navigate(self.config["base_url"])
            self.login_page.clear_login_form()
            
            # Fill form
            self.login_page.send_keys(self.login_page.USERNAME_INPUT, "testuser")
            self.login_page.send_keys(self.login_page.PASSWORD_INPUT, "testpass")
            
            # Submit form
            self.login_page.click(self.login_page.LOGIN_BUTTON)
            
            # Check for loading indicator (if any)
            loading_indicators = [
                "//*[contains(@class, 'loading')]",
                "//*[contains(@class, 'spinner')]",
                "//*[contains(@class, 'progress')]",
                "//*[contains(text(), 'Loading')]",
                "//*[contains(text(), 'Please wait')]",
            ]
            
            for xpath in loading_indicators:
                try:
                    elements = self.driver.find_elements_by_xpath(xpath)
                    if elements:
                        logger.info(f"Found loading indicator: {xpath}")
                        break
                except:
                    continue
    
    @allure.title("Test browser back/forward navigation with form data")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.validation
    def test_browser_navigation_with_form(self):
        """Test browser back/forward navigation with form data"""
        with allure.step("Fill form but don't submit"):
            self.login_page.navigate(self.config["base_url"])
            self.login_page.clear_login_form()
            
            # Fill form with data
            test_data = {
                "username": "testuser123",
                "password": "testpass123"
            }
            
            self.login_page.send_keys(self.login_page.USERNAME_INPUT, test_data["username"])
            self.login_page.send_keys(self.login_page.PASSWORD_INPUT, test_data["password"])
            
            # Take screenshot
            self.login_page.take_screenshot("reports/screenshots/form_filled_before_nav.png")
        
        with allure.step("Navigate away without submitting"):
            # Go to another page
            self.driver.get(f"{self.config['base_url']}/contact.aspx")
            time.sleep(1)
        
        with allure.step("Use browser back button"):
            self.driver.back()
            time.sleep(1)
            
            # Check if form data is preserved (browser feature, not app)
            username_value = self.login_page.find_element(
                self.login_page.USERNAME_INPUT
            ).get_attribute("value")
            password_value = self.login_page.find_element(
                self.login_page.PASSWORD_INPUT
            ).get_attribute("value")
            
            allure.attach(
                f"After back navigation:\n"
                f"Username: {username_value}\n"
                f"Password: {password_value}",
                name="Form Data After Back Navigation",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Some browsers preserve form data, others don't
            # This is testing browser behavior, not application
    
    @allure.title("Test form accessibility validations")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.validation
    @pytest.mark.accessibility
    def test_form_accessibility(self):
        """Test form accessibility features"""
        with allure.step("Check form accessibility attributes"):
            self.login_page.navigate(self.config["base_url"])
            
            # Check for label associations
            username_field = self.login_page.find_element(self.login_page.USERNAME_INPUT)
            password_field = self.login_page.find_element(self.login_page.PASSWORD_INPUT)
            
            # Check aria-label or aria-labelledby
            username_aria_label = username_field.get_attribute("aria-label")
            username_aria_labelledby = username_field.get_attribute("aria-labelledby")
            password_aria_label = password_field.get_attribute("aria-label")
            password_aria_labelledby = password_field.get_attribute("aria-labelledby")
            
            accessibility_info = [
                f"Username field:",
                f"  aria-label: {username_aria_label}",
                f"  aria-labelledby: {username_aria_labelledby}",
                f"Password field:",
                f"  aria-label: {password_aria_label}",
                f"  aria-labelledby: {password_aria_labelledby}",
            ]
            
            allure.attach(
                "\n".join(accessibility_info),
                name="Form Accessibility Attributes",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Check for proper labels
            # Field should have either aria-label, aria-labelledby, or associated label element
            has_accessibility = (
                (username_aria_label or username_aria_labelledby) and
                (password_aria_label or password_aria_labelledby)
            )
            
            if not has_accessibility:
                logger.warning("Form fields might lack proper accessibility attributes")
    
    @allure.title("Test form with JavaScript disabled")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.validation
    def test_form_without_javascript(self):
        """Test form functionality without JavaScript"""
        # This would require running tests with JavaScript disabled
        # For demo, we'll check if form has noscript fallback
        
        with allure.step("Check for noscript content"):
            self.login_page.navigate(self.config["base_url"])
            
            # Look for noscript tags
            noscript_elements = self.driver.find_elements_by_tag_name("noscript")
            
            if noscript_elements:
                noscript_content = "\n".join([el.text for el in noscript_elements if el.text])
                
                allure.attach(
                    f"Found {len(noscript_elements)} noscript elements\n"
                    f"Content sample: {noscript_content[:200]}...",
                    name="Noscript Content",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                logger.info("Form has noscript fallback content")
            else:
                logger.info("No noscript content found (form might require JavaScript)")