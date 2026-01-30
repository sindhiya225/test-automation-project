"""
Advanced logging configuration for the test framework.
Supports multiple log levels, file rotation, and structured logging.
"""
import logging
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.threadName
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        return json.dumps(log_entry, default=str)


class ColorFormatter(logging.Formatter):
    """Color formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        
        formatted = super().format(record)
        return f"{level_color}{formatted}{self.COLORS['RESET']}"


class TestLogger:
    """
    Advanced logger for test automation framework.
    Supports multiple handlers, structured logging, and performance tracking.
    """
    
    _loggers: Dict[str, 'TestLogger'] = {}
    
    def __init__(self, name: str, log_dir: str = "logs", level: str = "INFO"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.level = getattr(logging, level.upper())
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        self.logger.propagate = False
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add handlers
        self._setup_handlers()
    
    @classmethod
    def get_logger(cls, name: str = __name__, **kwargs) -> 'TestLogger':
        """Get or create logger instance"""
        if name not in cls._loggers:
            cls._loggers[name] = cls(name, **kwargs)
        return cls._loggers[name]
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        console_formatter = ColorFormatter(console_format, datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
        # File handler for all logs (rotating)
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
        file_formatter = logging.Formatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        
        # JSON handler for structured logging
        json_file = self.log_dir / f"{self.name}_structured.json"
        json_handler = TimedRotatingFileHandler(
            json_file,
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        json_formatter = StructuredFormatter()
        json_handler.setFormatter(json_formatter)
        json_handler.setLevel(logging.INFO)
        self.logger.addHandler(json_handler)
        
        # Error handler for errors only
        error_file = self.log_dir / f"{self.name}_error.log"
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
    
    def set_level(self, level: str):
        """Set logging level"""
        self.level = getattr(logging, level.upper())
        self.logger.setLevel(self.level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(self.level)
    
    def log_test_start(self, test_name: str, test_data: Dict[str, Any] = None):
        """Log test execution start"""
        self.logger.info(f"Starting test: {test_name}", extra={
            "event": "test_start",
            "test_name": test_name,
            "test_data": test_data or {}
        })
    
    def log_test_end(self, test_name: str, status: str, duration: float = None):
        """Log test execution end"""
        self.logger.info(f"Test {status}: {test_name}", extra={
            "event": "test_end",
            "test_name": test_name,
            "status": status,
            "duration": duration
        })
    
    def log_api_call(self, method: str, url: str, status_code: int, duration: float):
        """Log API call details"""
        self.logger.info(f"API {method} {url} - {status_code} ({duration:.2f}s)", extra={
            "event": "api_call",
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration": duration
        })
    
    def log_page_load(self, url: str, duration: float):
        """Log page load details"""
        self.logger.info(f"Page loaded: {url} ({duration:.2f}s)", extra={
            "event": "page_load",
            "url": url,
            "duration": duration
        })
    
    def log_element_interaction(self, action: str, locator: tuple, success: bool):
        """Log element interaction"""
        self.logger.debug(f"Element {action}: {locator} - {'Success' if success else 'Failed'}", extra={
            "event": "element_interaction",
            "action": action,
            "locator": str(locator),
            "success": success
        })
    
    def log_performance(self, metric: str, value: float, threshold: float = None):
        """Log performance metric"""
        extra = {
            "event": "performance",
            "metric": metric,
            "value": value
        }
        
        if threshold is not None:
            extra["threshold"] = threshold
            extra["within_limit"] = value <= threshold
            
            if value > threshold:
                self.logger.warning(f"Performance threshold exceeded: {metric}={value:.2f} > {threshold}", extra=extra)
            else:
                self.logger.info(f"Performance OK: {metric}={value:.2f} <= {threshold}", extra=extra)
        else:
            self.logger.info(f"Performance: {metric}={value:.2f}", extra=extra)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related event"""
        self.logger.warning(f"Security event: {event_type}", extra={
            "event": "security",
            "event_type": event_type,
            "details": details
        })
    
    def capture_screenshot_info(self, filename: str, reason: str):
        """Log screenshot capture information"""
        self.logger.info(f"Screenshot saved: {filename}", extra={
            "event": "screenshot",
            "filename": filename,
            "reason": reason
        })
    
    def log_bug_report(self, bug_id: str, test_name: str, error: str):
        """Log bug report creation"""
        self.logger.error(f"Bug report created: {bug_id} for test {test_name}", extra={
            "event": "bug_report",
            "bug_id": bug_id,
            "test_name": test_name,
            "error": error
        })
    
    # Convenience methods
    def debug(self, msg: str, **kwargs):
        """Log debug message"""
        self.logger.debug(msg, extra=kwargs)
    
    def info(self, msg: str, **kwargs):
        """Log info message"""
        self.logger.info(msg, extra=kwargs)
    
    def warning(self, msg: str, **kwargs):
        """Log warning message"""
        self.logger.warning(msg, extra=kwargs)
    
    def error(self, msg: str, **kwargs):
        """Log error message"""
        self.logger.error(msg, extra=kwargs)
    
    def critical(self, msg: str, **kwargs):
        """Log critical message"""
        self.logger.critical(msg, extra=kwargs)
    
    def exception(self, msg: str, exc_info: bool = True, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(msg, exc_info=exc_info, extra=kwargs)
    
    def get_log_file_path(self, handler_type: str = "file") -> Optional[Path]:
        """Get log file path for specific handler"""
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler) and handler_type == "file":
                return Path(handler.baseFilename)
            elif isinstance(handler, TimedRotatingFileHandler) and handler_type == "json":
                return Path(handler.baseFilename)
        return None
    
    def clear_handlers(self):
        """Clear all logging handlers"""
        self.logger.handlers.clear()
    
    def add_custom_handler(self, handler: logging.Handler):
        """Add custom logging handler"""
        self.logger.addHandler(handler)


# Default logger instance
logger = TestLogger.get_logger("TestFramework")