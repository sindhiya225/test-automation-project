"""
UI test package for the automation framework.
Contains UI test suites for various pages and user interactions.
"""

from tests.ui.test_login import TestLogin
from tests.ui.test_dashboard import TestDashboard
from tests.ui.test_forms import TestForms
from tests.ui.test_validations import TestValidations

__all__ = [
    'TestLogin',
    'TestDashboard', 
    'TestForms',
    'TestValidations'
]