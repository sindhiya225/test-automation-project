"""
Advanced configuration settings for the testing framework.
Centralized settings management with environment variable support.
"""
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"
    REMOTE = "remote"

class EnvironmentType(Enum):
    """Supported environment types"""
    DEV = "dev"
    QA = "qa"
    STAGING = "staging"
    PROD = "prod"

@dataclass
class TestSettings:
    """
    Centralized test settings configuration.
    Supports environment-specific configurations.
    """
    
    # Environment Settings
    environment: EnvironmentType = field(
        default_factory=lambda: EnvironmentType(os.getenv("ENVIRONMENT", "qa"))
    )
    
    # Application URLs
    base_url: str = field(
        default_factory=lambda: os.getenv("BASE_URL", "https://demo.testfire.net")
    )
    api_url: str = field(
        default_factory=lambda: os.getenv("API_URL", "https://jsonplaceholder.typicode.com")
    )
    
    # Browser Configuration
    browser: BrowserType = field(
        default_factory=lambda: BrowserType(os.getenv("BROWSER", "chrome"))
    )
    headless: bool = field(
        default_factory=lambda: os.getenv("HEADLESS", "true").lower() == "true"
    )
    browser_timeout: int = field(
        default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT", "30"))
    )
    implicit_wait: int = field(
        default_factory=lambda: int(os.getenv("IMPLICIT_WAIT", "10"))
    )
    explicit_wait: int = field(
        default_factory=lambda: int(os.getenv("EXPLICIT_WAIT", "30"))
    )
    
    # Window/Viewport Settings
    window_width: int = field(
        default_factory=lambda: int(os.getenv("WINDOW_WIDTH", "1920"))
    )
    window_height: int = field(
        default_factory=lambda: int(os.getenv("WINDOW_HEIGHT", "1080"))
    )
    
    # Selenium Grid Configuration
    selenium_hub_url: str = field(
        default_factory=lambda: os.getenv("SELENIUM_HUB_URL", "http://localhost:4444/wd/hub")
    )
    enable_grid: bool = field(
        default_factory=lambda: os.getenv("ENABLE_GRID", "false").lower() == "true"
    )
    
    # API Configuration
    api_timeout: int = field(
        default_factory=lambda: int(os.getenv("API_TIMEOUT", "30"))
    )
    api_retries: int = field(
        default_factory=lambda: int(os.getenv("API_RETRIES", "3"))
    )
    
    # Authentication
    admin_username: str = field(
        default_factory=lambda: os.getenv("ADMIN_USERNAME", "admin")
    )
    admin_password: str = field(
        default_factory=lambda: os.getenv("ADMIN_PASSWORD", "admin123")
    )
    
    # Test Execution Settings
    test_timeout: int = field(
        default_factory=lambda: int(os.getenv("TEST_TIMEOUT", "300"))
    )
    parallel_execution: bool = field(
        default_factory=lambda: os.getenv("PARALLEL_EXECUTION", "true").lower() == "true"
    )
    max_parallel_workers: int = field(
        default_factory=lambda: int(os.getenv("MAX_PARALLEL_WORKERS", "4"))
    )
    
    # Retry Configuration
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("MAX_RETRIES", "3"))
    )
    retry_delay: int = field(
        default_factory=lambda: int(os.getenv("RETRY_DELAY", "2"))
    )
    
    # Screenshot and Video Settings
    screenshot_on_failure: bool = field(
        default_factory=lambda: os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    )
    screenshot_dir: str = field(
        default_factory=lambda: os.getenv("SCREENSHOT_DIR", "reports/screenshots")
    )
    video_on_failure: bool = field(
        default_factory=lambda: os.getenv("VIDEO_ON_FAILURE", "false").lower() == "true"
    )
    video_dir: str = field(
        default_factory=lambda: os.getenv("VIDEO_DIR", "reports/videos")
    )
    
    # Reporting Settings
    report_dir: str = field(
        default_factory=lambda: os.getenv("REPORT_DIR", "reports")
    )
    report_format: str = field(
        default_factory=lambda: os.getenv("REPORT_FORMAT", "html")
    )
    allure_report: bool = field(
        default_factory=lambda: os.getenv("ALLURE_REPORT", "true").lower() == "true"
    )
    
    # Logging Settings
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    log_dir: str = field(
        default_factory=lambda: os.getenv("LOG_DIR", "logs")
    )
    log_format: str = field(
        default_factory=lambda: os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    
    # Performance Settings
    page_load_timeout: int = field(
        default_factory=lambda: int(os.getenv("PAGE_LOAD_TIMEOUT", "60"))
    )
    script_timeout: int = field(
        default_factory=lambda: int(os.getenv("SCRIPT_TIMEOUT", "30"))
    )
    
    # Security Settings
    security_scan: bool = field(
        default_factory=lambda: os.getenv("SECURITY_SCAN", "true").lower() == "true"
    )
    ssl_verification: bool = field(
        default_factory=lambda: os.getenv("SSL_VERIFICATION", "true").lower() == "true"
    )
    
    # Database Settings (if applicable)
    db_host: str = field(
        default_factory=lambda: os.getenv("DB_HOST", "localhost")
    )
    db_port: int = field(
        default_factory=lambda: int(os.getenv("DB_PORT", "5432"))
    )
    db_name: str = field(
        default_factory=lambda: os.getenv("DB_NAME", "test_db")
    )
    db_user: str = field(
        default_factory=lambda: os.getenv("DB_USER", "test_user")
    )
    db_password: str = field(
        default_factory=lambda: os.getenv("DB_PASSWORD", "")
    )
    
    # Email/Slack Notifications
    enable_notifications: bool = field(
        default_factory=lambda: os.getenv("ENABLE_NOTIFICATIONS", "false").lower() == "true"
    )
    notification_email: str = field(
        default_factory=lambda: os.getenv("NOTIFICATION_EMAIL", "")
    )
    slack_webhook: str = field(
        default_factory=lambda: os.getenv("SLACK_WEBHOOK", "")
    )
    
    # Test Data Settings
    test_data_dir: str = field(
        default_factory=lambda: os.getenv("TEST_DATA_DIR", "test_data")
    )
    use_fake_data: bool = field(
        default_factory=lambda: os.getenv("USE_FAKE_DATA", "true").lower() == "true"
    )
    
    # Cache Settings
    clear_cache_before_test: bool = field(
        default_factory=lambda: os.getenv("CLEAR_CACHE_BEFORE_TEST", "true").lower() == "true"
    )
    clear_cookies_before_test: bool = field(
        default_factory=lambda: os.getenv("CLEAR_COOKIES_BEFORE_TEST", "true").lower() == "true"
    )
    
    # Mobile Testing
    mobile_emulation: bool = field(
        default_factory=lambda: os.getenv("MOBILE_EMULATION", "false").lower() == "true"
    )
    mobile_device: str = field(
        default_factory=lambda: os.getenv("MOBILE_DEVICE", "iPhone 12")
    )
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        env_configs = {
            EnvironmentType.DEV: {
                "base_url": "http://localhost:8080",
                "api_url": "http://localhost:3000",
                "headless": False,
                "log_level": "DEBUG"
            },
            EnvironmentType.QA: {
                "base_url": "https://qa.example.com",
                "api_url": "https://qa-api.example.com",
                "headless": True,
                "log_level": "INFO"
            },
            EnvironmentType.STAGING: {
                "base_url": "https://staging.example.com",
                "api_url": "https://staging-api.example.com",
                "headless": True,
                "log_level": "INFO"
            },
            EnvironmentType.PROD: {
                "base_url": "https://example.com",
                "api_url": "https://api.example.com",
                "headless": True,
                "log_level": "WARNING"
            }
        }
        
        return env_configs.get(self.environment, {})
    
    def get_browser_capabilities(self) -> Dict[str, Any]:
        """Get browser-specific capabilities"""
        capabilities = {
            BrowserType.CHROME: {
                "browserName": "chrome",
                "version": "latest",
                "platform": "ANY",
                "goog:loggingPrefs": {"browser": "ALL", "performance": "ALL"},
                "chromeOptions": {
                    "args": [
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        f"--window-size={self.window_width},{self.window_height}"
                    ]
                }
            },
            BrowserType.FIREFOX: {
                "browserName": "firefox",
                "moz:firefoxOptions": {
                    "args": ["-headless"] if self.headless else []
                }
            },
            BrowserType.EDGE: {
                "browserName": "MicrosoftEdge",
                "version": "latest"
            }
        }
        
        return capabilities.get(self.browser, {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "environment": self.environment.value,
            "browser": self.browser.value,
            "headless": self.headless,
            "base_url": self.base_url,
            "api_url": self.api_url,
            "window_size": f"{self.window_width}x{self.window_height}",
            "timeouts": {
                "browser": self.browser_timeout,
                "api": self.api_timeout,
                "test": self.test_timeout
            }
        }
    
    def save_to_file(self, filepath: str = "config/settings.json"):
        """Save settings to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str = "config/settings.json") -> 'TestSettings':
        """Load settings from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert string values back to enums
        data['environment'] = EnvironmentType(data['environment'])
        data['browser'] = BrowserType(data['browser'])
        
        return cls(**data)


# Global settings instance
settings = TestSettings()