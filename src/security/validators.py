"""
Security validators for MCP SQL operations
Provides comprehensive input validation and sanitization
"""
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel, validator, Field
from datetime import datetime, timedelta
import logging

from config.settings import get_database_config

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """
    Security configuration for SQL operations
    
    Attributes:
        max_query_length: Maximum allowed SQL query length
        allowed_query_types: List of allowed SQL query types
        dangerous_patterns: Regex patterns that indicate dangerous queries
        rate_limit_window: Time window for rate limiting (seconds)
        max_requests_per_window: Maximum requests allowed per window
        blocked_keywords: Keywords that are completely blocked
    """
    max_query_length: int = 10000
    allowed_query_types: List[str] = field(default_factory=lambda: ["SELECT"])
    dangerous_patterns: List[str] = field(default_factory=lambda: [
        r';\s*(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE|EXEC|EXECUTE)',
        r'\bUNION\s+SELECT\b',
        r'\bEXEC\s*\(',
        r'\bxp_cmdshell\b',
        r'\bsp_executesql\b',
        r'--.*$',
        r'/\*.*?\*/',
        r'\bSHUTDOWN\b',
        r'\bRESTORE\b',
        r'\bBACKUP\b'
    ])
    rate_limit_window: int = 60  # 1 minute
    max_requests_per_window: int = 100
    blocked_keywords: List[str] = field(default_factory=lambda: [
        'xp_cmdshell', 'sp_executesql', 'openrowset', 'opendatasource',
        'bulk', 'master..xp_', 'exec master', 'exec(', 'execute('
    ])

class SQLQueryRequest(BaseModel):
    """
    Pydantic model for SQL query request validation
    
    Attributes:
        query: SQL query string to validate
        database: Target database name
        user_id: User identifier for rate limiting
        session_id: Session identifier for tracking
    """
    query: str = Field(..., min_length=1, max_length=10000)
    database: Optional[str] = Field(default="default", max_length=100)
    user_id: Optional[str] = Field(default="anonymous", max_length=50)
    session_id: Optional[str] = Field(default=None, max_length=100)
    
    @validator('query')
    def validate_query_content(cls, v):
        """
        Validate SQL query content for security
        
        Args:
            v: Query string to validate
            
        Returns:
            str: Validated and cleaned query
            
        Raises:
            ValueError: If query is invalid or unsafe
        """
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Remove potential SQL comments
        cleaned_query = re.sub(r'--.*$', '', v, flags=re.MULTILINE)
        cleaned_query = re.sub(r'/\*.*?\*/', '', cleaned_query, flags=re.DOTALL)
        
        # Check query length after cleaning
        if len(cleaned_query.strip()) == 0:
            raise ValueError("Query contains only comments")
        
        return cleaned_query.strip()
    
    @validator('database')
    def validate_database_name(cls, v):
        """
        Validate database name format
        
        Args:
            v: Database name to validate
            
        Returns:
            str: Validated database name
            
        Raises:
            ValueError: If database name is invalid
        """
        if v and not re.match(r'^[a-zA-Z0-9_][a-zA-Z0-9_\-]*$', v):
            raise ValueError("Invalid database name format. Only alphanumeric characters, underscores, and hyphens allowed")
        
        return v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """
        Validate user ID format
        
        Args:
            v: User ID to validate
            
        Returns:
            str: Validated user ID
            
        Raises:
            ValueError: If user ID is invalid
        """
        if v and not re.match(r'^[a-zA-Z0-9_@\.-]+$', v):
            raise ValueError("Invalid user ID format")
        
        return v

class TableRequest(BaseModel):
    """
    Pydantic model for table operation request validation
    
    Attributes:
        table_name: Name of the table to operate on
        database: Target database name
        include_sample_data: Whether to include sample data
        user_id: User identifier for rate limiting
    """
    table_name: Optional[str] = Field(None, max_length=128)
    database: Optional[str] = Field(default="default", max_length=100)
    include_sample_data: bool = Field(default=False)
    user_id: Optional[str] = Field(default="anonymous", max_length=50)
    
    @validator('table_name')
    def validate_table_name(cls, v):
        """
        Validate table name format
        
        Args:
            v: Table name to validate
            
        Returns:
            str: Validated table name
            
        Raises:
            ValueError: If table name is invalid
        """
        if v and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError("Invalid table name format. Must start with letter or underscore, followed by alphanumeric characters or underscores")
        
        return v

class RateLimiter:
    """
    Simple in-memory rate limiter for request throttling
    In production, this should use Redis or similar persistent storage
    """
    
    def __init__(self, config: SecurityConfig):
        """
        Initialize rate limiter with security configuration
        
        Args:
            config: Security configuration object
        """
        self.config = config
        self.requests: Dict[str, List[float]] = {}
        
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limiting
        
        Args:
            identifier: Unique identifier for rate limiting (user_id, IP, etc.)
            
        Returns:
            Tuple[bool, Dict]: (is_allowed, rate_limit_info)
        """
        current_time = time.time()
        window_start = current_time - self.config.rate_limit_window
        
        # Clean old requests outside the window
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        current_requests = len(self.requests[identifier])
        
        if current_requests >= self.config.max_requests_per_window:
            return False, {
                "rate_limited": True,
                "current_requests": current_requests,
                "max_requests": self.config.max_requests_per_window,
                "window_seconds": self.config.rate_limit_window,
                "reset_time": window_start + self.config.rate_limit_window
            }
        
        # Add current request
        self.requests[identifier].append(current_time)
        
        return True, {
            "rate_limited": False,
            "current_requests": current_requests + 1,
            "max_requests": self.config.max_requests_per_window,
            "window_seconds": self.config.rate_limit_window
        }

class SecurityValidator:
    """
    Main security validator class for SQL operations
    Provides comprehensive validation and sanitization
    """
    
    def __init__(self):
        """Initialize security validator with configuration"""
        self.config = SecurityConfig()
        self.rate_limiter = RateLimiter(self.config)
        self.db_config = get_database_config()
        
        # Override max_query_length from database config if available
        if hasattr(self.db_config, 'max_query_length'):
            self.config.max_query_length = self.db_config.max_query_length
    
    def validate_sql_query(self, request: SQLQueryRequest) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive SQL query validation
        
        Args:
            request: Validated SQLQueryRequest object
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            query = request.query.upper().strip()
            
            # Check if query type is allowed
            query_type = query.split()[0] if query.split() else ""
            if query_type not in self.config.allowed_query_types:
                return False, f"Query type '{query_type}' not allowed. Only {self.config.allowed_query_types} queries permitted"
            
            # Check for dangerous patterns
            for pattern in self.config.dangerous_patterns:
                if re.search(pattern, query, re.IGNORECASE | re.MULTILINE):
                    logger.warning(f"Dangerous pattern detected in query: {pattern}")
                    return False, f"Query contains potentially dangerous pattern: {pattern}"
            
            # Check for blocked keywords
            for keyword in self.config.blocked_keywords:
                if keyword.lower() in query.lower():
                    logger.warning(f"Blocked keyword detected in query: {keyword}")
                    return False, f"Query contains blocked keyword: {keyword}"
            
            # Additional SQL injection checks
            if self._check_sql_injection_patterns(request.query):
                return False, "Query contains patterns that may indicate SQL injection"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error during query validation: {e}")
            return False, f"Validation error: {e}"
    
    def _check_sql_injection_patterns(self, query: str) -> bool:
        """
        Check for common SQL injection patterns
        
        Args:
            query: SQL query string to check
            
        Returns:
            bool: True if suspicious patterns found
        """
        suspicious_patterns = [
            r"'[^']*'[^']*'",  # Multiple quotes
            r'"\s*;\s*\w+',    # Semicolon with commands
            r'\b1\s*=\s*1\b',  # Always true conditions
            r'\bOR\s+1\s*=\s*1\b',
            r'\bAND\s+1\s*=\s*1\b',
            r"'\s*OR\s*'[^']*'\s*=\s*'[^']*'",  # OR with quotes
            r'WAITFOR\s+DELAY',  # Time-based attacks
            r'BENCHMARK\s*\(',   # MySQL benchmark attacks
            r'SLEEP\s*\(',       # MySQL sleep attacks
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Suspicious SQL injection pattern detected: {pattern}")
                return True
        
        return False
    
    def check_rate_limit(self, user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limiting for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple[bool, Dict]: (is_allowed, rate_limit_info)
        """
        return self.rate_limiter.is_allowed(user_id)
    
    def sanitize_input(self, input_string: str) -> str:
        """
        Sanitize input string by removing potentially dangerous characters
        
        Args:
            input_string: String to sanitize
            
        Returns:
            str: Sanitized string
        """
        if not input_string:
            return ""
        
        # Remove or escape dangerous characters
        sanitized = input_string
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Remove or escape certain control characters
        sanitized = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    def validate_connection_string_safety(self, connection_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that connection string doesn't contain dangerous parameters
        
        Args:
            connection_string: Database connection string to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_safe, error_message)
        """
        dangerous_params = [
            'xp_cmdshell=true',
            'ole automation procedures=true', 
            'Ad Hoc Distributed Queries=true',
            'clr enabled=true',
            'Database Mail XPs=true'
        ]
        
        for param in dangerous_params:
            if param.lower() in connection_string.lower():
                return False, f"Connection string contains dangerous parameter: {param}"
        
        return True, None

# Global validator instance
_security_validator: Optional[SecurityValidator] = None

def get_security_validator() -> SecurityValidator:
    """
    Get the global security validator instance (singleton pattern)
    
    Returns:
        SecurityValidator: Security validator instance
    """
    global _security_validator
    if _security_validator is None:
        _security_validator = SecurityValidator()
    return _security_validator

def validate_and_sanitize_query(query: str, database: str = "default", 
                               user_id: str = "anonymous") -> Tuple[bool, Optional[str], Optional[SQLQueryRequest]]:
    """
    Convenience function to validate and sanitize a SQL query
    
    Args:
        query: SQL query string
        database: Target database name
        user_id: User identifier
        
    Returns:
        Tuple[bool, Optional[str], Optional[SQLQueryRequest]]: 
        (is_valid, error_message, validated_request)
    """
    try:
        # Create request object (this will run Pydantic validation)
        request = SQLQueryRequest(
            query=query,
            database=database,
            user_id=user_id
        )
        
        # Get validator and run security checks
        validator = get_security_validator()
        
        # Check rate limiting
        rate_allowed, rate_info = validator.check_rate_limit(user_id)
        if not rate_allowed:
            return False, f"Rate limit exceeded. {rate_info.get('current_requests', 0)}/{rate_info.get('max_requests', 0)} requests in {rate_info.get('window_seconds', 0)}s window", None
        
        # Validate query security
        is_valid, error_msg = validator.validate_sql_query(request)
        if not is_valid:
            return False, error_msg, None
        
        return True, None, request
        
    except Exception as e:
        logger.error(f"Error in validate_and_sanitize_query: {e}")
        return False, f"Validation error: {e}", None