"""
Base Page Object Model with advanced utilities
"""
from abc import ABC
from typing import List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from src.core.logger import TestLogger
import time

logger = TestLogger.get_logger(__name__)

class BasePage(ABC):
    """Base Page Object Model with advanced selenium utilities"""
    
    def __init__(self, driver: WebDriver, timeout: int = 30):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
    
    def find_element(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        """Find element with explicit wait and retry"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        
        def _find_element(driver):
            try:
                element = driver.find_element(*locator)
                if element.is_displayed() and element.is_enabled():
                    return element
            except StaleElementReferenceException:
                return False
            except Exception:
                return False
            return False
        
        return wait.until(_find_element)
    
    def find_elements(self, locator: tuple, timeout: Optional[int] = None) -> List[WebElement]:
        """Find multiple elements"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_all_elements_located(locator))
    
    def click(self, locator: tuple):
        """Click element with retry"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                element = self.find_element(locator)
                element.click()
                logger.info(f"Clicked element: {locator}")
                return
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(1)
                logger.warning(f"Click attempt {attempt + 1} failed: {e}")
    
    def send_keys(self, locator: tuple, text: str, clear_first: bool = True):
        """Send keys to element"""
        element = self.find_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.info(f"Sent text '{text}' to element: {locator}")
    
    def get_text(self, locator: tuple) -> str:
        """Get text from element"""
        element = self.find_element(locator)
        text = element.text
        logger.info(f"Got text '{text}' from element: {locator}")
        return text
    
    def is_element_present(self, locator: tuple, timeout: Optional[int] = None) -> bool:
        """Check if element is present"""
        try:
            self.find_element(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def wait_for_element_visible(self, locator: tuple, timeout: Optional[int] = None):
        """Wait for element to be visible"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.visibility_of_element_located(locator))
    
    def take_screenshot(self, filename: str):
        """Take screenshot of current page"""
        self.driver.save_screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")
    
    def get_page_source(self) -> str:
        """Get page source"""
        return self.driver.page_source
    
    def execute_javascript(self, script: str, *args):
        """Execute JavaScript"""
        return self.driver.execute_script(script, *args)
    
    def scroll_to_element(self, locator: tuple):
        """Scroll to element"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def switch_to_frame(self, locator: tuple):
        """Switch to iframe"""
        frame = self.find_element(locator)
        self.driver.switch_to.frame(frame)
    
    def switch_to_default_content(self):
        """Switch back to default content"""
        self.driver.switch_to.default_content()
    
    def accept_alert(self):
        """Accept alert"""
        alert = self.driver.switch_to.alert
        alert.accept()
    
    def dismiss_alert(self):
        """Dismiss alert"""
        alert = self.driver.switch_to.alert
        alert.dismiss()