"""
API endpoint configurations and route definitions.
Centralized management of all API endpoints with parameter support.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class HTTPMethod(Enum):
    """HTTP methods enum"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class EndpointCategory(Enum):
    """API endpoint categories"""
    AUTH = "auth"
    USERS = "users"
    PRODUCTS = "products"
    ORDERS = "orders"
    REPORTS = "reports"
    SYSTEM = "system"
    UTILITIES = "utilities"


@dataclass
class EndpointConfig:
    """Configuration for a single API endpoint"""
    name: str
    path: str
    method: HTTPMethod
    category: EndpointCategory
    description: str = ""
    requires_auth: bool = True
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    success_codes: List[int] = field(default_factory=lambda: [200, 201, 204])
    timeout: int = 30
    retry_count: int = 3
    schema_validation: bool = True
    
    def __post_init__(self):
        """Validate endpoint configuration"""
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        
        # Set default headers based on method
        if self.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            if 'Content-Type' not in self.headers:
                self.headers['Content-Type'] = 'application/json'
    
    def get_full_path(self, base_url: str = "", **params) -> str:
        """Get complete URL with parameters"""
        path = self.path
        
        # Replace path parameters
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in path:
                path = path.replace(placeholder, str(value))
                # Remove from params to avoid duplicate in query string
                params.pop(key)
        
        # Build query string from remaining params
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            path = f"{path}?{query_string}"
        
        return f"{base_url.rstrip('/')}{path}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert endpoint configuration to dictionary"""
        return {
            "name": self.name,
            "path": self.path,
            "method": self.method.value,
            "category": self.category.value,
            "description": self.description,
            "requires_auth": self.requires_auth,
            "parameters": self.parameters,
            "headers": self.headers,
            "success_codes": self.success_codes,
            "timeout": self.timeout,
            "retry_count": self.retry_count
        }


class APIEndpoints:
    """
    Centralized API endpoint configurations.
    Contains all endpoints for the application with metadata.
    """
    
    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self._endpoints: Dict[str, EndpointConfig] = {}
        self._initialize_endpoints()
    
    def _initialize_endpoints(self):
        """Initialize all API endpoints"""
        
        # Authentication endpoints
        self._endpoints["login"] = EndpointConfig(
            name="login",
            path="/api/v1/auth/login",
            method=HTTPMethod.POST,
            category=EndpointCategory.AUTH,
            description="Authenticate user and get access token",
            requires_auth=False,
            parameters=[
                {"name": "username", "type": "string", "required": True},
                {"name": "password", "type": "string", "required": True}
            ],
            success_codes=[200]
        )
        
        self._endpoints["logout"] = EndpointConfig(
            name="logout",
            path="/api/v1/auth/logout",
            method=HTTPMethod.POST,
            category=EndpointCategory.AUTH,
            description="Logout user and invalidate token",
            success_codes=[200, 204]
        )
        
        self._endpoints["refresh_token"] = EndpointConfig(
            name="refresh_token",
            path="/api/v1/auth/refresh",
            method=HTTPMethod.POST,
            category=EndpointCategory.AUTH,
            description="Refresh access token using refresh token",
            success_codes=[200]
        )
        
        # User management endpoints
        self._endpoints["get_users"] = EndpointConfig(
            name="get_users",
            path="/api/v1/users",
            method=HTTPMethod.GET,
            category=EndpointCategory.USERS,
            description="Get list of users with pagination",
            parameters=[
                {"name": "page", "type": "integer", "required": False, "default": 1},
                {"name": "limit", "type": "integer", "required": False, "default": 20},
                {"name": "role", "type": "string", "required": False},
                {"name": "active", "type": "boolean", "required": False}
            ],
            success_codes=[200]
        )
        
        self._endpoints["create_user"] = EndpointConfig(
            name="create_user",
            path="/api/v1/users",
            method=HTTPMethod.POST,
            category=EndpointCategory.USERS,
            description="Create a new user",
            parameters=[
                {"name": "username", "type": "string", "required": True},
                {"name": "email", "type": "string", "required": True},
                {"name": "password", "type": "string", "required": True},
                {"name": "first_name", "type": "string", "required": False},
                {"name": "last_name", "type": "string", "required": False},
                {"name": "role", "type": "string", "required": False, "default": "user"}
            ],
            success_codes=[201]
        )
        
        self._endpoints["get_user"] = EndpointConfig(
            name="get_user",
            path="/api/v1/users/{user_id}",
            method=HTTPMethod.GET,
            category=EndpointCategory.USERS,
            description="Get user details by ID",
            parameters=[
                {"name": "user_id", "type": "string", "required": True, "in": "path"}
            ],
            success_codes=[200]
        )
        
        self._endpoints["update_user"] = EndpointConfig(
            name="update_user",
            path="/api/v1/users/{user_id}",
            method=HTTPMethod.PUT,
            category=EndpointCategory.USERS,
            description="Update user details",
            parameters=[
                {"name": "user_id", "type": "string", "required": True, "in": "path"}
            ],
            success_codes=[200]
        )
        
        self._endpoints["delete_user"] = EndpointConfig(
            name="delete_user",
            path="/api/v1/users/{user_id}",
            method=HTTPMethod.DELETE,
            category=EndpointCategory.USERS,
            description="Delete a user",
            parameters=[
                {"name": "user_id", "type": "string", "required": True, "in": "path"}
            ],
            success_codes=[204]
        )
        
        # Product endpoints
        self._endpoints["get_products"] = EndpointConfig(
            name="get_products",
            path="/api/v1/products",
            method=HTTPMethod.GET,
            category=EndpointCategory.PRODUCTS,
            description="Get list of products",
            parameters=[
                {"name": "category", "type": "string", "required": False},
                {"name": "in_stock", "type": "boolean", "required": False},
                {"name": "min_price", "type": "number", "required": False},
                {"name": "max_price", "type": "number", "required": False}
            ],
            success_codes=[200]
        )
        
        self._endpoints["create_product"] = EndpointConfig(
            name="create_product",
            path="/api/v1/products",
            method=HTTPMethod.POST,
            category=EndpointCategory.PRODUCTS,
            description="Create a new product",
            success_codes=[201]
        )
        
        # Order endpoints
        self._endpoints["create_order"] = EndpointConfig(
            name="create_order",
            path="/api/v1/orders",
            method=HTTPMethod.POST,
            category=EndpointCategory.ORDERS,
            description="Create a new order",
            success_codes=[201]
        )
        
        # System endpoints
        self._endpoints["health_check"] = EndpointConfig(
            name="health_check",
            path="/api/v1/health",
            method=HTTPMethod.GET,
            category=EndpointCategory.SYSTEM,
            description="Check system health status",
            requires_auth=False,
            success_codes=[200]
        )
        
        self._endpoints["metrics"] = EndpointConfig(
            name="metrics",
            path="/api/v1/metrics",
            method=HTTPMethod.GET,
            category=EndpointCategory.SYSTEM,
            description="Get system metrics",
            success_codes=[200]
        )
    
    def get_endpoint(self, endpoint_name: str) -> EndpointConfig:
        """Get endpoint configuration by name"""
        if endpoint_name not in self._endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found")
        return self._endpoints[endpoint_name]
    
    def get_endpoints_by_category(self, category: EndpointCategory) -> List[EndpointConfig]:
        """Get all endpoints for a specific category"""
        return [
            endpoint for endpoint in self._endpoints.values()
            if endpoint.category == category
        ]
    
    def get_url(self, endpoint_name: str, **params) -> str:
        """Get complete URL for an endpoint"""
        endpoint = self.get_endpoint(endpoint_name)
        return endpoint.get_full_path(self.base_url, **params)
    
    def get_endpoint_details(self, endpoint_name: str) -> Dict[str, Any]:
        """Get detailed information about an endpoint"""
        endpoint = self.get_endpoint(endpoint_name)
        details = endpoint.to_dict()
        details["url"] = self.get_url(endpoint_name)
        return details
    
    def add_endpoint(self, endpoint: EndpointConfig):
        """Add a custom endpoint to the configuration"""
        if endpoint.name in self._endpoints:
            raise ValueError(f"Endpoint '{endpoint.name}' already exists")
        self._endpoints[endpoint.name] = endpoint
    
    def update_base_url(self, base_url: str):
        """Update the base URL for all endpoints"""
        self.base_url = base_url
    
    def export_to_openapi(self, filepath: str = "api_spec.json"):
        """Export endpoints to OpenAPI specification format"""
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API Specification",
                "version": "1.0.0",
                "description": "Auto-generated API specification from endpoint configurations"
            },
            "servers": [
                {"url": self.base_url, "description": "Test Server"}
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
        
        # Group endpoints by path
        for endpoint in self._endpoints.values():
            path = endpoint.path
            method = endpoint.method.value.lower()
            
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}
            
            # Create path operation
            operation = {
                "summary": endpoint.name.replace('_', ' ').title(),
                "description": endpoint.description,
                "operationId": endpoint.name,
                "responses": {
                    str(code): {"description": "Success" if code < 400 else "Error"}
                    for code in endpoint.success_codes + [400, 401, 403, 404, 500]
                }
            }
            
            # Add security requirement
            if endpoint.requires_auth:
                operation["security"] = [{"bearerAuth": []}]
            
            # Add parameters
            if endpoint.parameters:
                operation["parameters"] = []
                for param in endpoint.parameters:
                    param_spec = {
                        "name": param["name"],
                        "in": param.get("in", "query"),
                        "required": param.get("required", False),
                        "schema": {"type": param["type"]}
                    }
                    if "default" in param:
                        param_spec["schema"]["default"] = param["default"]
                    operation["parameters"].append(param_spec)
            
            openapi_spec["paths"][path][method] = operation
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(openapi_spec, f, indent=2)
        
        return openapi_spec
    
    def validate_request(self, endpoint_name: str, response_status: int, response_data: Dict = None) -> bool:
        """Validate API response against endpoint configuration"""
        endpoint = self.get_endpoint(endpoint_name)
        
        # Check status code
        if response_status not in endpoint.success_codes:
            return False
        
        # Additional validation could be added here
        # (e.g., schema validation, response structure)
        
        return True