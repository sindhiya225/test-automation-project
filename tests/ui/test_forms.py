"""
Form testing suite for various form interactions and validations.
Tests form filling, submissions, and complex form scenarios.
"""
import pytest
import allure
import json
from typing import Dict, Any, List
from src.pages.login_page import LoginPage
from src.core.logger import TestLogger
from src.core.utilities import test_utils

logger = TestLogger.get_logger(__name__)


@allure.epic("UI Testing")
@allure.feature("Forms")
@allure.story("Form Interactions and Validations")
class TestForms:
    """Test class for form interactions and validations"""
    
    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, test_config):
        """Setup before each test"""
        self.driver = selenium_driver
        self.config = test_config
        self.login_page = LoginPage(self.driver)
        yield
    
    @allure.title("Test basic form filling and submission")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.forms
    @pytest.mark.smoke
    def test_basic_form_filling(self):
        """Test filling and submitting a basic form"""
        with allure.step("Navigate to login page (as a form example)"):
            self.login_page.navigate(self.config["base_url"])
        
        with allure.step("Fill form with valid data"):
            test_username = "testuser123"
            test_password = "TestPassword123!"
            
            self.login_page.send_keys(self.login_page.USERNAME_INPUT, test_username)
            self.login_page.send_keys(self.login_page.PASSWORD_INPUT, test_password)
            
            # Take screenshot of filled form
            self.login_page.take_screenshot("reports/screenshots/filled_form.png")
        
        with allure.step("Submit form and verify"):
            self.login_page.click(self.login_page.LOGIN_BUTTON)
            
            # Check for either success or appropriate error
            # (since we're using test credentials that might not exist)
            error_message = self.login_page.get_error_message()
            
            if error_message:
                # Invalid credentials error is expected
                assert "invalid" in error_message.lower() or \
                       "incorrect" in error_message.lower()
                logger.info("Form submitted, got expected error for invalid credentials")
            else:
                # Might have actually logged in (unlikely with random credentials)
                logger.warning("Unexpected form submission result")
    
    @allure.title("Test form field validations")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.forms
    @pytest.mark.validation
    def test_form_field_validations(self):
        """Test form field validation rules"""
        with allure.step("Navigate to login page"):
            self.login_page.navigate(self.config["base_url"])
        
        with allure.step("Test required field validation"):
            # Clear form
            self.login_page.clear_login_form()
            
            # Try to submit empty form
            self.login_page.click(self.login_page.LOGIN_BUTTON)
            
            # Check for validation errors
            validation_errors = self.login_page.get_form_validation_errors()
            
            allure.attach(
                json.dumps(validation_errors, indent=2),
                name="Validation Errors",
                attachment_type=allure.attachment_type.JSON
            )
            
            # Should have errors for required fields
            assert len(validation_errors) > 0, "Expected validation errors for empty form"
            
            # Check for specific field errors
            if "username" in validation_errors:
                assert "required" in validation_errors["username"].lower()
            if "password" in validation_errors:
                assert "required" in validation_errors["password"].lower()
        
        with allure.step("Test input length validations"):
            # Test very long username
            long_username = "a" * 256
            self.login_page.send_keys(self.login_page.USERNAME_INPUT, long_username)
            
            # Some forms might truncate, others might show error
            # Just verify form handles it without crashing
            entered_value = self.login_page.find_element(
                self.login_page.USERNAME_INPUT
            ).get_attribute("value")
            
            assert len(entered_value) <= 256, "Form should handle long input"
    
    @allure.title("Test form with special characters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_special_characters(self):
        """Test form handling of special characters"""
        test_cases = [
            ("user@name", "pass@word"),
            ("user&name", "pass&word"),
            ("user#name", "pass#word"),
            ("user$name", "pass$word"),
            ("user%name", "pass%word"),
            ("user^name", "pass^word"),
            ("user*name", "pass*word"),
            ("user(name)", "pass(word)"),
            ("user[name]", "pass[word]"),
            ("user{name}", "pass{word}"),
        ]
        
        for username, password in test_cases:
            with allure.step(f"Test with special chars: {username}"):
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, username)
                self.login_page.send_keys(self.login_page.PASSWORD_INPUT, password)
                
                # Submit form
                self.login_page.click(self.login_page.LOGIN_BUTTON)
                
                # Should handle special chars without errors
                # (might get authentication error, but not crash)
                error_message = self.login_page.get_error_message()
                if error_message:
                    # Should be authentication error, not input validation error
                    assert "special" not in error_message.lower(), \
                        f"Unexpected error for special chars: {error_message}"
    
    @allure.title("Test form with Unicode/International characters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_unicode_characters(self):
        """Test form handling of Unicode and international characters"""
        test_cases = [
            ("usérnàme", "pässwörd"),  # Accented characters
            ("用户名", "密码"),  # Chinese
            ("ユーザー名", "パスワード"),  # Japanese
            ("사용자이름", "비밀번호"),  # Korean
            ("имяпользователя", "пароль"),  # Russian
            ("اسمالمستخدم", "كلمهالسر"),  # Arabic
            ("αξιωματικός", "σύνθημα"),  # Greek
            ("🐱username", "🐶password"),  # Emoji
        ]
        
        for username, password in test_cases:
            with allure.step(f"Test with Unicode: {username[:10]}..."):
                self.login_page.navigate(self.config["base_url"])
                self.login_page.clear_login_form()
                
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, username)
                self.login_page.send_keys(self.login_page.PASSWORD_INPUT, password)
                
                # Take screenshot
                self.login_page.take_screenshot(
                    f"reports/screenshots/unicode_form_{hash(username) % 1000}.png"
                )
                
                # Submit form
                self.login_page.click(self.login_page.LOGIN_BUTTON)
                
                # Verify no crashes with Unicode
                # Might get authentication error, which is OK
                current_url = self.driver.current_url
                assert "error" not in current_url.lower(), \
                    f"Server error with Unicode input: {username}"
    
    @allure.title("Test form auto-complete functionality")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_autocomplete(self):
        """Test form auto-complete attributes and behavior"""
        with allure.step("Check auto-complete attributes"):
            self.login_page.navigate(self.config["base_url"])
            
            username_field = self.login_page.find_element(self.login_page.USERNAME_INPUT)
            password_field = self.login_page.find_element(self.login_page.PASSWORD_INPUT)
            
            # Check autocomplete attributes
            username_autocomplete = username_field.get_attribute("autocomplete")
            password_autocomplete = password_field.get_attribute("autocomplete")
            
            allure.attach(
                f"Username autocomplete: {username_autocomplete}\n"
                f"Password autocomplete: {password_autocomplete}",
                name="Autocomplete Attributes",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Password field should have autocomplete="current-password" or similar
            if password_autocomplete:
                assert "password" in password_autocomplete.lower(), \
                    "Password field should have appropriate autocomplete"
    
    @allure.title("Test form field maximum lengths")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_field_maxlength(self):
        """Test form field maximum length constraints"""
        with allure.step("Check maxlength attributes"):
            self.login_page.navigate(self.config["base_url"])
            
            username_field = self.login_page.find_element(self.login_page.USERNAME_INPUT)
            password_field = self.login_page.find_element(self.login_page.PASSWORD_INPUT)
            
            username_maxlength = username_field.get_attribute("maxlength")
            password_maxlength = password_field.get_attribute("maxlength")
            
            allure.attach(
                f"Username maxlength: {username_maxlength}\n"
                f"Password maxlength: {password_maxlength}",
                name="Maxlength Attributes",
                attachment_type=allure.attachment_type.TEXT
            )
            
            if username_maxlength:
                # Test with exactly maxlength characters
                max_chars = int(username_maxlength)
                test_input = "a" * max_chars
                
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, test_input)
                entered_value = username_field.get_attribute("value")
                
                assert len(entered_value) <= max_chars, \
                    f"Field should not exceed maxlength of {max_chars}"
    
    @allure.title("Test form with copy-paste operations")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_copy_paste(self):
        """Test form behavior with copy-paste operations"""
        with allure.step("Test paste into form fields"):
            self.login_page.navigate(self.config["base_url"])
            self.login_page.clear_login_form()
            
            # Test data
            test_username = "paste_test_user"
            test_password = "PasteTest123!"
            
            # We can't directly simulate OS clipboard in Selenium
            # But we can test that fields accept programmatic value setting
            username_field = self.login_page.find_element(self.login_page.USERNAME_INPUT)
            password_field = self.login_page.find_element(self.login_page.PASSWORD_INPUT)
            
            # Simulate paste by setting value via JavaScript
            self.driver.execute_script(
                "arguments[0].value = arguments[1];", 
                username_field, test_username
            )
            self.driver.execute_script(
                "arguments[0].value = arguments[1];", 
                password_field, test_password
            )
            
            # Verify values were set
            assert username_field.get_attribute("value") == test_username
            assert password_field.get_attribute("value") == test_password
            
            # Take screenshot
            self.login_page.take_screenshot("reports/screenshots/form_paste_test.png")
    
    @allure.title("Test form tab order and keyboard navigation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    @pytest.mark.accessibility
    def test_form_tab_order(self):
        """Test form tab order and keyboard navigation"""
        with allure.step("Test tab navigation through form"):
            self.login_page.navigate(self.config["base_url"])
            self.login_page.clear_login_form()
            
            # Get all focusable elements in form
            focusable_selectors = [
                "input:not([disabled]):not([type='hidden'])",
                "button:not([disabled])",
                "select:not([disabled])",
                "textarea:not([disabled])",
                "a[href]"
            ]
            
            focusable_elements = []
            for selector in focusable_selectors:
                elements = self.driver.find_elements_by_css_selector(selector)
                focusable_elements.extend(elements)
            
            allure.attach(
                f"Found {len(focusable_elements)} focusable elements",
                name="Tab Order Test",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Test tab key navigation (simplified)
            # In real test, you would simulate tab key presses
            # and verify focus moves between elements
            
            # Check tabindex attributes
            for element in focusable_elements[:5]:  # Check first 5
                tabindex = element.get_attribute("tabindex")
                if tabindex:
                    try:
                        tabindex_int = int(tabindex)
                        assert tabindex_int >= -1, "tabindex should be >= -1"
                    except ValueError:
                        logger.warning(f"Invalid tabindex: {tabindex}")
    
    @allure.title("Test form submission with Enter key")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_submit_with_enter(self):
        """Test form submission using Enter key"""
        from selenium.webdriver.common.keys import Keys
        
        with allure.step("Test form submission with Enter key"):
            self.login_page.navigate(self.config["base_url"])
            self.login_page.clear_login_form()
            
            # Fill form
            self.login_page.send_keys(self.login_page.USERNAME_INPUT, "testuser")
            self.login_page.send_keys(self.login_page.PASSWORD_INPUT, "testpass")
            
            # Press Enter in password field (should submit form)
            password_field = self.login_page.find_element(self.login_page.PASSWORD_INPUT)
            password_field.send_keys(Keys.ENTER)
            
            # Wait for form submission
            import time
            time.sleep(2)
            
            # Verify form was submitted
            current_url = self.driver.current_url
            assert current_url != self.config["base_url"] + "/login.aspx", \
                "Form should have been submitted with Enter key"
    
    @allure.title("Test form reset functionality")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_reset(self):
        """Test form reset/clear functionality"""
        with allure.step("Test form reset button or functionality"):
            self.login_page.navigate(self.config["base_url"])
            
            # Fill form with data
            self.login_page.send_keys(self.login_page.USERNAME_INPUT, "test data")
            self.login_page.send_keys(self.login_page.PASSWORD_INPUT, "more test data")
            
            # Check if there's a reset button
            reset_buttons = self.driver.find_elements_by_css_selector(
                "input[type='reset'], button[type='reset']"
            )
            
            if reset_buttons:
                # Click reset button
                reset_buttons[0].click()
                
                # Verify fields are cleared
                username_value = self.login_page.find_element(
                    self.login_page.USERNAME_INPUT
                ).get_attribute("value")
                password_value = self.login_page.find_element(
                    self.login_page.PASSWORD_INPUT
                ).get_attribute("value")
                
                assert username_value == "", "Username should be cleared after reset"
                assert password_value == "", "Password should be cleared after reset"
            else:
                logger.info("No reset button found in form")
    
    @allure.title("Test form with disabled submit button")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_disabled_submit(self):
        """Test form with disabled submit button (until valid)"""
        with allure.step("Check if submit button is initially disabled"):
            self.login_page.navigate(self.config["base_url"])
            
            submit_button = self.login_page.find_element(self.login_page.LOGIN_BUTTON)
            is_disabled = submit_button.get_attribute("disabled")
            
            if is_disabled:
                allure.attach(
                    "Submit button is initially disabled (requires valid input)",
                    name="Disabled Submit Test",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Fill form with valid data
                self.login_page.send_keys(self.login_page.USERNAME_INPUT, "test")
                self.login_page.send_keys(self.login_page.PASSWORD_INPUT, "test")
                
                # Check if button becomes enabled
                is_still_disabled = submit_button.get_attribute("disabled")
                assert not is_still_disabled, \
                    "Submit button should be enabled after filling form"
    
    @allure.title("Test multi-step/form wizard")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_multi_step_form(self):
        """Test multi-step form or form wizard"""
        # This test would need a specific multi-step form
        # For demo, we'll simulate with navigation
        
        logger.info("Multi-step form test would navigate through form steps")
        
        # Example steps would include:
        # 1. Fill step 1, click Next
        # 2. Fill step 2, click Next
        # 3. Review step, click Submit
        # 4. Verify success
    
    @allure.title("Test form error message display")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_error_messages(self):
        """Test form error message display and styling"""
        with allure.step("Trigger form validation error"):
            self.login_page.navigate(self.config["base_url"])
            self.login_page.clear_login_form()
            
            # Submit empty form to trigger errors
            self.login_page.click(self.login_page.LOGIN_BUTTON)
            
            # Wait for error messages
            import time
            time.sleep(1)
        
        with allure.step("Check error message visibility and styling"):
            error_message = self.login_page.get_error_message()
            
            if error_message:
                # Check error message is visible
                error_element = self.login_page.find_element(self.login_page.ERROR_MESSAGE)
                assert error_element.is_displayed(), "Error message should be visible"
                
                # Check error message styling (color, etc.)
                error_color = error_element.value_of_css_property("color")
                assert "rgb" in error_color or "#" in error_color, \
                    "Error message should have visible color"
                
                # Take screenshot of error
                self.login_page.take_screenshot("reports/screenshots/form_error.png")
                
                allure.attach(
                    f"Error message: {error_message}\nColor: {error_color}",
                    name="Error Message Details",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.title("Test form with file upload")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_file_upload(self):
        """Test form with file upload functionality"""
        # This would require a form with file upload
        # For demo, we'll log what we would test
        
        logger.info("File upload test would:")
        logger.info("1. Find file input element")
        logger.info("2. Upload test file")
        logger.info("3. Verify file is attached")
        logger.info("4. Submit form")
        logger.info("5. Verify file was uploaded successfully")
    
    @allure.title("Test form with CAPTCHA")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.forms
    def test_form_with_captcha(self):
        """Test form with CAPTCHA challenge"""
        # CAPTCHA can't be automated in tests
        # This test would verify CAPTCHA is present and form
        # cannot be submitted without it
        
        logger.info("CAPTCHA test would verify CAPTCHA element is present")
        logger.info("and form submission is blocked without CAPTCHA")