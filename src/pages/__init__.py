"""
Page Object Model package for UI automation.
Contains base page class and page-specific implementations.
"""

from src.pages.base_page import BasePage
from src.pages.login_page import LoginPage
from src.pages.dashboard_page import DashboardPage

__all__ = ['BasePage', 'LoginPage', 'DashboardPage']