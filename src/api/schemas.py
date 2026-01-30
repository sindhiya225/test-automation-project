"""
JSON schema definitions for API response validation.
Ensures consistent data structures across API responses.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

# Common schema components
COMMON_SCHEMAS = {
    "timestamp": {
        "type": "string",
        "format": "date-time",
        "description": "ISO 8601 timestamp"
    },
    "error": {
        "type": "object",
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"},
            "details": {"type": "string"}
        },
        "required": ["code", "message"]
    },
    "pagination": {
        "type": "object",
        "properties": {
            "page": {"type": "integer", "minimum": 1},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            "total": {"type": "integer", "minimum": 0},
            "pages": {"type": "integer", "minimum": 0}
        },
        "required": ["page", "limit", "total", "pages"]
    }
}

# Authentication schemas
AuthResponseSchema = {
    "type": "object",
    "properties": {
        "access_token": {"type": "string"},
        "refresh_token": {"type": "string"},
        "token_type": {"type": "string", "enum": ["Bearer"]},
        "expires_in": {"type": "integer", "minimum": 60},
        "user": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "role": {"type": "string"}
            },
            "required": ["id", "username", "email"]
        },
        "timestamp": COMMON_SCHEMAS["timestamp"]
    },
    "required": ["access_token", "token_type", "expires_in", "user"]
}

RefreshTokenSchema = {
    "type": "object",
    "properties": {
        "access_token": {"type": "string"},
        "refresh_token": {"type": "string"},
        "token_type": {"type": "string", "enum": ["Bearer"]},
        "expires_in": {"type": "integer"}
    },
    "required": ["access_token", "token_type"]
}

# User schemas
UserSchema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "username": {"type": "string", "minLength": 3, "maxLength": 50},
        "email": {"type": "string", "format": "email"},
        "first_name": {"type": "string", "minLength": 1, "maxLength": 50},
        "last_name": {"type": "string", "minLength": 1, "maxLength": 50},
        "role": {"type": "string", "enum": ["admin", "user", "viewer", "qa", "devops", "finance"]},
        "is_active": {"type": "boolean"},
        "created_at": COMMON_SCHEMAS["timestamp"],
        "updated_at": COMMON_SCHEMAS["timestamp"],
        "last_login": COMMON_SCHEMAS["timestamp"],
        "department": {"type": "string"},
        "employee_id": {"type": "string"},
        "permissions": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["id", "username", "email", "role", "is_active", "created_at"]
}

UserListSchema = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": UserSchema
        },
        "pagination": COMMON_SCHEMAS["pagination"],
        "timestamp": COMMON_SCHEMAS["timestamp"]
    },
    "required": ["data", "pagination"]
}

CreateUserSchema = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "minLength": 3, "maxLength": 50},
        "email": {"type": "string", "format": "email"},
        "password": {
            "type": "string",
            "minLength": 8,
            "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$"
        },
        "first_name": {"type": "string", "minLength": 1, "maxLength": 50},
        "last_name": {"type": "string", "minLength": 1, "maxLength": 50},
        "role": {"type": "string", "enum": ["admin", "user", "viewer", "qa", "devops", "finance"]},
        "department": {"type": "string"}
    },
    "required": ["username", "email", "password"]
}

# Product schemas
ProductSchema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1, "maxLength": 100},
        "description": {"type": "string"},
        "sku": {"type": "string", "pattern": "^[A-Z0-9-]+$"},
        "category": {"type": "string"},
        "price": {"type": "number", "minimum": 0, "exclusiveMinimum": True},
        "currency": {"type": "string", "enum": ["USD", "EUR", "GBP"]},
        "stock_quantity": {"type": "integer", "minimum": 0},
        "in_stock": {"type": "boolean"},
        "weight": {"type": "number", "minimum": 0},
        "weight_unit": {"type": "string", "enum": ["g", "kg", "lb", "oz"]},
        "dimensions": {
            "type": "object",
            "properties": {
                "length": {"type": "number", "minimum": 0},
                "width": {"type": "number", "minimum": 0},
                "height": {"type": "number", "minimum": 0},
                "unit": {"type": "string", "enum": ["cm", "in", "mm"]}
            }
        },
        "manufacturer": {"type": "string"},
        "created_at": COMMON_SCHEMAS["timestamp"],
        "updated_at": COMMON_SCHEMAS["timestamp"]
    },
    "required": ["id", "name", "sku", "price", "stock_quantity", "in_stock"]
}

ProductListSchema = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": ProductSchema
        },
        "pagination": COMMON_SCHEMAS["pagination"],
        "timestamp": COMMON_SCHEMAS["timestamp"]
    },
    "required": ["data", "pagination"]
}

# Order schemas
OrderItemSchema = {
    "type": "object",
    "properties": {
        "product_id": {"type": "integer", "minimum": 1},
        "product_name": {"type": "string"},
        "quantity": {"type": "integer", "minimum": 1},
        "unit_price": {"type": "number", "minimum": 0},
        "total_price": {"type": "number", "minimum": 0}
    },
    "required": ["product_id", "quantity", "unit_price", "total_price"]
}

OrderSchema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "order_number": {"type": "string", "pattern": "^ORD-[0-9]{8}-[0-9]{6}$"},
        "user_id": {"type": "integer", "minimum": 1},
        "status": {
            "type": "string",
            "enum": ["pending", "processing", "shipped", "delivered", "cancelled", "refunded"]
        },
        "items": {
            "type": "array",
            "items": OrderItemSchema,
            "minItems": 1
        },
        "total_amount": {"type": "number", "minimum": 0},
        "currency": {"type": "string", "enum": ["USD", "EUR", "GBP"]},
        "shipping_address": {"type": "string"},
        "billing_address": {"type": "string"},
        "payment_method": {"type": "string"},
        "payment_status": {"type": "string", "enum": ["pending", "paid", "failed", "refunded"]},
        "created_at": COMMON_SCHEMAS["timestamp"],
        "updated_at": COMMON_SCHEMAS["timestamp"],
        "estimated_delivery": COMMON_SCHEMAS["timestamp"]
    },
    "required": ["id", "order_number", "user_id", "status", "items", "total_amount", "created_at"]
}

OrderListSchema = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": OrderSchema
        },
        "pagination": COMMON_SCHEMAS["pagination"],
        "timestamp": COMMON_SCHEMAS["timestamp"]
    },
    "required": ["data", "pagination"]
}

# Error schemas
ErrorSchema = {
    "type": "object",
    "properties": {
        "error": COMMON_SCHEMAS["error"],
        "timestamp": COMMON_SCHEMAS["timestamp"],
        "path": {"type": "string"},
        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]}
    },
    "required": ["error", "timestamp", "path", "method"]
}

ValidationErrorSchema = {
    "type": "object",
    "properties": {
        "errors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "string"}
                },
                "required": ["field", "message"]
            }
        },
        "timestamp": COMMON_SCHEMAS["timestamp"]
    },
    "required": ["errors", "timestamp"]
}

# System schemas
HealthCheckSchema = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["UP", "DOWN", "DEGRADED"]},
        "components": {
            "type": "object",
            "properties": {
                "database": {"type": "string", "enum": ["UP", "DOWN"]},
                "cache": {"type": "string", "enum": ["UP", "DOWN"]},
                "storage": {"type": "string", "enum": ["UP", "DOWN"]},
                "messaging": {"type": "string", "enum": ["UP", "DOWN"]}
            }
        },
        "timestamp": COMMON_SCHEMAS["timestamp"],
        "uptime": {"type": "number", "minimum": 0},
        "version": {"type": "string"}
    },
    "required": ["status", "timestamp"]
}

MetricsSchema = {
    "type": "object",
    "properties": {
        "system": {
            "type": "object",
            "properties": {
                "cpu_usage": {"type": "number", "minimum": 0, "maximum": 100},
                "memory_usage": {"type": "number", "minimum": 0, "maximum": 100},
                "disk_usage": {"type": "number", "minimum": 0, "maximum": 100},
                "active_connections": {"type": "integer", "minimum": 0}
            }
        },
        "application": {
            "type": "object",
            "properties": {
                "total_requests": {"type": "integer", "minimum": 0},
                "requests_per_minute": {"type": "number", "minimum": 0},
                "error_rate": {"type": "number", "minimum": 0, "maximum": 100},
                "average_response_time": {"type": "number", "minimum": 0}
            }
        },
        "timestamp": COMMON_SCHEMAS["timestamp"]
    },
    "required": ["system", "application", "timestamp"]
}

# Schema registry
SCHEMA_REGISTRY = {
    "auth_response": AuthResponseSchema,
    "refresh_token": RefreshTokenSchema,
    "user": UserSchema,
    "user_list": UserListSchema,
    "create_user": CreateUserSchema,
    "product": ProductSchema,
    "product_list": ProductListSchema,
    "order": OrderSchema,
    "order_list": OrderListSchema,
    "error": ErrorSchema,
    "validation_error": ValidationErrorSchema,
    "health_check": HealthCheckSchema,
    "metrics": MetricsSchema
}


class SchemaValidator:
    """Utility class for schema validation"""
    
    @staticmethod
    def get_schema(schema_name: str) -> Dict[str, Any]:
        """Get schema by name"""
        if schema_name not in SCHEMA_REGISTRY:
            raise ValueError(f"Schema '{schema_name}' not found in registry")
        return SCHEMA_REGISTRY[schema_name]
    
    @staticmethod
    def validate(schema_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against schema.
        
        Args:
            schema_name: Name of the schema to validate against
            data: Data to validate
            
        Returns:
            Dictionary with validation results
        """
        from jsonschema import validate as jsonschema_validate
        from jsonschema.exceptions import ValidationError
        
        schema = SchemaValidator.get_schema(schema_name)
        
        try:
            jsonschema_validate(instance=data, schema=schema)
            return {
                "valid": True,
                "errors": [],
                "schema": schema_name
            }
        except ValidationError as e:
            return {
                "valid": False,
                "errors": [{
                    "path": list(e.path) if e.path else [],
                    "message": e.message,
                    "validator": e.validator,
                    "validator_value": e.validator_value
                }],
                "schema": schema_name
            }
    
    @staticmethod
    def validate_multiple(data: Dict[str, Any], schemas: List[str]) -> Dict[str, Any]:
        """
        Validate data against multiple schemas.
        
        Args:
            data: Data to validate
            schemas: List of schema names to try
            
        Returns:
            Dictionary with validation results
        """
        results = {}
        
        for schema_name in schemas:
            result = SchemaValidator.validate(schema_name, data)
            results[schema_name] = result
            
            if result["valid"]:
                return {
                    "valid": True,
                    "matched_schema": schema_name,
                    "all_results": results
                }
        
        return {
            "valid": False,
            "matched_schema": None,
            "all_results": results
        }
    
    @staticmethod
    def generate_schema_example(schema_name: str) -> Dict[str, Any]:
        """Generate example data for a schema"""
        schema = SchemaValidator.get_schema(schema_name)
        
        # Generate example based on schema structure
        example = {}
        
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                example[prop_name] = SchemaValidator._generate_example_value(prop_schema)
        
        return example
    
    @staticmethod
    def _generate_example_value(schema: Dict[str, Any]) -> Any:
        """Generate example value for a schema property"""
        if "type" not in schema:
            return None
        
        data_type = schema["type"]
        
        if data_type == "string":
            if "format" in schema:
                if schema["format"] == "date-time":
                    return datetime.now().isoformat()
                elif schema["format"] == "email":
                    return "example@test.com"
            
            if "enum" in schema:
                return schema["enum"][0]
            
            if "pattern" in schema:
                if schema["pattern"] == "^[A-Z0-9-]+$":
                    return "SKU-12345"
                elif schema["pattern"] == "^ORD-[0-9]{8}-[0-9]{6}$":
                    return "ORD-20240115-123456"
            
            return "example_string"
        
        elif data_type == "integer":
            if "minimum" in schema:
                return schema["minimum"]
            return 1
        
        elif data_type == "number":
            if "minimum" in schema:
                return float(schema["minimum"] + 0.1)
            return 10.5
        
        elif data_type == "boolean":
            return True
        
        elif data_type == "array":
            if "items" in schema:
                item_example = SchemaValidator._generate_example_value(schema["items"])
                return [item_example] * min(schema.get("minItems", 1), 3)
            return []
        
        elif data_type == "object":
            if "properties" in schema:
                example = {}
                for prop_name, prop_schema in schema["properties"].items():
                    example[prop_name] = SchemaValidator._generate_example_value(prop_schema)
                return example
            return {}
        
        return None