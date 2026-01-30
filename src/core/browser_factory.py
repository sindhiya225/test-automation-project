"""
Advanced Browser Factory supporting multiple browsers and configurations
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)

class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"

class BrowserFactory(ABC):
    """Abstract Browser Factory"""
    
    @abstractmethod
    def create_driver(self):
        pass

class ChromeBrowserFactory(BrowserFactory):
    """Chrome Browser Factory"""
    
    def create_driver(self, headless: bool = False, options: Optional[ChromeOptions] = None):
        if options is None:
            options = ChromeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        # Performance and reliability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Mobile emulation (optional)
        mobile_emulation = {
            "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)"
        }
        # options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(),
            options=options
        )
        
        # Execute CDP commands
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
        
        logger.info("Chrome driver created with advanced options")
        return driver

class FirefoxBrowserFactory(BrowserFactory):
    """Firefox Browser Factory"""
    
    def create_driver(self, headless: bool = False, options: Optional[FirefoxOptions] = None):
        if options is None:
            options = FirefoxOptions()
        
        if headless:
            options.add_argument("--headless")
        
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        driver = webdriver.Firefox(
            executable_path=GeckoDriverManager().install(),
            options=options
        )
        
        logger.info("Firefox driver created")
        return driver

class BrowserManager:
    """Browser Manager to handle browser creation and management"""
    
    @staticmethod
    def get_browser_factory(browser_type: BrowserType) -> BrowserFactory:
        factories = {
            BrowserType.CHROME: ChromeBrowserFactory(),
            BrowserType.FIREFOX: FirefoxBrowserFactory(),
            BrowserType.EDGE: lambda: webdriver.Edge(
                executable_path=EdgeChromiumDriverManager().install()
            ),
        }
        
        factory = factories.get(browser_type)
        if not factory:
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        return factory
    
    @staticmethod
    def create_driver(browser_type: BrowserType = BrowserType.CHROME, **kwargs):
        factory = BrowserManager.get_browser_factory(browser_type)
        return factory.create_driver(**kwargs)