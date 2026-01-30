"""
Core framework components for the automation framework.
Contains essential utilities, factories, and base classes.
"""

from src.core.browser_factory import BrowserFactory, BrowserManager, BrowserType
from src.core.api_client import APIClient
from src.core.logger import TestLogger
from src.core.utilities import (
    TestUtilities,
    DataGenerator,
    PerformanceTimer,
    FileHandler
)

__all__ = [
    'BrowserFactory',
    'BrowserManager',
    'BrowserType',
    'APIClient',
    'TestLogger',
    'TestUtilities',
    'DataGenerator',
    'PerformanceTimer',
    'FileHandler'
]