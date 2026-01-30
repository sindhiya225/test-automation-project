"""
Configuration package for test framework settings.
This file makes the config directory a Python package.
"""

from config.settings import TestSettings
from config.urls import URLConfig

__all__ = ['TestSettings', 'URLConfig']