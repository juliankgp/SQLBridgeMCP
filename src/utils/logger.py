"""
Logging configuration and utilities for SQLBridgeMCP
Provides structured logging with security audit trail and performance monitoring
"""
import os
import sys
import logging
import logging.handlers
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from dataclasses import dataclass, asdict

from config.settings import get_mcp_config

@dataclass
class LogEntry:
    """
    Structured log entry for audit trail and monitoring
    
    Attributes:
        timestamp: ISO timestamp of the log entry
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Name of the logger that created this entry
        message: Log message content
        user_id: User identifier for audit trail
        session_id: Session identifier for tracking
        operation: Type of operation being performed
        database: Target database name
        query_hash: Hash of the SQL query for tracking
        execution_time_ms: Query execution time in milliseconds
        result_count: Number of results returned
        metadata: Additional metadata dictionary
    """
    timestamp: str
    level: str
    logger_name: str
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    database: Optional[str] = None
    query_hash: Optional[int] = None
    execution_time_ms: Optional[float] = None
    result_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class SecurityAuditFilter(logging.Filter):
    """
    Custom logging filter for security audit events
    Adds security-specific context to log records
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and enhance log records with security context
        
        Args:
            record: Log record to filter
            
        Returns:
            bool: True if record should be logged
        """
        # Add security audit flag
        if hasattr(record, 'security_event'):
            record.audit_level = 'SECURITY'
        
        # Add request context if available
        if not hasattr(record, 'user_id'):
            record.user_id = getattr(record, 'user_id', 'unknown')
        
        if not hasattr(record, 'session_id'):
            record.session_id = getattr(record, 'session_id', 'unknown')
        
        return True

class PerformanceFormatter(logging.Formatter):
    """
    Custom formatter for performance and security logging
    Outputs structured JSON logs for better parsing and monitoring
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON
        
        Args:
            record: Log record to format
            
        Returns:
            str: Formatted log message as JSON
        """
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            user_id=getattr(record, 'user_id', None),
            session_id=getattr(record, 'session_id', None),
            operation=getattr(record, 'operation', None),
            database=getattr(record, 'database', None),
            query_hash=getattr(record, 'query_hash', None),
            execution_time_ms=getattr(record, 'execution_time_ms', None),
            result_count=getattr(record, 'result_count', None),
            metadata=getattr(record, 'metadata', None)
        )
        
        # Convert to dict and remove None values
        log_dict = {k: v for k, v in asdict(log_entry).items() if v is not None}
        
        # Add exception info if present
        if record.exc_info:
            log_dict['exception'] = self.formatException(record.exc_info)
        
        try:
            return json.dumps(log_dict, ensure_ascii=False)
        except (TypeError, ValueError):
            # Fallback to simple format if JSON serialization fails
            return f"{log_entry.timestamp} [{log_entry.level}] {log_entry.logger_name}: {log_entry.message}"

class SQLBridgeLogger:
    """
    Main logger class for SQLBridgeMCP with security and performance monitoring
    Implements singleton pattern for consistent logging across the application
    """
    
    _instance: Optional['SQLBridgeLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'SQLBridgeLogger':
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger configuration"""
        if not self._initialized:
            self.config = get_mcp_config()
            self.logs_dir = Path("logs")
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self) -> None:
        """
        Set up logging configuration with handlers and formatters
        """
        # Create logs directory if it doesn't exist
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.log_level, logging.INFO))
        
        # Remove existing handlers to prevent duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler for application logs (with rotation)
        app_log_file = self.logs_dir / "sqlbridge.log"
        file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, self.config.log_level, logging.INFO))
        file_formatter = PerformanceFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Security audit log handler
        security_log_file = self.logs_dir / "security_audit.log"
        security_handler = logging.handlers.RotatingFileHandler(
            security_log_file,
            maxBytes=50*1024*1024,  # 50MB for security logs
            backupCount=10
        )
        security_handler.setLevel(logging.WARNING)  # Only warnings and errors
        security_handler.addFilter(SecurityAuditFilter())
        security_handler.setFormatter(PerformanceFormatter())
        
        # Create security logger
        security_logger = logging.getLogger('security')
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.WARNING)
        
        # Performance log handler  
        performance_log_file = self.logs_dir / "performance.log"
        performance_handler = logging.handlers.RotatingFileHandler(
            performance_log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=5
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(PerformanceFormatter())
        
        # Create performance logger
        perf_logger = logging.getLogger('performance')
        perf_logger.addHandler(performance_handler)
        perf_logger.setLevel(logging.INFO)
        
        logging.info(f"Logging initialized - Level: {self.config.log_level}, Logs dir: {self.logs_dir}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(name)
    
    def get_security_logger(self) -> logging.Logger:
        """
        Get the security audit logger
        
        Returns:
            logging.Logger: Security audit logger
        """
        return logging.getLogger('security')
    
    def get_performance_logger(self) -> logging.Logger:
        """
        Get the performance monitoring logger
        
        Returns:
            logging.Logger: Performance logger
        """
        return logging.getLogger('performance')
    
    def log_query_execution(self, 
                          query: str,
                          database: str,
                          user_id: str,
                          execution_time_ms: float,
                          result_count: int,
                          success: bool,
                          error_msg: Optional[str] = None,
                          session_id: Optional[str] = None) -> None:
        """
        Log SQL query execution with performance metrics
        
        Args:
            query: SQL query that was executed
            database: Target database name
            user_id: User who executed the query
            execution_time_ms: Query execution time in milliseconds
            result_count: Number of results returned
            success: Whether the query was successful
            error_msg: Error message if query failed
            session_id: Session identifier
        """
        perf_logger = self.get_performance_logger()
        
        # Create log record with extra context
        extra = {
            'user_id': user_id,
            'session_id': session_id,
            'operation': 'query_execution',
            'database': database,
            'query_hash': hash(query),
            'execution_time_ms': execution_time_ms,
            'result_count': result_count,
            'metadata': {
                'query_preview': query[:100] + '...' if len(query) > 100 else query,
                'success': success,
                'error': error_msg
            }
        }
        
        if success:
            perf_logger.info(
                f"Query executed successfully - {result_count} rows in {execution_time_ms:.2f}ms",
                extra=extra
            )
        else:
            perf_logger.error(
                f"Query execution failed: {error_msg}",
                extra=extra
            )
    
    def log_security_event(self,
                          event_type: str,
                          severity: str,
                          message: str,
                          user_id: str,
                          additional_data: Optional[Dict[str, Any]] = None,
                          session_id: Optional[str] = None) -> None:
        """
        Log security-related events for audit trail
        
        Args:
            event_type: Type of security event (e.g., 'blocked_query', 'rate_limit_exceeded')
            severity: Event severity ('warning', 'error', 'critical')
            message: Descriptive message about the event
            user_id: User involved in the event
            additional_data: Additional event metadata
            session_id: Session identifier
        """
        security_logger = self.get_security_logger()
        
        extra = {
            'user_id': user_id,
            'session_id': session_id,
            'operation': 'security_event',
            'security_event': True,
            'metadata': {
                'event_type': event_type,
                'severity': severity,
                **(additional_data or {})
            }
        }
        
        log_level = getattr(logging, severity.upper(), logging.WARNING)
        security_logger.log(log_level, message, extra=extra)
    
    def log_connection_event(self,
                           event_type: str,
                           database: str,
                           success: bool,
                           error_msg: Optional[str] = None,
                           connection_time_ms: Optional[float] = None) -> None:
        """
        Log database connection events
        
        Args:
            event_type: Type of connection event ('connect', 'disconnect', 'health_check')
            database: Database name
            success: Whether the connection was successful
            error_msg: Error message if connection failed
            connection_time_ms: Connection time in milliseconds
        """
        logger = self.get_logger('database.connection')
        
        extra = {
            'operation': 'connection_event',
            'database': database,
            'execution_time_ms': connection_time_ms,
            'metadata': {
                'event_type': event_type,
                'success': success,
                'error': error_msg
            }
        }
        
        if success:
            logger.info(f"Database {event_type} successful", extra=extra)
        else:
            logger.error(f"Database {event_type} failed: {error_msg}", extra=extra)

# Global logger instance
_sql_bridge_logger: Optional[SQLBridgeLogger] = None

def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get a configured logger instance
    
    Args:
        name: Logger name (defaults to calling module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    global _sql_bridge_logger
    if _sql_bridge_logger is None:
        _sql_bridge_logger = SQLBridgeLogger()
    
    return _sql_bridge_logger.get_logger(name)

def get_security_logger() -> logging.Logger:
    """
    Get the security audit logger
    
    Returns:
        logging.Logger: Security audit logger
    """
    global _sql_bridge_logger
    if _sql_bridge_logger is None:
        _sql_bridge_logger = SQLBridgeLogger()
    
    return _sql_bridge_logger.get_security_logger()

def get_performance_logger() -> logging.Logger:
    """
    Get the performance monitoring logger
    
    Returns:
        logging.Logger: Performance logger
    """
    global _sql_bridge_logger
    if _sql_bridge_logger is None:
        _sql_bridge_logger = SQLBridgeLogger()
    
    return _sql_bridge_logger.get_performance_logger()

def log_query_execution(query: str,
                       database: str,
                       user_id: str,
                       execution_time_ms: float,
                       result_count: int,
                       success: bool,
                       error_msg: Optional[str] = None,
                       session_id: Optional[str] = None) -> None:
    """
    Convenience function to log query execution
    
    Args:
        query: SQL query that was executed
        database: Target database name
        user_id: User who executed the query
        execution_time_ms: Query execution time in milliseconds
        result_count: Number of results returned
        success: Whether the query was successful
        error_msg: Error message if query failed
        session_id: Session identifier
    """
    global _sql_bridge_logger
    if _sql_bridge_logger is None:
        _sql_bridge_logger = SQLBridgeLogger()
    
    _sql_bridge_logger.log_query_execution(
        query, database, user_id, execution_time_ms, 
        result_count, success, error_msg, session_id
    )

def log_security_event(event_type: str,
                      severity: str,
                      message: str,
                      user_id: str,
                      additional_data: Optional[Dict[str, Any]] = None,
                      session_id: Optional[str] = None) -> None:
    """
    Convenience function to log security events
    
    Args:
        event_type: Type of security event
        severity: Event severity ('warning', 'error', 'critical')
        message: Descriptive message about the event
        user_id: User involved in the event
        additional_data: Additional event metadata
        session_id: Session identifier
    """
    global _sql_bridge_logger
    if _sql_bridge_logger is None:
        _sql_bridge_logger = SQLBridgeLogger()
    
    _sql_bridge_logger.log_security_event(
        event_type, severity, message, user_id, additional_data, session_id
    )