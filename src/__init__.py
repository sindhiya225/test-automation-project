"""

Features:
---------
1. Cross-browser testing with Selenium Grid
2. Comprehensive API testing with schema validation
3. Postman collection integration
4. Advanced reporting with screenshots and bug tracking
5. Docker containerization for CI/CD
6. Parallel test execution
7. Performance monitoring
8. Security testing capabilities

Modules:
--------
- src.core: Core framework components
- src.api: API testing utilities
- src.pages: Page Object Model implementations
- utilities: Additional tools and utilities
- tests: Test suites and test cases
- config: Configuration management
- test_data: Test data management

Usage:
------
1. Install dependencies: pip install -r requirements.txt
2. Configure environment: cp .env.example .env
3. Run tests: pytest tests/ -v
4. Generate report: pytest --html=reports/report.html


"""

__version__ = "1.0.0"
__email__ = "applicant@example.com"

# Package exports
from src.core import (
    BrowserFactory,
    BrowserManager,
    BrowserType,
    APIClient,
    TestLogger,
    TestUtilities,
    DataGenerator,
    PerformanceTimer,
    FileHandler
)

from src.api import (
    APIEndpoints,
    UserSchema,
    AuthResponseSchema,
    ErrorSchema,
    ProductSchema,
    OrderSchema
)

from src.pages import (
    BasePage,
    LoginPage,
    DashboardPage
)

# Import utilities
from utilities.bug_reporter import BugReporter
from utilities.screenshot_manager import ScreenshotManager
from utilities.postman_runner import PostmanRunner

__all__ = [
    # Core components
    'BrowserFactory',
    'BrowserManager',
    'BrowserType',
    'APIClient',
    'TestLogger',
    'TestUtilities',
    'DataGenerator',
    'PerformanceTimer',
    'FileHandler',
    
    # API components
    'APIEndpoints',
    'UserSchema',
    'AuthResponseSchema',
    'ErrorSchema',
    'ProductSchema',
    'OrderSchema',
    
    # Page Objects
    'BasePage',
    'LoginPage',
    'DashboardPage',
    
    # Utilities
    'BugReporter',
    'ScreenshotManager',
    'PostmanRunner',
]

# Initialize framework components on import
logger = TestLogger.get_logger(__name__)
logger.info(f"Test Automation Framework v{__version__} initialized")