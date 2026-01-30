"""
URL configuration for the testing framework.
Centralized URL management for different environments and applications.
"""
from typing import Dict, Any
from enum import Enum
from config.settings import settings


class AppType(Enum):
    """Application types"""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API = "api"
    ADMIN = "admin"


class URLConfig:
    """
    Centralized URL configuration management.
    Provides URLs for different applications and environments.
    """
    
    def __init__(self, base_url: str = None, api_url: str = None):
        self.base_url = base_url or settings.base_url
        self.api_url = api_url or settings.api_url
        
        # Application-specific paths
        self._paths = {
            AppType.WEB_APP: {
                "login": "/login.aspx",
                "logout": "/logout.aspx",
                "dashboard": "/bank/main.aspx",
                "account_summary": "/bank/account-summary.aspx",
                "transfer_funds": "/bank/transfer.aspx",
                "pay_bills": "/bank/billpay.aspx",
                "contact": "/bank/contact.aspx",
                "search": "/search.aspx"
            },
            AppType.ADMIN: {
                "login": "/admin/login",
                "dashboard": "/admin/dashboard",
                "users": "/admin/users",
                "settings": "/admin/settings",
                "reports": "/admin/reports"
            },
            AppType.API: {
                "auth": {
                    "login": "/api/login",
                    "logout": "/api/logout",
                    "refresh": "/api/refresh",
                    "validate": "/api/validate"
                },
                "users": {
                    "list": "/api/users",
                    "create": "/api/users",
                    "detail": "/api/users/{id}",
                    "update": "/api/users/{id}",
                    "delete": "/api/users/{id}",
                    "search": "/api/users/search"
                },
                "products": {
                    "list": "/api/products",
                    "create": "/api/products",
                    "detail": "/api/products/{id}",
                    "update": "/api/products/{id}",
                    "delete": "/api/products/{id}",
                    "categories": "/api/products/categories"
                },
                "orders": {
                    "list": "/api/orders",
                    "create": "/api/orders",
                    "detail": "/api/orders/{id}",
                    "update": "/api/orders/{id}",
                    "cancel": "/api/orders/{id}/cancel"
                }
            }
        }
    
    def get_url(self, app_type: AppType, endpoint: str, **params) -> str:
        """
        Get complete URL for given application type and endpoint.
        
        Args:
            app_type: Type of application (WEB_APP, ADMIN, API)
            endpoint: Endpoint key from _paths dictionary
            **params: Parameters to format into the URL
            
        Returns:
            Complete formatted URL
        """
        base = self._get_base_url(app_type)
        path = self._get_path(app_type, endpoint)
        
        # Format path with parameters
        if params:
            try:
                path = path.format(**params)
            except KeyError as e:
                raise ValueError(f"Missing parameter for URL formatting: {e}")
        
        return f"{base.rstrip('/')}{path}"
    
    def _get_base_url(self, app_type: AppType) -> str:
        """Get base URL for application type"""
        base_urls = {
            AppType.WEB_APP: self.base_url,
            AppType.ADMIN: f"{self.base_url}/admin",
            AppType.API: self.api_url,
            AppType.MOBILE_APP: f"{self.base_url}/mobile"
        }
        return base_urls.get(app_type, self.base_url)
    
    def _get_path(self, app_type: AppType, endpoint: str) -> str:
        """Get path for application type and endpoint"""
        if app_type not in self._paths:
            raise ValueError(f"Unknown application type: {app_type}")
        
        # Handle nested endpoints (e.g., API endpoints)
        if app_type == AppType.API:
            # Split endpoint like "auth.login"
            parts = endpoint.split('.')
            current = self._paths[app_type]
            
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    raise ValueError(f"Unknown API endpoint: {endpoint}")
            
            if isinstance(current, dict):
                raise ValueError(f"Endpoint {endpoint} points to a category, not a specific endpoint")
            
            return current
        
        # Regular endpoints
        if endpoint not in self._paths[app_type]:
            raise ValueError(f"Unknown endpoint for {app_type}: {endpoint}")
        
        return self._paths[app_type][endpoint]
    
    def get_login_url(self, app_type: AppType = AppType.WEB_APP) -> str:
        """Get login URL for application type"""
        return self.get_url(app_type, "login")
    
    def get_dashboard_url(self, app_type: AppType = AppType.WEB_APP) -> str:
        """Get dashboard URL for application type"""
        return self.get_url(app_type, "dashboard")
    
    def get_api_endpoint(self, category: str, endpoint: str, **params) -> str:
        """Get API endpoint URL"""
        return self.get_url(AppType.API, f"{category}.{endpoint}", **params)
    
    # Convenience methods for common URLs
    @property
    def login_page(self) -> str:
        """Get web app login page URL"""
        return self.get_login_url(AppType.WEB_APP)
    
    @property
    def dashboard_page(self) -> str:
        """Get web app dashboard URL"""
        return self.get_dashboard_url(AppType.WEB_APP)
    
    @property
    def account_summary_page(self) -> str:
        """Get account summary page URL"""
        return self.get_url(AppType.WEB_APP, "account_summary")
    
    @property
    def transfer_funds_page(self) -> str:
        """Get transfer funds page URL"""
        return self.get_url(AppType.WEB_APP, "transfer_funds")
    
    @property
    def api_auth_login(self) -> str:
        """Get API auth login endpoint"""
        return self.get_api_endpoint("auth", "login")
    
    @property
    def api_users_list(self) -> str:
        """Get API users list endpoint"""
        return self.get_api_endpoint("users", "list")
    
    def get_all_urls(self) -> Dict[str, Dict[str, str]]:
        """Get all configured URLs organized by application type"""
        all_urls = {}
        
        for app_type in AppType:
            if app_type in self._paths:
                app_urls = {}
                
                if app_type == AppType.API:
                    # Flatten nested API endpoints
                    for category, endpoints in self._paths[app_type].items():
                        if isinstance(endpoints, dict):
                            for endpoint, path in endpoints.items():
                                key = f"{category}.{endpoint}"
                                app_urls[key] = f"{self._get_base_url(app_type)}{path}"
                else:
                    for endpoint, path in self._paths[app_type].items():
                        app_urls[endpoint] = f"{self._get_base_url(app_type)}{path}"
                
                all_urls[app_type.value] = app_urls
        
        return all_urls
    
    def validate_urls(self) -> Dict[str, Any]:
        """Validate all configured URLs"""
        import requests
        from requests.exceptions import RequestException
        
        results = {}
        
        for app_type, endpoints in self.get_all_urls().items():
            results[app_type] = {}
            
            for endpoint_name, url in endpoints.items():
                try:
                    # Skip formatting for URLs with placeholders
                    if '{' in url and '}' in url:
                        results[app_type][endpoint_name] = {
                            "status": "skipped",
                            "reason": "contains parameters"
                        }
                        continue
                    
                    # Test URL accessibility
                    response = requests.head(url, timeout=5, verify=settings.ssl_verification)
                    results[app_type][endpoint_name] = {
                        "status": "accessible" if response.status_code < 400 else "error",
                        "status_code": response.status_code,
                        "url": url
                    }
                    
                except RequestException as e:
                    results[app_type][endpoint_name] = {
                        "status": "unreachable",
                        "error": str(e),
                        "url": url
                    }
        
        return results


# Global URL config instance
urls = URLConfig()