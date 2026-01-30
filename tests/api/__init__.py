"""
API test package for the automation framework.
Contains API test suites for various endpoints and scenarios.
"""

from tests.api.test_auth_api import TestAuthAPI
from tests.api.test_user_api import TestUserAPI
from tests.api.test_data_validation import TestDataValidation

__all__ = [
    'TestAuthAPI',
    'TestUserAPI', 
    'TestDataValidation'
]