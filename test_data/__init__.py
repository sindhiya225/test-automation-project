"""
Test data package for managing test data files.
Provides utilities for loading and managing test data in various formats.
"""

import json
import yaml
import csv
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class DataFormat(Enum):
    """Supported data formats"""
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    XML = "xml"
    TXT = "txt"


@dataclass
class TestUser:
    """Test user data model"""
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    role: str
    permissions: List[str]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class TestDataManager:
    """
    Manager for test data loading and manipulation.
    Supports multiple data formats and data generation.
    """
    
    def __init__(self, data_dir: str = "test_data"):
        self.data_dir = data_dir
        self._cache = {}
    
    def load_data(self, filename: str, format_type: DataFormat = None) -> Any:
        """
        Load test data from file.
        
        Args:
            filename: Name of the data file
            format_type: Format of the file (auto-detected if None)
            
        Returns:
            Loaded data
        """
        filepath = os.path.join(self.data_dir, filename)
        
        # Auto-detect format from extension
        if format_type is None:
            ext = os.path.splitext(filename)[1].lower().lstrip('.')
            try:
                format_type = DataFormat(ext)
            except ValueError:
                raise ValueError(f"Unsupported file format: {ext}")
        
        # Check cache
        cache_key = f"{filename}_{format_type.value}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Load based on format
        if format_type == DataFormat.JSON:
            with open(filepath, 'r') as f:
                data = json.load(f)
        elif format_type == DataFormat.YAML:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
        elif format_type == DataFormat.CSV:
            data = self._load_csv(filepath)
        elif format_type == DataFormat.TXT:
            with open(filepath, 'r') as f:
                data = f.read()
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Cache the data
        self._cache[cache_key] = data
        return data
    
    def _load_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Load CSV file and convert to list of dictionaries"""
        data = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    def save_data(self, filename: str, data: Any, format_type: DataFormat = None):
        """
        Save test data to file.
        
        Args:
            filename: Name of the data file
            data: Data to save
            format_type: Format of the file (auto-detected if None)
        """
        filepath = os.path.join(self.data_dir, filename)
        
        # Auto-detect format from extension
        if format_type is None:
            ext = os.path.splitext(filename)[1].lower().lstrip('.')
            try:
                format_type = DataFormat(ext)
            except ValueError:
                raise ValueError(f"Unsupported file format: {ext}")
        
        # Save based on format
        if format_type == DataFormat.JSON:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif format_type == DataFormat.YAML:
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        elif format_type == DataFormat.CSV:
            self._save_csv(filepath, data)
        elif format_type == DataFormat.TXT:
            with open(filepath, 'w') as f:
                f.write(str(data))
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Update cache
        cache_key = f"{filename}_{format_type.value}"
        self._cache[cache_key] = data
    
    def _save_csv(self, filepath: str, data: List[Dict[str, Any]]):
        """Save list of dictionaries to CSV file"""
        if not data:
            return
        
        fieldnames = data[0].keys()
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def get_test_users(self) -> List[TestUser]:
        """Load test users from JSON file"""
        users_data = self.load_data("users.json", DataFormat.JSON)
        users = []
        
        for user_data in users_data.get("users", []):
            user = TestUser(**user_data)
            users.append(user)
        
        return users
    
    def get_user_by_role(self, role: str) -> Optional[TestUser]:
        """Get a test user by role"""
        users = self.get_test_users()
        for user in users:
            if user.role.lower() == role.lower():
                return user
        return None
    
    def get_credentials(self, role: str = "admin") -> Dict[str, str]:
        """Get credentials for a specific role"""
        user = self.get_user_by_role(role)
        if user:
            return {
                "username": user.username,
                "password": user.password,
                "email": user.email
            }
        return {}
    
    def generate_test_data(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate synthetic test data"""
        from faker import Faker
        
        fake = Faker()
        test_data = []
        
        for i in range(count):
            data = {
                "id": i + 1,
                "name": fake.name(),
                "email": fake.email(),
                "address": fake.address(),
                "phone": fake.phone_number(),
                "company": fake.company(),
                "job_title": fake.job(),
                "date_of_birth": fake.date_of_birth().isoformat(),
                "credit_card": fake.credit_card_number(),
                "ssn": fake.ssn(),
                "website": fake.url(),
                "username": fake.user_name(),
                "password": fake.password(length=12),
                "created_at": fake.date_time_this_year().isoformat(),
                "updated_at": fake.date_time_this_month().isoformat()
            }
            test_data.append(data)
        
        return test_data
    
    def clear_cache(self):
        """Clear the data cache"""
        self._cache.clear()
    
    def list_data_files(self) -> List[str]:
        """List all test data files"""
        files = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(('.json', '.yaml', '.yml', '.csv', '.txt')):
                files.append(filename)
        return files


# Global test data manager instance
data_manager = TestDataManager()


def load_test_data(filename: str, format_type: DataFormat = None) -> Any:
    """Convenience function to load test data"""
    return data_manager.load_data(filename, format_type)


def get_test_users() -> List[TestUser]:
    """Convenience function to get test users"""
    return data_manager.get_test_users()


def get_credentials(role: str = "admin") -> Dict[str, str]:
    """Convenience function to get credentials"""
    return data_manager.get_credentials(role)


__all__ = [
    'DataFormat',
    'TestUser',
    'TestDataManager',
    'data_manager',
    'load_test_data',
    'get_test_users',
    'get_credentials'
]