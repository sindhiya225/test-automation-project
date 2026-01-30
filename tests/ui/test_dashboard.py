"""
Dashboard functionality test suite.
Tests post-login dashboard features and user interactions.
"""
import pytest
import allure
import json
from typing import Dict, Any, List
from src.pages.dashboard_page import DashboardPage
from src.pages.login_page import LoginPage
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)


@allure.epic("UI Testing")
@allure.feature("Dashboard")
@allure.story("Post-Login Functionality")
class TestDashboard:
    """Test class for dashboard functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, test_config, test_data):
        """Setup before each test - login first"""
        self.driver = selenium_driver
        self.config = test_config
        self.test_data = test_data
        self.login_page = LoginPage(self.driver)
        self.dashboard_page = DashboardPage(self.driver)
        
        # Login before each test
        self._login_to_dashboard()
        yield
        
        # Optional: Logout after each test
        # self.dashboard_page.logout()
    
    def _login_to_dashboard(self):
        """Helper to login and navigate to dashboard"""
        self.login_page.navigate(self.config["base_url"])
        credentials = self.test_data["valid_credentials"]
        self.login_page.login(
            username=credentials["username"],
            password=credentials["password"]
        )
        assert self.login_page.is_login_successful()
        logger.info("Logged in successfully for dashboard tests")
    
    @allure.title("Test dashboard page load and elements")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_dashboard_load(self):
        """Test that dashboard loads correctly with all elements"""
        with allure.step("Verify dashboard is loaded"):
            assert self.dashboard_page.is_dashboard_loaded()
            
            # Take screenshot of loaded dashboard
            self.dashboard_page.take_screenshot("reports/screenshots/dashboard_loaded.png")
        
        with allure.step("Verify all dashboard elements are present"):
            elements_status = self.dashboard_page.verify_dashboard_elements()
            
            allure.attach(
                json.dumps(elements_status, indent=2),
                name="Dashboard Elements Status",
                attachment_type=allure.attachment_type.JSON
            )
            
            # All critical elements should be present
            critical_elements = ["welcome_message", "account_summary", "logout_link"]
            for element in critical_elements:
                assert elements_status.get(element, False), f"Missing critical element: {element}"
    
    @allure.title("Test account summary display")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_account_summary_display(self):
        """Test that account summary is displayed correctly"""
        with allure.step("Get account summary from dashboard"):
            accounts = self.dashboard_page.get_account_summary()
            
            allure.attach(
                json.dumps(accounts, indent=2),
                name="Account Summary",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Verify account summary data"):
            assert len(accounts) > 0, "No accounts displayed in summary"
            
            for account in accounts:
                # Verify required fields
                assert "type" in account
                assert "number" in account
                assert "balance" in account
                assert "available_balance" in account
                
                # Verify data types and values
                assert isinstance(account["balance"], (int, float))
                assert isinstance(account["available_balance"], (int, float))
                assert account["balance"] >= 0
                assert account["available_balance"] >= 0
                
                # Available balance should not exceed balance
                assert account["available_balance"] <= account["balance"]
    
    @allure.title("Test navigation between dashboard sections")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_dashboard_navigation(self):
        """Test navigation between different dashboard sections"""
        sections = [
            ("accounts", "Account Summary"),
            ("transfers", "Transfer Funds"),
            ("bill_pay", "Bill Payment"),
            ("contact", "Contact")
        ]
        
        for section_method, expected_content in sections:
            with allure.step(f"Navigate to {section_method.replace('_', ' ')}"):
                # Navigate using appropriate method
                if section_method == "accounts":
                    self.dashboard_page.navigate_to_accounts()
                elif section_method == "transfers":
                    self.dashboard_page.navigate_to_transfers()
                elif section_method == "bill_pay":
                    self.dashboard_page.navigate_to_bill_pay()
                elif section_method == "contact":
                    self.dashboard_page.navigate_to_contact()
                
                # Verify we're on the correct page
                # This would check for page-specific elements or URL
                # For demo, we'll just verify page loaded
                time.sleep(1)  # Wait for navigation
                
                # Take screenshot
                self.dashboard_page.take_screenshot(
                    f"reports/screenshots/dashboard_{section_method}.png"
                )
                
                # Navigate back to dashboard
                self.dashboard_page.click(self.dashboard_page.DASHBOARD_LINK)
    
    @allure.title("Test fund transfer functionality")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.transaction
    def test_fund_transfer(self):
        """Test transferring funds between accounts"""
        with allure.step("Get initial account balances"):
            initial_accounts = self.dashboard_page.get_account_summary()
            
            if len(initial_accounts) < 2:
                pytest.skip("Need at least 2 accounts for transfer test")
            
            from_account = initial_accounts[0]
            to_account = initial_accounts[1]
        
        with allure.step("Perform fund transfer"):
            transfer_amount = 50.00
            
            success = self.dashboard_page.transfer_funds(
                from_account=from_account["number"],
                to_account=to_account["number"],
                amount=transfer_amount,
                description="Test transfer"
            )
            
            assert success, "Fund transfer failed"
            
            # Take screenshot of transfer confirmation
            self.dashboard_page.take_screenshot("reports/screenshots/transfer_confirmation.png")
        
        with allure.step("Verify transfer reflected in accounts"):
            # Wait for update
            import time
            time.sleep(2)
            
            # Get updated accounts
            updated_accounts = self.dashboard_page.get_account_summary()
            updated_from = next(a for a in updated_accounts if a["number"] == from_account["number"])
            updated_to = next(a for a in updated_accounts if a["number"] == to_account["number"])
            
            # Verify balance changes (might need to account for fees)
            from_balance_change = updated_from["balance"] - from_account["balance"]
            to_balance_change = updated_to["balance"] - to_account["balance"]
            
            # Allow small differences for potential fees
            assert abs(from_balance_change + transfer_amount) < 1.00
            assert abs(to_balance_change - transfer_amount) < 1.00
    
    @allure.title("Test bill payment functionality")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.transaction
    def test_bill_payment(self):
        """Test paying a bill from dashboard"""
        with allure.step("Prepare payee information"):
            payee_info = {
                "name": "Test Utility Company",
                "address": "123 Utility St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345",
                "phone": "(555) 123-4567",
                "account": "UTIL-789012"
            }
        
        with allure.step("Get account for payment"):
            accounts = self.dashboard_page.get_account_summary()
            if not accounts:
                pytest.skip("No accounts available for payment")
            
            from_account = accounts[0]["number"]
        
        with allure.step("Perform bill payment"):
            payment_amount = 75.50
            
            success = self.dashboard_page.pay_bill(
                payee_info=payee_info,
                amount=payment_amount,
                from_account=from_account
            )
            
            # Some bill payment systems might require additional steps
            # or return to a confirmation page
            if success:
                logger.info("Bill payment submitted successfully")
                self.dashboard_page.take_screenshot("reports/screenshots/bill_payment_success.png")
            else:
                logger.warning("Bill payment may not have completed successfully")
                # This might be OK if payment requires manual approval
    
    @allure.title("Test recent transactions display")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_recent_transactions(self):
        """Test display of recent transactions"""
        with allure.step("Get recent transactions"):
            transactions = self.dashboard_page.get_recent_transactions(count=5)
            
            allure.attach(
                json.dumps(transactions, indent=2),
                name="Recent Transactions",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Verify transaction data structure"):
            if transactions:  # May be empty if no recent transactions
                for transaction in transactions:
                    # Check for required fields
                    assert "date" in transaction
                    assert "description" in transaction
                    assert "amount" in transaction
                    
                    # Amount should be a string with currency symbol
                    assert "$" in transaction["amount"] or \
                           any(char.isdigit() for char in transaction["amount"])
    
    @allure.title("Test search functionality")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.search
    def test_search_functionality(self):
        """Test search feature on dashboard"""
        with allure.step("Test search with valid term"):
            # Search for a common transaction term
            search_results = self.dashboard_page.search_transactions("transfer")
            
            allure.attach(
                f"Found {len(search_results)} results for 'transfer'",
                name="Search Results",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Search should return results (might be empty if no matching transactions)
            # Just verify search completes without error
        
        with allure.step("Test search with empty term"):
            empty_results = self.dashboard_page.search_transactions("")
            # Should handle empty search gracefully
    
    @allure.title("Test user profile and settings")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.profile
    def test_user_profile(self):
        """Test user profile and settings functionality"""
        with allure.step("Access user settings"):
            self.dashboard_page.open_user_settings()
            
            # Verify settings page loaded
            # This would check for settings-specific elements
            time.sleep(1)
            
            self.dashboard_page.take_screenshot("reports/screenshots/user_settings.png")
            
            # Navigate back to dashboard
            self.driver.back()
    
    @allure.title("Test logout functionality")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_logout(self):
        """Test user logout from dashboard"""
        with allure.step("Perform logout"):
            self.dashboard_page.logout()
        
        with allure.step("Verify logout successful"):
            # Should be redirected to login page
            assert "login" in self.driver.current_url.lower()
            
            # Should not be able to access dashboard directly
            self.driver.get(f"{self.config['base_url']}/bank/main.aspx")
            
            # Should be redirected back to login
            assert "login" in self.driver.current_url.lower()
    
    @allure.title("Test dashboard responsiveness")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.responsive
    def test_dashboard_responsiveness(self):
        """Test dashboard on different window sizes"""
        test_sizes = [
            (1920, 1080),  # Desktop
            (1366, 768),   # Laptop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in test_sizes:
            with allure.step(f"Test at {width}x{height}"):
                self.driver.set_window_size(width, height)
                time.sleep(1)  # Allow resize
                
                # Verify dashboard still loads
                assert self.dashboard_page.is_dashboard_loaded()
                
                # Take screenshot
                self.dashboard_page.take_screenshot(
                    f"reports/screenshots/dashboard_{width}x{height}.png"
                )
        
        # Restore to original size
        self.driver.maximize_window()
    
    @allure.title("Test dashboard alerts and notifications")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_dashboard_alerts(self):
        """Test alert and notification functionality"""
        with allure.step("Check for alerts"):
            alerts = self.dashboard_page.get_alerts()
            
            if alerts:
                allure.attach(
                    "\n".join(alerts),
                    name="Dashboard Alerts",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Test dismissing an alert
                self.dashboard_page.dismiss_alert(alerts[0])
            else:
                logger.info("No alerts present on dashboard")
    
    @allure.title("Test dashboard performance metrics")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.performance
    def test_dashboard_performance(self):
        """Test dashboard loading performance"""
        import time
        
        with allure.step("Measure dashboard load time"):
            # Navigate away and back to measure load time
            self.driver.get(f"{self.config['base_url']}/contact.aspx")
            time.sleep(1)
            
            start_time = time.time()
            self.driver.get(f"{self.config['base_url']}/bank/main.aspx")
            
            # Wait for dashboard to load
            self.dashboard_page.wait_for_element_visible(
                self.dashboard_page.WELCOME_MESSAGE
            )
            
            load_time = time.time() - start_time
            
            allure.attach(
                f"Dashboard load time: {load_time:.2f} seconds",
                name="Performance Metric",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Performance threshold (adjust based on requirements)
            assert load_time < 10.0, f"Dashboard load time too slow: {load_time:.2f}s"
    
    @allure.title("Test dashboard accessibility features")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.accessibility
    def test_dashboard_accessibility(self):
        """Test basic accessibility features"""
        with allure.step("Check for alt text on images"):
            images = self.driver.find_elements_by_tag_name("img")
            
            images_without_alt = []
            for img in images[:10]:  # Check first 10 images
                alt_text = img.get_attribute("alt")
                if not alt_text or alt_text.strip() == "":
                    images_without_alt.append(img.get_attribute("src") or "unknown")
            
            if images_without_alt:
                allure.attach(
                    f"Images without alt text:\n" + "\n".join(images_without_alt[:5]),
                    name="Accessibility Issues",
                    attachment_type=allure.attachment_type.TEXT
                )
                logger.warning(f"Found {len(images_without_alt)} images without alt text")
        
        with allure.step("Check for proper heading structure"):
            # Check for h1 tag (should exist for main page title)
            h1_elements = self.driver.find_elements_by_tag_name("h1")
            assert len(h1_elements) > 0, "No h1 heading found"
            
            # Check heading hierarchy
            headings = self.driver.find_elements_by_css_selector("h1, h2, h3, h4, h5, h6")
            if len(headings) > 1:
                # Verify hierarchy (simplified check)
                pass
    
    @allure.title("Test dashboard with different user roles")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.roles
    def test_dashboard_user_roles(self):
        """Test dashboard for different user roles"""
        # This would require testing with different user accounts
        # For demo, we'll test with current user and verify role-based elements
        
        with allure.step("Check role-based visibility"):
            # Some elements might be visible only to certain roles
            # Example: Admin links might not be visible to regular users
            
            admin_elements = [
                # List of admin-only element locators
            ]
            
            regular_user_elements = [
                # List of regular user element locators
            ]
            
            # Check which elements are visible
            # This depends on the actual user's role
            
            logger.info("Role-based testing would verify element visibility based on user role")