"""
Utility functions and helper classes for the test framework.
Contains reusable utilities for various testing tasks.
"""
import os
import sys
import json
import yaml
import csv
import random
import string
import time
import hashlib
import subprocess
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import inspect
import tempfile
import zipfile
import io
from PIL import Image
import numpy as np


class TestUtilities:
    """Collection of test utility functions"""
    
    @staticmethod
    def generate_random_string(length: int = 10, include_special: bool = False) -> str:
        """Generate random string"""
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_random_email() -> str:
        """Generate random email address"""
        domains = ["test.com", "example.com", "demo.net", "sample.org"]
        username = TestUtilities.generate_random_string(8)
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_random_phone() -> str:
        """Generate random phone number"""
        area_code = random.randint(200, 999)
        prefix = random.randint(200, 999)
        line = random.randint(1000, 9999)
        return f"({area_code}) {prefix}-{line}"
    
    @staticmethod
    def generate_test_data(count: int = 10) -> List[Dict[str, Any]]:
        """Generate test data"""
        test_data = []
        
        for i in range(count):
            data = {
                "id": i + 1,
                "name": f"Test User {i+1}",
                "email": TestUtilities.generate_random_email(),
                "phone": TestUtilities.generate_random_phone(),
                "address": f"{random.randint(1, 999)} Test St",
                "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                "zip_code": str(random.randint(10000, 99999)),
                "created_at": datetime.now().isoformat(),
                "active": random.choice([True, False])
            }
            test_data.append(data)
        
        return test_data
    
    @staticmethod
    def calculate_md5(filepath: str) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @staticmethod
    def compare_files(file1: str, file2: str) -> bool:
        """Compare two files"""
        if not os.path.exists(file1) or not os.path.exists(file2):
            return False
        
        if os.path.getsize(file1) != os.path.getsize(file2):
            return False
        
        return TestUtilities.calculate_md5(file1) == TestUtilities.calculate_md5(file2)
    
    @staticmethod
    def wait_for_condition(condition: Callable, timeout: int = 30, 
                          interval: float = 0.5, message: str = None) -> bool:
        """Wait for a condition to be true"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if condition():
                    return True
            except Exception:
                pass
            
            time.sleep(interval)
        
        if message:
            print(f"Timeout waiting for condition: {message}")
        
        return False
    
    @staticmethod
    def retry_on_exception(func: Callable, max_attempts: int = 3, 
                          delay: float = 1, exceptions: tuple = (Exception,)):
        """Decorator to retry function on exception"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(delay * attempt)  # Exponential backoff
                    else:
                        raise last_exception
            
            raise last_exception
        
        return wrapper
    
    @staticmethod
    def execute_command(cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Execute shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            
            return {
                "success": True,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "returncode": e.returncode,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": str(e)
            }
        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "timeout": True,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def parse_json_response(response_text: str) -> Dict[str, Any]:
        """Parse JSON response with error handling"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # Try to extract JSON from messy response
            lines = response_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        return json.loads(line)
                    except:
                        continue
            
            raise ValueError(f"Invalid JSON response: {e}")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Supports various formats
        patterns = [
            r'^\(\d{3}\) \d{3}-\d{4}$',  # (123) 456-7890
            r'^\d{3}-\d{3}-\d{4}$',      # 123-456-7890
            r'^\d{10}$',                 # 1234567890
            r'^\d{3}\.\d{3}\.\d{4}$',    # 123.456.7890
            r'^\+\d{1,3}\s\d{3}\s\d{3}\s\d{4}$'  # +1 123 456 7890
        ]
        
        return any(bool(re.match(pattern, phone)) for pattern in patterns)


class DataGenerator:
    """Generate test data for various scenarios"""
    
    def __init__(self, locale: str = 'en_US'):
        from faker import Faker
        self.faker = Faker(locale)
    
    def generate_user_data(self, role: str = "user") -> Dict[str, Any]:
        """Generate user data"""
        user = {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "password": self.faker.password(length=12),
            "phone": self.faker.phone_number(),
            "address": self.faker.address().replace('\n', ', '),
            "city": self.faker.city(),
            "state": self.faker.state_abbr(),
            "zip_code": self.faker.zipcode(),
            "country": self.faker.country_code(),
            "company": self.faker.company(),
            "job_title": self.faker.job(),
            "date_of_birth": self.faker.date_of_birth(minimum_age=18, maximum_age=65).isoformat(),
            "ssn": self.faker.ssn(),
            "credit_card": self.faker.credit_card_number(),
            "credit_card_expiry": self.faker.credit_card_expire(),
            "credit_card_cvv": self.faker.credit_card_security_code(),
            "role": role,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        
        return user
    
    def generate_product_data(self) -> Dict[str, Any]:
        """Generate product data"""
        categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Toys"]
        
        product = {
            "name": self.faker.catch_phrase(),
            "description": self.faker.text(max_nb_chars=200),
            "sku": f"SKU-{self.faker.random_number(digits=8)}",
            "category": random.choice(categories),
            "price": round(random.uniform(10, 1000), 2),
            "currency": "USD",
            "stock_quantity": random.randint(0, 1000),
            "weight": round(random.uniform(0.1, 50), 2),
            "weight_unit": random.choice(["kg", "lb", "g"]),
            "manufacturer": self.faker.company(),
            "manufacturer_part_number": f"MPN-{self.faker.random_number(digits=10)}",
            "created_at": datetime.now().isoformat()
        }
        
        return product
    
    def generate_order_data(self, user_id: int = None, product_count: int = 3) -> Dict[str, Any]:
        """Generate order data"""
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{self.faker.random_number(digits=6)}"
        
        # Generate order items
        items = []
        total_amount = 0
        
        for i in range(product_count):
            quantity = random.randint(1, 5)
            unit_price = round(random.uniform(10, 500), 2)
            item_total = round(quantity * unit_price, 2)
            
            items.append({
                "product_id": i + 1,
                "product_name": self.faker.word().capitalize(),
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": item_total
            })
            
            total_amount += item_total
        
        order = {
            "order_number": order_number,
            "user_id": user_id or random.randint(1, 100),
            "status": random.choice(["pending", "processing", "shipped", "delivered"]),
            "items": items,
            "total_amount": round(total_amount, 2),
            "currency": "USD",
            "shipping_address": self.faker.address().replace('\n', ', '),
            "billing_address": self.faker.address().replace('\n', ', '),
            "payment_method": random.choice(["credit_card", "paypal", "bank_transfer"]),
            "payment_status": random.choice(["pending", "paid", "failed"]),
            "created_at": datetime.now().isoformat(),
            "estimated_delivery": (datetime.now() + timedelta(days=random.randint(3, 14))).isoformat()
        }
        
        return order
    
    def generate_bulk_data(self, data_type: str, count: int = 100) -> List[Dict[str, Any]]:
        """Generate bulk test data"""
        data = []
        
        for i in range(count):
            if data_type == "user":
                item = self.generate_user_data()
            elif data_type == "product":
                item = self.generate_product_data()
            elif data_type == "order":
                item = self.generate_order_data()
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            item["id"] = i + 1
            data.append(item)
        
        return data


class PerformanceTimer:
    """Performance timing and measurement utility"""
    
    def __init__(self):
        self.timings = {}
        self.start_times = {}
    
    def start(self, name: str):
        """Start timing for a named operation"""
        self.start_times[name] = time.perf_counter()
    
    def stop(self, name: str) -> float:
        """Stop timing and return duration"""
        if name not in self.start_times:
            raise KeyError(f"No timer started for '{name}'")
        
        end_time = time.perf_counter()
        duration = end_time - self.start_times[name]
        
        if name not in self.timings:
            self.timings[name] = []
        
        self.timings[name].append(duration)
        del self.start_times[name]
        
        return duration
    
    @contextlib.contextmanager
    def measure(self, name: str):
        """Context manager for timing code blocks"""
        self.start(name)
        try:
            yield
        finally:
            self.stop(name)
    
    def get_stats(self, name: str = None) -> Dict[str, Any]:
        """Get timing statistics"""
        if name:
            if name not in self.timings:
                return {}
            
            timings = self.timings[name]
            return {
                "name": name,
                "count": len(timings),
                "total": sum(timings),
                "average": sum(timings) / len(timings),
                "min": min(timings),
                "max": max(timings),
                "last": timings[-1] if timings else 0
            }
        else:
            stats = {}
            for name in self.timings:
                stats[name] = self.get_stats(name)
            return stats
    
    def reset(self, name: str = None):
        """Reset timings"""
        if name:
            if name in self.timings:
                del self.timings[name]
            if name in self.start_times:
                del self.start_times[name]
        else:
            self.timings.clear()
            self.start_times.clear()
    
    def log_stats(self, logger=None):
        """Log timing statistics"""
        stats = self.get_stats()
        
        if not stats:
            return
        
        output = ["Performance Statistics:"]
        output.append("-" * 50)
        
        for name, stat in stats.items():
            output.append(f"{name}:")
            output.append(f"  Count: {stat['count']}")
            output.append(f"  Total: {stat['total']:.4f}s")
            output.append(f"  Average: {stat['average']:.4f}s")
            output.append(f"  Min: {stat['min']:.4f}s")
            output.append(f"  Max: {stat['max']:.4f}s")
            output.append(f"  Last: {stat['last']:.4f}s")
            output.append("")
        
        result = '\n'.join(output)
        
        if logger:
            logger.info(result)
        else:
            print(result)


class FileHandler:
    """File handling utilities for test data"""
    
    @staticmethod
    def read_json(filepath: str) -> Dict[str, Any]:
        """Read JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(filepath: str, data: Dict[str, Any], indent: int = 2):
        """Write JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def read_yaml(filepath: str) -> Dict[str, Any]:
        """Read YAML file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def write_yaml(filepath: str, data: Dict[str, Any]):
        """Write YAML file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    @staticmethod
    def read_csv(filepath: str) -> List[Dict[str, str]]:
        """Read CSV file"""
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    @staticmethod
    def write_csv(filepath: str, data: List[Dict[str, Any]], fieldnames: List[str] = None):
        """Write CSV file"""
        if not data:
            return
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    @staticmethod
    def compare_images(image1_path: str, image2_path: str, threshold: float = 0.99) -> Dict[str, Any]:
        """Compare two images and return similarity score"""
        try:
            # Open images
            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)
            
            # Convert to same mode and size
            if img1.mode != img2.mode:
                img2 = img2.convert(img1.mode)
            
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
            
            # Convert to numpy arrays
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            
            # Calculate similarity
            if arr1.shape != arr2.shape:
                return {
                    "similar": False,
                    "similarity": 0,
                    "error": "Image shapes don't match"
                }
            
            # Normalize and compare
            arr1_norm = arr1.astype(float) / 255.0
            arr2_norm = arr2.astype(float) / 255.0
            
            # Calculate mean squared error
            mse = np.mean((arr1_norm - arr2_norm) ** 2)
            
            # Calculate similarity (1 - normalized MSE)
            similarity = 1.0 - mse
            
            result = {
                "similar": similarity >= threshold,
                "similarity": float(similarity),
                "mse": float(mse),
                "threshold": threshold,
                "image1_size": img1.size,
                "image1_mode": img1.mode,
                "image2_size": img2.size,
                "image2_mode": img2.mode
            }
            
            return result
            
        except Exception as e:
            return {
                "similar": False,
                "similarity": 0,
                "error": str(e)
            }
    
    @staticmethod
    def compress_directory(source_dir: str, output_zip: str):
        """Compress directory to zip file"""
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
    
    @staticmethod
    def create_temp_file(content: str = "", suffix: str = ".tmp") -> str:
        """Create temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            return f.name
    
    @staticmethod
    def create_temp_dir() -> str:
        """Create temporary directory"""
        return tempfile.mkdtemp()


# Global utility instances
test_utils = TestUtilities()
data_generator = DataGenerator()
performance_timer = PerformanceTimer()
file_handler = FileHandler()