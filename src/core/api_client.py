"""
Advanced API Client with authentication, retry logic, and request/response validation
"""
import json
import time
from typing import Dict, Any, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.core.logger import TestLogger
from jsonschema import validate

logger = TestLogger.get_logger(__name__)

class APIClient:
    """Advanced API Client with built-in retry, validation, and logging"""
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def validate_schema(self, response_data: Dict[str, Any], schema: Dict[str, Any]):
        """Validate response against JSON schema"""
        try:
            validate(instance=response_data, schema=schema)
            logger.info("Response validation successful")
            return True
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with enhanced logging and error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Log request
        logger.info(f"Making {method} request to {url}")
        if kwargs.get('json'):
            logger.debug(f"Request payload: {json.dumps(kwargs['json'], indent=2)}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Log response
            logger.info(f"Response status: {response.status_code}")
            if response.text:
                try:
                    logger.debug(f"Response body: {json.dumps(response.json(), indent=2)}")
                except:
                    logger.debug(f"Response text: {response.text[:500]}")
            
            # Raise for status
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)
    
    def postman_import(self, postman_collection_path: str):
        """Import and convert Postman collection to test cases"""
        import json
        with open(postman_collection_path, 'r') as f:
            collection = json.load(f)
        
        tests = []
        for item in collection.get('item', []):
            test_case = {
                'name': item['name'],
                'method': item['request']['method'],
                'url': item['request']['url']['raw'],
                'headers': item['request'].get('header', []),
                'body': item['request'].get('body', {}),
                'tests': item.get('event', [])
            }
            tests.append(test_case)
        
        logger.info(f"Imported {len(tests)} tests from Postman collection")
        return tests