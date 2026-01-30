"""
Utility to run and convert Postman collections to pytest tests
"""
import json
import os
import subprocess
import tempfile
from typing import Dict, List, Any
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)

class PostmanRunner:
    """Utility to integrate Postman collections with pytest framework"""
    
    def __init__(self, newman_path: str = None):
        self.newman_path = newman_path or self._find_newman()
    
    def _find_newman(self) -> str:
        """Find Newman installation path"""
        try:
            # Try to find newman in PATH
            result = subprocess.run(
                ["which", "newman"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Try npm global installation
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "newman", "--parseable"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                paths = result.stdout.strip().split('\n')
                for path in paths:
                    if "newman" in path:
                        return os.path.join(path, "bin", "newman.js")
        except:
            pass
        
        raise EnvironmentError("Newman not found. Please install Newman with 'npm install -g newman'")
    
    def run_collection(
        self,
        collection_path: str,
        environment_path: str = None,
        report_dir: str = "reports/postman",
        **kwargs
    ) -> Dict[str, Any]:
        """Run Postman collection using Newman"""
        
        os.makedirs(report_dir, exist_ok=True)
        
        # Build newman command
        cmd = [
            "newman", "run", collection_path,
            "--reporters", "cli,json,html,junit",
            "--reporter-json-export", f"{report_dir}/newman-report.json",
            "--reporter-html-export", f"{report_dir}/newman-report.html",
            "--reporter-junit-export", f"{report_dir}/newman-report.xml"
        ]
        
        if environment_path:
            cmd.extend(["-e", environment_path])
        
        # Add additional options
        if kwargs.get("iteration_count"):
            cmd.extend(["-n", str(kwargs["iteration_count"])])
        
        if kwargs.get("delay"):
            cmd.extend(["--delay-request", str(kwargs["delay"])])
        
        # Run newman
        logger.info(f"Running Postman collection: {collection_path}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Postman collection executed successfully")
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Postman collection failed: {e}")
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "return_code": e.returncode
            }
    
    def convert_to_pytest(self, collection_path: str, output_dir: str = "tests/postman_converted"):
        """Convert Postman collection to pytest tests"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(collection_path, 'r') as f:
            collection = json.load(f)
        
        test_file_content = self._generate_pytest_file(collection)
        
        output_file = os.path.join(output_dir, "test_postman_collection.py")
        with open(output_file, 'w') as f:
            f.write(test_file_content)
        
        logger.info(f"Postman collection converted to pytest: {output_file}")
        return output_file
    
    def _generate_pytest_file(self, collection: Dict[str, Any]) -> str:
        """Generate pytest test file from Postman collection"""
        
        imports = """
import pytest
import requests
import json
from src.core.api_client import APIClient
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)
"""
        
        test_class = f"""
class TestPostmanCollection:
    \"\"\"Auto-generated tests from Postman collection: {collection.get('info', {}).get('name', 'Unknown')}\"\"\"
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.client = api_client
        self.base_url = "{collection.get('variable', [{}])[0].get('value', '')}"
"""
        
        test_methods = []
        
        for item in collection.get('item', []):
            request = item.get('request', {})
            method = request.get('method', 'GET')
            url = request.get('url', {}).get('raw', '')
            
            # Extract path from URL
            import urllib.parse
            parsed_url = urllib.parse.urlparse(url)
            endpoint = parsed_url.path
            
            # Generate test method
            test_method = f"""
    def test_{self._sanitize_name(item.get('name', 'unnamed'))}(self):
        \"\"\"Test: {item.get('name', 'Unnamed')}\"\"\"
        
        # Request details
        method = "{method}"
        endpoint = "{endpoint}"
        
        # Headers
        headers = {json.dumps({h['key']: h['value'] for h in request.get('header', [])}, indent=8)}
        
        # Body
        body = {json.dumps(request.get('body', {}), indent=8)}
        
        # Make request
        logger.info(f"Making {{method}} request to {{endpoint}}")
        
        if method == "GET":
            response = self.client.get(endpoint, headers=headers)
        elif method == "POST":
            response = self.client.post(endpoint, json=body, headers=headers)
        elif method == "PUT":
            response = self.client.put(endpoint, json=body, headers=headers)
        elif method == "DELETE":
            response = self.client.delete(endpoint, headers=headers)
        else:
            pytest.fail(f"Unsupported method: {{method}}")
        
        # Assertions
        assert response.status_code == 200
        
        # Add more assertions based on Postman tests
        tests = {json.dumps(item.get('event', []), indent=8)}
        
        logger.info(f"Test passed: {{item.get('name', 'Unnamed')}}")
"""
            test_methods.append(test_method)
        
        return imports + test_class + '\n'.join(test_methods)
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize test name for Python method"""
        sanitized = name.lower().replace(' ', '_').replace('-', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
        return sanitized
    
    def generate_collection_report(self, collection_path: str) -> Dict[str, Any]:
        """Generate a report analyzing the Postman collection"""
        
        with open(collection_path, 'r') as f:
            collection = json.load(f)
        
        report = {
            "collection_name": collection.get('info', {}).get('name'),
            "total_requests": len(collection.get('item', [])),
            "methods": {},
            "endpoints": [],
            "authentication": collection.get('auth', {}),
            "variables": collection.get('variable', []),
            "tests_present": False
        }
        
        # Count methods
        for item in collection.get('item', []):
            method = item.get('request', {}).get('method', 'UNKNOWN')
            report["methods"][method] = report["methods"].get(method, 0) + 1
            
            # Check for tests
            events = item.get('event', [])
            for event in events:
                if event.get('listen') == 'test':
                    report["tests_present"] = True
        
        logger.info(f"Postman collection analysis: {report}")
        return report