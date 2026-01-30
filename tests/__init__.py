"""
Test automation framework test suite package.
Contains all test modules for UI, API, and integration testing.

This package organizes tests into logical groups:
- UI Tests: User interface testing with Selenium/Playwright
- API Tests: REST API testing with requests
- Integration Tests: End-to-end workflows combining UI and API

Usage:
    pytest tests/ -v                    # Run all tests
    pytest tests/ui/ -v -m ui          # Run only UI tests
    pytest tests/api/ -v -m api        # Run only API tests
    pytest tests/ -v -m smoke          # Run smoke tests only
    pytest tests/ -v -m security       # Run security tests only
"""

from tests.ui import TestLogin, TestDashboard, TestForms, TestValidations
from tests.api import TestAuthAPI, TestUserAPI, TestDataValidation
from tests.integration import TestUIApiIntegration

__all__ = [
    # UI Tests
    'TestLogin',
    'TestDashboard',
    'TestForms',
    'TestValidations',
    
    # API Tests
    'TestAuthAPI',
    'TestUserAPI',
    'TestDataValidation',
    
    # Integration Tests
    'TestUIApiIntegration'
]

# Test configuration and constants
TEST_CATEGORIES = {
    'ui': 'User Interface Tests',
    'api': 'API Integration Tests',
    'integration': 'End-to-End Integration Tests',
    'smoke': 'Smoke/Sanity Tests',
    'regression': 'Regression Tests',
    'security': 'Security Tests',
    'performance': 'Performance Tests'
}

# Test environment configuration
ENVIRONMENT = "qa"  # Default test environment
BROWSER = "chrome"  # Default browser for UI tests
HEADLESS = True     # Run browsers in headless mode by default