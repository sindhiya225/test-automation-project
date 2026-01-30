"""
API testing package for the automation framework.
Contains API client, endpoint configurations, and schema validation.
"""

from src.api.endpoints import APIEndpoints
from src.api.schemas import (
    UserSchema,
    AuthResponseSchema,
    ErrorSchema,
    ProductSchema,
    OrderSchema
)

__all__ = [
    'APIEndpoints',
    'UserSchema',
    'AuthResponseSchema',
    'ErrorSchema',
    'ProductSchema',
    'OrderSchema'
]