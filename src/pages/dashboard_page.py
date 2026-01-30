"""
Dashboard Page Object Model for post-login functionality.
Contains comprehensive dashboard interactions and validations.
"""
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from src.pages.base_page import BasePage
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)


class DashboardPage(BasePage):
    """
    Dashboard Page Object Model.
    Represents the main dashboard after successful login.
    """
    
    # Navigation locators
    DASHBOARD_LINK = (By.ID, "MenuHyperLink1")
    ACCOUNTS_LINK = (By.ID, "MenuHyperLink2")
    TRANSFERS_LINK = (By.ID, "MenuHyperLink3")
    BILL_PAY_LINK = (By.ID, "MenuHyperLink4")
    CONTACT_LINK = (By.ID, "MenuHyperLink5")
    LOGOUT_LINK = (By.ID, "MenuHyperLink6")
    
    # Dashboard elements
    WELCOME_MESSAGE = (By.CSS_SELECTOR, ".welcome-message")
    ACCOUNT_SUMMARY_TABLE = (By.ID, "accountTable")
    ACCOUNT_BALANCES = (By.CLASS_NAME, "balance")
    RECENT_TRANSACTIONS = (By.ID, "transactionsTable")
    
    # Account summary locators
    ACCOUNT_ROWS = (By.XPATH, "//table[@id='accountTable']//tr[position()>1]")
    ACCOUNT_TYPE_COL = (By.XPATH, "./td[1]")
    ACCOUNT_NUMBER_COL = (By.XPATH, "./td[2]")
    BALANCE_COL = (By.XPATH, "./td[3]")
    AVAILABLE_BALANCE_COL = (By.XPATH, "./td[4]")
    
    # Quick actions
    QUICK_TRANSFER_BUTTON = (By.ID, "quickTransfer")
    QUICK_PAYMENT_BUTTON = (By.ID, "quickPayment")
    VIEW_STATEMENT_BUTTON = (By.ID, "viewStatement")
    
    # Transfer funds locators
    TRANSFER_FROM_DROPDOWN = (By.ID, "fromAccount")
    TRANSFER_TO_DROPDOWN = (By.ID, "toAccount")
    TRANSFER_AMOUNT_INPUT = (By.ID, "transferAmount")
    TRANSFER_DESCRIPTION_INPUT = (By.ID, "description")
    TRANSFER_SUBMIT_BUTTON = (By.ID, "transferButton")
    TRANSFER_SUCCESS_MESSAGE = (By.ID, "_ctl0__ctl0_Content_Main_postResp")
    
    # Bill payment locators
    PAYEE_NAME_INPUT = (By.ID, "payeeName")
    PAYEE_ADDRESS_INPUT = (By.ID, "payeeAddress")
    PAYEE_CITY_INPUT = (By.ID, "payeeCity")
    PAYEE_STATE_INPUT = (By.ID, "payeeState")
    PAYEE_ZIP_INPUT = (By.ID, "payeeZip")
    PAYEE_PHONE_INPUT = (By.ID, "payeePhone")
    PAYEE_ACCOUNT_INPUT = (By.ID, "payeeAccount")
    PAYEE_VERIFY_ACCOUNT_INPUT = (By.ID, "verifyAccount")
    PAYEE_AMOUNT_INPUT = (By.ID, "amount")
    PAYEE_FROM_ACCOUNT_DROPDOWN = (By.ID, "fromAccount")
    PAYEE_SUBMIT_BUTTON = (By.ID, "submitButton")
    
    # Alerts and notifications
    ALERT_MESSAGE = (By.CLASS_NAME, "alert")
    NOTIFICATION_BELL = (By.ID, "notificationBell")
    NOTIFICATION_LIST = (By.ID, "notificationList")
    
    # Search functionality
    SEARCH_INPUT = (By.ID, "searchInput")
    SEARCH_BUTTON = (By.ID, "searchButton")
    SEARCH_RESULTS = (By.ID, "searchResults")
    
    # User profile
    USER_PROFILE_BUTTON = (By.ID, "userProfile")
    USER_SETTINGS_LINK = (By.ID, "userSettings")
    CHANGE_PASSWORD_LINK = (By.ID, "changePassword")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
    
    def is_dashboard_loaded(self) -> bool:
        """Check if dashboard is fully loaded"""
        try:
            return self.is_element_present(self.WELCOME_MESSAGE) and \
                   self.is_element_present(self.ACCOUNT_SUMMARY_TABLE)
        except Exception as e:
            logger.error(f"Dashboard load check failed: {e}")
            return False
    
    def get_welcome_message(self) -> str:
        """Get welcome message text"""
        return self.get_text(self.WELCOME_MESSAGE)
    
    def get_account_summary(self) -> List[Dict[str, str]]:
        """Get account summary data"""
        accounts = []
        
        try:
            account_rows = self.find_elements(self.ACCOUNT_ROWS)
            
            for row in account_rows:
                account_type = row.find_element(*self.ACCOUNT_TYPE_COL).text
                account_number = row.find_element(*self.ACCOUNT_NUMBER_COL).text
                balance = row.find_element(*self.BALANCE_COL).text
                available_balance = row.find_element(*self.AVAILABLE_BALANCE_COL).text
                
                accounts.append({
                    "type": account_type,
                    "number": account_number,
                    "balance": self._parse_currency(balance),
                    "available_balance": self._parse_currency(available_balance)
                })
            
        except Exception as e:
            logger.error(f"Failed to get account summary: {e}")
        
        return accounts
    
    def _parse_currency(self, currency_text: str) -> float:
        """Parse currency string to float"""
        try:
            # Remove currency symbols and commas
            cleaned = currency_text.replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse currency: {currency_text}")
            return 0.0
    
    def get_total_balance(self) -> float:
        """Get total balance across all accounts"""
        accounts = self.get_account_summary()
        return sum(account["balance"] for account in accounts)
    
    def navigate_to_transfers(self):
        """Navigate to transfer funds page"""
        self.click(self.TRANSFERS_LINK)
        logger.info("Navigated to transfers page")
    
    def navigate_to_bill_pay(self):
        """Navigate to bill payment page"""
        self.click(self.BILL_PAY_LINK)
        logger.info("Navigated to bill pay page")
    
    def navigate_to_accounts(self):
        """Navigate to accounts page"""
        self.click(self.ACCOUNTS_LINK)
        logger.info("Navigated to accounts page")
    
    def navigate_to_contact(self):
        """Navigate to contact page"""
        self.click(self.CONTACT_LINK)
        logger.info("Navigated to contact page")
    
    def logout(self):
        """Logout from the application"""
        self.click(self.LOGOUT_LINK)
        logger.info("User logged out")
    
    def transfer_funds(self, from_account: str, to_account: str, 
                      amount: float, description: str = "") -> bool:
        """Transfer funds between accounts"""
        try:
            self.navigate_to_transfers()
            
            # Wait for page to load
            self.wait_for_element_visible(self.TRANSFER_FROM_DROPDOWN)
            
            # Select from account
            from_dropdown = Select(self.find_element(self.TRANSFER_FROM_DROPDOWN))
            from_dropdown.select_by_visible_text(from_account)
            
            # Select to account
            to_dropdown = Select(self.find_element(self.TRANSFER_TO_DROPDOWN))
            to_dropdown.select_by_visible_text(to_account)
            
            # Enter amount
            self.send_keys(self.TRANSFER_AMOUNT_INPUT, str(amount))
            
            # Enter description (optional)
            if description:
                self.send_keys(self.TRANSFER_DESCRIPTION_INPUT, description)
            
            # Submit transfer
            self.click(self.TRANSFER_SUBMIT_BUTTON)
            
            # Wait for success message
            self.wait_for_element_visible(self.TRANSFER_SUCCESS_MESSAGE)
            
            success_message = self.get_text(self.TRANSFER_SUCCESS_MESSAGE)
            logger.info(f"Transfer successful: {success_message}")
            
            return True
            
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            return False
    
    def pay_bill(self, payee_info: Dict[str, str], amount: float, 
                from_account: str) -> bool:
        """Pay a bill to a payee"""
        try:
            self.navigate_to_bill_pay()
            
            # Wait for page to load
            self.wait_for_element_visible(self.PAYEE_NAME_INPUT)
            
            # Fill payee information
            self.send_keys(self.PAYEE_NAME_INPUT, payee_info.get("name", ""))
            self.send_keys(self.PAYEE_ADDRESS_INPUT, payee_info.get("address", ""))
            self.send_keys(self.PAYEE_CITY_INPUT, payee_info.get("city", ""))
            self.send_keys(self.PAYEE_STATE_INPUT, payee_info.get("state", ""))
            self.send_keys(self.PAYEE_ZIP_INPUT, payee_info.get("zip", ""))
            self.send_keys(self.PAYEE_PHONE_INPUT, payee_info.get("phone", ""))
            
            # Fill account information
            account = payee_info.get("account", "")
            self.send_keys(self.PAYEE_ACCOUNT_INPUT, account)
            self.send_keys(self.PAYEE_VERIFY_ACCOUNT_INPUT, account)
            
            # Enter amount
            self.send_keys(self.PAYEE_AMOUNT_INPUT, str(amount))
            
            # Select from account
            from_dropdown = Select(self.find_element(self.PAYEE_FROM_ACCOUNT_DROPDOWN))
            from_dropdown.select_by_visible_text(from_account)
            
            # Submit payment
            self.click(self.PAYEE_SUBMIT_BUTTON)
            
            # Wait for confirmation
            time.sleep(2)  # Wait for processing
            
            # Check for success (adjust based on actual application)
            # This is a simplified check
            current_url = self.driver.current_url
            success = "confirm" in current_url.lower() or "success" in current_url.lower()
            
            if success:
                logger.info(f"Bill payment submitted for {payee_info.get('name')}")
            else:
                logger.warning("Bill payment may not have been successful")
            
            return success
            
        except Exception as e:
            logger.error(f"Bill payment failed: {e}")
            return False
    
    def search_transactions(self, search_term: str) -> List[Dict[str, str]]:
        """Search for transactions"""
        try:
            self.send_keys(self.SEARCH_INPUT, search_term)
            self.click(self.SEARCH_BUTTON)
            
            # Wait for results
            self.wait_for_element_visible(self.SEARCH_RESULTS)
            
            # Parse results (implementation depends on actual page structure)
            # This is a placeholder implementation
            results = []
            
            # Example: Assuming results are in a table
            result_rows = self.find_elements((By.XPATH, "//table[@id='searchResults']//tr[position()>1]"))
            
            for row in result_rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 4:
                    result = {
                        "date": cells[0].text,
                        "description": cells[1].text,
                        "amount": cells[2].text,
                        "balance": cells[3].text
                    }
                    results.append(result)
            
            logger.info(f"Found {len(results)} transactions for '{search_term}'")
            return results
            
        except Exception as e:
            logger.error(f"Transaction search failed: {e}")
            return []
    
    def get_recent_transactions(self, count: int = 10) -> List[Dict[str, str]]:
        """Get recent transactions"""
        try:
            transactions = []
            
            # Navigate to transactions if not already there
            if not self.is_element_present(self.RECENT_TRANSACTIONS):
                # Click on view more or navigate to transaction history
                # This depends on the actual application
                pass
            
            # Parse transaction table
            transaction_rows = self.find_elements(
                (By.XPATH, "//table[@id='transactionsTable']//tr[position()>1]")
            )[:count]
            
            for row in transaction_rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 5:
                    transaction = {
                        "date": cells[0].text,
                        "description": cells[1].text,
                        "type": cells[2].text,
                        "amount": cells[3].text,
                        "balance": cells[4].text
                    }
                    transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get recent transactions: {e}")
            return []
    
    def get_alerts(self) -> List[str]:
        """Get alert messages"""
        alerts = []
        
        try:
            alert_elements = self.find_elements(self.ALERT_MESSAGE)
            for alert in alert_elements:
                alerts.append(alert.text)
        except Exception:
            # No alerts found
            pass
        
        return alerts
    
    def dismiss_alert(self, alert_text: str = None):
        """Dismiss an alert"""
        try:
            if alert_text:
                # Find specific alert by text
                alert_xpath = f"//div[contains(@class, 'alert') and contains(text(), '{alert_text}')]"
                alert = self.find_element((By.XPATH, alert_xpath))
                # Click close button if exists
                close_button = alert.find_element(By.CLASS_NAME, "close")
                close_button.click()
            else:
                # Dismiss first alert
                alert = self.find_element(self.ALERT_MESSAGE)
                close_button = alert.find_element(By.CLASS_NAME, "close")
                close_button.click()
            
            logger.info("Alert dismissed")
            
        except Exception as e:
            logger.error(f"Failed to dismiss alert: {e}")
    
    def open_user_settings(self):
        """Open user settings"""
        self.click(self.USER_PROFILE_BUTTON)
        self.click(self.USER_SETTINGS_LINK)
        logger.info("Opened user settings")
    
    def change_password(self, current_password: str, new_password: str, 
                       confirm_password: str = None) -> bool:
        """Change user password"""
        try:
            self.click(self.USER_PROFILE_BUTTON)
            self.click(self.CHANGE_PASSWORD_LINK)
            
            # Wait for password change form to load
            # This would need actual locators for the password change form
            
            # For demonstration, assuming form elements exist
            # current_pwd_input = self.find_element((By.ID, "currentPassword"))
            # new_pwd_input = self.find_element((By.ID, "newPassword"))
            # confirm_pwd_input = self.find_element((By.ID, "confirmPassword"))
            # submit_button = self.find_element((By.ID, "changePasswordSubmit"))
            
            # Fill form
            # self.send_keys(current_pwd_input, current_password)
            # self.send_keys(new_pwd_input, new_password)
            # self.send_keys(confirm_pwd_input, confirm_password or new_password)
            # self.click(submit_button)
            
            logger.info("Password change process initiated")
            return True
            
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return False
    
    def export_account_statement(self, account_number: str, 
                               format: str = "pdf") -> Optional[str]:
        """Export account statement"""
        try:
            # Navigate to account details
            self.navigate_to_accounts()
            
            # Find and click on the account
            account_xpath = f"//tr[td[contains(text(), '{account_number}')]]//a[contains(text(), 'Statement')]"
            statement_link = self.find_element((By.XPATH, account_xpath))
            statement_link.click()
            
            # Select format if needed
            if format != "pdf":
                format_dropdown = Select(self.find_element((By.ID, "formatDropdown")))
                format_dropdown.select_by_value(format)
            
            # Click export button
            export_button = self.find_element((By.ID, "exportButton"))
            export_button.click()
            
            # Handle file download (depends on browser configuration)
            # This would need to be implemented based on download handling strategy
            
            logger.info(f"Exported statement for account {account_number} in {format} format")
            return f"statement_{account_number}.{format}"
            
        except Exception as e:
            logger.error(f"Failed to export statement: {e}")
            return None
    
    def verify_dashboard_elements(self) -> Dict[str, bool]:
        """Verify all dashboard elements are present and functional"""
        elements_status = {}
        
        try:
            elements = {
                "welcome_message": self.WELCOME_MESSAGE,
                "account_summary": self.ACCOUNT_SUMMARY_TABLE,
                "dashboard_link": self.DASHBOARD_LINK,
                "accounts_link": self.ACCOUNTS_LINK,
                "transfers_link": self.TRANSFERS_LINK,
                "bill_pay_link": self.BILL_PAY_LINK,
                "contact_link": self.CONTACT_LINK,
                "logout_link": self.LOGOUT_LINK
            }
            
            for name, locator in elements.items():
                try:
                    is_present = self.is_element_present(locator, timeout=5)
                    elements_status[name] = is_present
                    
                    if not is_present:
                        logger.warning(f"Dashboard element missing: {name}")
                except Exception:
                    elements_status[name] = False
            
            # Additional functional checks
            elements_status["has_accounts"] = len(self.get_account_summary()) > 0
            elements_status["total_balance_valid"] = self.get_total_balance() >= 0
            
            logger.info(f"Dashboard verification completed: {elements_status}")
            
        except Exception as e:
            logger.error(f"Dashboard verification failed: {e}")
            elements_status["verification_error"] = False
        
        return elements_status