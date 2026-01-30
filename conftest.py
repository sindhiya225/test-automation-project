"""
Advanced Pytest configuration with fixtures for the entire test suite
"""
import os
import json
import pytest
import logging
from datetime import datetime
from typing import Dict, Any, Generator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import Browser, Page, sync_playwright
from dotenv import load_dotenv
from src.core.browser_factory import BrowserFactory
from src.core.api_client import APIClient
from src.core.logger import TestLogger
from utilities.screenshot_manager import ScreenshotManager
from utilities.bug_reporter import BugReporter

# Load environment variables
load_dotenv()

# Configure logging
logger = TestLogger.get_logger(__name__)

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Load test configuration"""
    config = {
        "base_url": os.getenv("BASE_URL", "https://demo.testfire.net"),
        "api_url": os.getenv("API_URL", "https://jsonplaceholder.typicode.com"),
        "browser": os.getenv("BROWSER", "chrome"),
        "headless": os.getenv("HEADLESS", "true").lower() == "true",
        "timeout": int(os.getenv("TIMEOUT", "30")),
        "screenshot_on_fail": True,
        "video_on_fail": False
    }
    return config

@pytest.fixture(scope="function")
def selenium_driver(test_config) -> Generator[webdriver.Remote, None, None]:
    """Selenium WebDriver fixture with advanced configuration"""
    options = Options()
    
    if test_config["headless"]:
        options.add_argument("--headless")
    
    # Advanced Chrome options
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # Enable performance logging
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(test_config["timeout"])
    driver.maximize_window()
    
    logger.info(f"Selenium driver initialized for {test_config['browser']}")
    
    yield driver
    
    # Teardown
    driver.quit()
    logger.info("Selenium driver closed")

@pytest.fixture(scope="function")
def playwright_page(test_config) -> Generator[Page, None, None]:
    """Playwright page fixture"""
    playwright = sync_playwright().start()
    
    browser_type = getattr(playwright, test_config["browser"])
    browser = browser_type.launch(
        headless=test_config["headless"],
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir="reports/videos" if test_config["video_on_fail"] else None
    )
    
    page = context.new_page()
    logger.info(f"Playwright page initialized for {test_config['browser']}")
    
    yield page
    
    # Teardown
    if test_config["video_on_fail"]:
        page.close()
        context.close()
    browser.close()
    playwright.stop()

@pytest.fixture(scope="session")
def api_client(test_config) -> APIClient:
    """API client fixture"""
    client = APIClient(base_url=test_config["api_url"])
    return client

@pytest.fixture(scope="function")
def test_data() -> Dict[str, Any]:
    """Load test data"""
    import yaml
    with open("test_data/test_cases.yaml", "r") as file:
        return yaml.safe_load(file)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Custom hook for taking screenshots and gathering logs on test failure"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # Take screenshot if driver is available
        if "selenium_driver" in item.funcargs:
            driver = item.funcargs["selenium_driver"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"reports/screenshots/failure_{item.name}_{timestamp}.png"
            
            try:
                driver.save_screenshot(screenshot_path)
                report.screenshot = screenshot_path
                logger.error(f"Screenshot saved: {screenshot_path}")
                
                # Get browser logs
                browser_logs = driver.get_log("browser")
                if browser_logs:
                    log_file = f"reports/logs/browser_{item.name}_{timestamp}.json"
                    with open(log_file, "w") as f:
                        json.dump(browser_logs, f, indent=2)
                
            except Exception as e:
                logger.error(f"Failed to capture screenshot: {e}")
        
        # Create bug report
        bug_reporter = BugReporter()
        bug_report = bug_reporter.create_bug_report(
            test_name=item.name,
            error=str(report.longrepr),
            steps_to_reproduce=item.function.__doc__ or "No steps documented"
        )
        
        if bug_report:
            logger.info(f"Bug report created: {bug_report}")

@pytest.fixture(autouse=True)
def setup_teardown(request, test_config):
    """Autouse fixture for setup and teardown operations"""
    logger.info(f"Starting test: {request.node.name}")
    
    yield
    
    logger.info(f"Finished test: {request.node.name}")