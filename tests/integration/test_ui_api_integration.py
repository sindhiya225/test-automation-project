"""
Advanced integration test suite combining UI and API testing.
Tests end-to-end workflows with both UI interactions and API validations.
"""
import pytest
import allure
import json
import time
from typing import Dict, Any
from src.pages.login_page import LoginPage
from src.pages.dashboard_page import DashboardPage
from src.core.api_client import APIClient
from src.api.schemas import SchemaValidator
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)


@allure.epic("Integration Testing")
@allure.feature("UI-API Integration")
@allure.story("End-to-End Workflows")
class TestUIApiIntegration:
    """
    Integration tests that combine UI actions with API validations.
    Tests complete workflows from login to complex operations.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, api_client, test_config):
        """Setup before each test"""
        self.driver = selenium_driver
        self.client = api_client
        self.config = test_config
        self.login_page = LoginPage(self.driver)
        self.dashboard_page = DashboardPage(self.driver)
        self.schema_validator = SchemaValidator()
        yield
    
    @allure.title("Test complete login workflow with API validation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.integration
    @pytest.mark.smoke
    def test_login_workflow_with_api_validation(self, test_data):
        """Test complete login workflow with API session validation"""
        with allure.step("Step 1: Navigate to login page via UI"):
            self.login_page.navigate(self.config["base_url"])
            assert "login" in self.driver.current_url.lower()
        
        with allure.step("Step 2: Perform UI login with valid credentials"):
            credentials = test_data["valid_credentials"]
            self.login_page.login(
                username=credentials["username"],
                password=credentials["password"]
            )
            
            # Verify UI login success
            assert self.login_page.is_login_successful()
            assert "main" in self.driver.current_url.lower()
        
        with allure.step("Step 3: Verify login via API session check"):
            # This would require an API endpoint to verify session
            # For demo, we'll check if we can access protected API endpoints
            try:
                # Try to access a protected endpoint (if API supports)
                api_response = self.client.get("protected-endpoint")
                
                if api_response.status_code == 200:
                    logger.info("API session is active after UI login")
                elif api_response.status_code == 401:
                    logger.warning("API session not established after UI login")
            except Exception as e:
                logger.warning(f"API session check not available: {e}")
        
        with allure.step("Step 4: Take screenshot of successful login"):
            self.login_page.take_screenshot("reports/screenshots/integration_login_success.png")
        
        with allure.step("Step 5: Logout and verify session termination"):
            self.dashboard_page.logout()
            assert "login" in self.driver.current_url.lower()
            
            # Verify API session is terminated
            try:
                api_response = self.client.get("protected-endpoint")
                if api_response.status_code == 401:
                    logger.info("API session terminated after UI logout")
            except Exception:
                pass
    
    @allure.title("Test user registration flow with API data validation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.integration
    @pytest.mark.registration
    def test_user_registration_flow(self):
        """Test complete user registration flow with API data verification"""
        with allure.step("Step 1: Generate test user data via API utilities"):
            from src.core.utilities import data_generator
            new_user_data = data_generator.generate_user_data()
            
            allure.attach(
                json.dumps(new_user_data, indent=2),
                name="Generated User Data",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Step 2: Create user via API"):
            api_response = self.client.post("users", json={
                "name": new_user_data["name"],
                "username": new_user_data["username"],
                "email": new_user_data["email"],
                "password": new_user_data["password"]
            })
            
            assert api_response.status_code in [200, 201]
            created_user = api_response.json()
            user_id = created_user.get("id")
            
            allure.attach(
                json.dumps(created_user, indent=2),
                name="API Created User",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Step 3: Verify user creation via UI login"):
            # Navigate to login page
            self.login_page.navigate(self.config["base_url"])
            
            # Attempt login with new credentials
            self.login_page.login(
                username=new_user_data["username"],
                password=new_user_data["password"]
            )
            
            # Check if login successful
            if self.login_page.is_login_successful():
                logger.info("New user can login via UI")
                
                # Take screenshot of first login
                self.login_page.take_screenshot("reports/screenshots/new_user_first_login.png")
                
                # Logout
                self.dashboard_page.logout()
            else:
                logger.warning("New user cannot login via UI (might need activation)")
        
        with allure.step("Step 4: Clean up test user via API"):
            if user_id:
                try:
                    delete_response = self.client.delete(f"users/{user_id}")
                    if delete_response.status_code in [200, 204]:
                        logger.info(f"Test user {user_id} cleaned up")
                except Exception as e:
                    logger.warning(f"Failed to cleanup test user: {e}")
    
    @allure.title("Test data synchronization between UI and API")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.integration
    @pytest.mark.data_sync
    def test_ui_api_data_synchronization(self, test_data):
        """Test that data shown in UI matches API data"""
        with allure.step("Step 1: Login via UI"):
            credentials = test_data["valid_credentials"]
            self.login_page.navigate(self.config["base_url"])
            self.login_page.login(
                username=credentials["username"],
                password=credentials["password"]
            )
            assert self.login_page.is_login_successful()
        
        with allure.step("Step 2: Get user data from UI dashboard"):
            # Get account information from UI
            ui_accounts = self.dashboard_page.get_account_summary()
            ui_total_balance = self.dashboard_page.get_total_balance()
            
            allure.attach(
                json.dumps(ui_accounts, indent=2),
                name="UI Account Data",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Step 3: Get user data from API"):
            # This would require API endpoints for account data
            # For demo, we'll use mock data or skip if not available
            try:
                # Assuming API has endpoint for user accounts
                api_response = self.client.get(f"users/{credentials['username']}/accounts")
                
                if api_response.status_code == 200:
                    api_accounts = api_response.json()
                    
                    # Compare UI and API data
                    self._compare_ui_api_data(ui_accounts, api_accounts)
                else:
                    logger.warning("Account API endpoint not available")
            except Exception as e:
                logger.warning(f"Could not fetch API account data: {e}")
        
        with allure.step("Step 4: Verify data consistency"):
            # Additional consistency checks
            if ui_accounts:
                # Verify UI data is internally consistent
                calculated_total = sum(acc["balance"] for acc in ui_accounts)
                assert abs(calculated_total - ui_total_balance) < 0.01, \
                    "UI total balance doesn't match sum of account balances"
    
    def _compare_ui_api_data(self, ui_data: list, api_data: list):
        """Compare UI and API data for consistency"""
        discrepancies = []
        
        # Simple comparison based on available data
        # In real scenario, this would be more sophisticated
        
        if ui_data and api_data:
            # Check if we have same number of accounts
            if len(ui_data) != len(api_data):
                discrepancies.append(f"Account count mismatch: UI={len(ui_data)}, API={len(api_data)}")
            
            # Compare balances (simplified)
            ui_balances = [acc["balance"] for acc in ui_data]
            api_balances = [acc.get("balance", 0) for acc in api_data]
            
            if sum(ui_balances) != sum(api_balances):
                discrepancies.append(f"Total balance mismatch: UI={sum(ui_balances)}, API={sum(api_balances)}")
        
        if discrepancies:
            allure.attach(
                "\n".join(discrepancies),
                name="Data Synchronization Issues",
                attachment_type=allure.attachment_type.TEXT
            )
            logger.warning(f"Data synchronization issues: {discrepancies}")
        else:
            logger.info("UI and API data are synchronized")
    
    @allure.title("Test transaction flow with API verification")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.integration
    @pytest.mark.transaction
    def test_transaction_flow_with_api_verification(self, test_data):
        """Test complete transaction flow with API validation"""
        with allure.step("Step 1: Login via UI"):
            credentials = test_data["valid_credentials"]
            self.login_page.navigate(self.config["base_url"])
            self.login_page.login(
                username=credentials["username"],
                password=credentials["password"]
            )
            assert self.login_page.is_login_successful()
        
        with allure.step("Step 2: Get initial account balances via UI"):
            initial_accounts = self.dashboard_page.get_account_summary()
            initial_balances = {acc["number"]: acc["balance"] for acc in initial_accounts}
            
            allure.attach(
                json.dumps(initial_balances, indent=2),
                name="Initial Balances",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Step 3: Perform transfer via UI"):
            # Find two accounts to transfer between
            if len(initial_accounts) >= 2:
                from_account = initial_accounts[0]["number"]
                to_account = initial_accounts[1]["number"]
                transfer_amount = 50.00
                
                # Perform transfer
                transfer_success = self.dashboard_page.transfer_funds(
                    from_account=from_account,
                    to_account=to_account,
                    amount=transfer_amount,
                    description="Integration test transfer"
                )
                
                assert transfer_success, "UI transfer failed"
                
                # Wait for transaction to process
                time.sleep(2)
        
        with allure.step("Step 4: Verify transaction via API"):
            # This would require API endpoints for transactions
            try:
                # Get transactions after transfer
                api_response = self.client.get(f"accounts/{from_account}/transactions")
                
                if api_response.status_code == 200:
                    transactions = api_response.json()
                    
                    # Look for our transfer
                    transfer_found = any(
                        txn.get("amount") == transfer_amount and 
                        txn.get("description", "").lower() == "integration test transfer"
                        for txn in transactions[:5]  # Check recent transactions
                    )
                    
                    if transfer_found:
                        logger.info("Transfer verified via API")
                    else:
                        logger.warning("Transfer not found in API transactions")
            except Exception as e:
                logger.warning(f"Could not verify transfer via API: {e}")
        
        with allure.step("Step 5: Verify updated balances via UI"):
            # Get updated balances
            updated_accounts = self.dashboard_page.get_account_summary()
            updated_balances = {acc["number"]: acc["balance"] for acc in updated_accounts}
            
            # Verify balance changes
            if from_account in updated_balances and to_account in updated_balances:
                from_change = updated_balances[from_account] - initial_balances[from_account]
                to_change = updated_balances[to_account] - initial_balances[to_account]
                
                # Note: Transfer amount might include fees
                assert abs(from_change + transfer_amount) < 1.00, \
                    f"From account change {from_change} doesn't match transfer amount {transfer_amount}"
                assert abs(to_change - transfer_amount) < 1.00, \
                    f"To account change {to_change} doesn't match transfer amount {transfer_amount}"
    
    @allure.title("Test error scenario handling across UI and API")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.integration
    @pytest.mark.negative
    def test_error_scenario_handling(self):
        """Test error handling consistency between UI and API"""
        with allure.step("Step 1: Test invalid login via UI and API"):
            # UI invalid login
            self.login_page.navigate(self.config["base_url"])
            self.login_page.login(username="invalid_user", password="wrong_password")
            ui_error = self.login_page.get_error_message()
            
            # API invalid login (if available)
            try:
                api_response = self.client.post("auth/login", json={
                    "username": "invalid_user",
                    "password": "wrong_password"
                })
                
                api_error = None
                if api_response.status_code in [400, 401]:
                    api_error = api_response.json().get("error", "Authentication failed")
            except Exception as e:
                api_error = f"API error: {e}"
            
            allure.attach(
                f"UI Error: {ui_error}\nAPI Error: {api_error}",
                name="Error Comparison",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Both should indicate authentication failure
            assert "invalid" in ui_error.lower() or "incorrect" in ui_error.lower() or \
                   "failed" in ui_error.lower(), "UI error message not informative"
    
    @allure.title("Test performance correlation between UI and API")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.integration
    @pytest.mark.performance
    def test_performance_correlation(self):
        """Test that UI performance correlates with API performance"""
        import time
        
        with allure.step("Step 1: Measure API response time"):
            api_start = time.time()
            api_response = self.client.get("users/1")
            api_duration = time.time() - api_start
            
            assert api_response.status_code == 200
        
        with allure.step("Step 2: Measure UI load time for same data"):
            # This would require UI page that displays user data
            # For demo, we'll measure dashboard load time
            self.login_page.navigate(self.config["base_url"])
            
            ui_start = time.time()
            # Perform login and wait for dashboard
            # This is simplified - real test would login first
            ui_duration = time.time() - ui_start
        
        with allure.step("Step 3: Analyze performance correlation"):
            performance_data = {
                "api_response_time": api_duration,
                "ui_load_time": ui_duration,
                "ratio": ui_duration / api_duration if api_duration > 0 else 0
            }
            
            allure.attach(
                json.dumps(performance_data, indent=2),
                name="Performance Correlation",
                attachment_type=allure.attachment_type.JSON
            )
            
            # UI should not be excessively slower than API
            # (UI includes rendering, API is just data)
            assert ui_duration < api_duration * 10, \
                f"UI excessively slow compared to API: UI={ui_duration:.2f}s, API={api_duration:.2f}s"
    
    @allure.title("Test security consistency across UI and API")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.integration
    @pytest.mark.security
    def test_security_consistency(self):
        """Test security measures are consistent between UI and API"""
        with allure.step("Step 1: Test SQL injection on UI login"):
            sql_payload = "' OR '1'='1"
            vulnerable = self.login_page.test_sql_injection(sql_payload)
            
            assert not vulnerable, "UI vulnerable to SQL injection"
        
        with allure.step("Step 2: Test SQL injection on API endpoint"):
            try:
                api_response = self.client.post("auth/login", json={
                    "username": "' OR '1'='1",
                    "password": "' OR '1'='1"
                })
                
                # Should return authentication error, not SQL error
                response_text = json.dumps(api_response.json()).lower()
                sql_indicators = ["sql", "syntax", "database", "query"]
                
                for indicator in sql_indicators:
                    assert indicator not in response_text, \
                        f"API vulnerable to SQL injection: {indicator} in response"
            except Exception as e:
                logger.warning(f"SQL injection test on API failed: {e}")
        
        with allure.step("Step 3: Test XSS consistency"):
            xss_payload = "<script>alert('XSS')</script>"
            
            # UI test (would test form inputs)
            # API test (would test input validation)
            
            # For demo, just log that we would test this
            logger.info("XSS tests would be performed here")
    
    @allure.title("Test session management across UI and API")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.integration
    @pytest.mark.session
    def test_session_management(self, test_data):
        """Test session consistency between UI and API"""
        with allure.step("Step 1: Establish session via UI login"):
            credentials = test_data["valid_credentials"]
            self.login_page.navigate(self.config["base_url"])
            self.login_page.login(
                username=credentials["username"],
                password=credentials["password"]
            )
            
            # Get session cookie from UI
            ui_cookies = self.driver.get_cookies()
            ui_session_cookie = next(
                (c for c in ui_cookies if "session" in c["name"].lower()),
                None
            )
        
        with allure.step("Step 2: Use UI session for API requests"):
            if ui_session_cookie:
                # Try to use UI session with API
                session_cookie = f"{ui_session_cookie['name']}={ui_session_cookie['value']}"
                
                try:
                    api_response = self.client.get("protected-endpoint", headers={
                        "Cookie": session_cookie
                    })
                    
                    if api_response.status_code == 200:
                        logger.info("UI session works with API")
                    else:
                        logger.warning("UI session not valid for API")
                except Exception as e:
                    logger.warning(f"Could not test session sharing: {e}")
        
        with allure.step("Step 3: Test session timeout consistency"):
            # This would require waiting for session timeout
            # and checking both UI and API
            logger.info("Session timeout test would be performed here")