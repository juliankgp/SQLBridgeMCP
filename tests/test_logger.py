"""
Unit tests for logger utilities module
Tests logging configuration and functionality
"""
import pytest
import tempfile
import os
import json
import sys
from unittest.mock import patch, Mock
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.logger import (
    SQLBridgeLogger, get_logger, get_security_logger, 
    get_performance_logger, log_query_execution, log_security_event
)

class TestSQLBridgeLogger:
    """Test cases for SQLBridgeLogger class"""
    
    def test_sql_bridge_logger_singleton(self):
        """Test SQLBridgeLogger singleton pattern"""
        logger1 = SQLBridgeLogger()
        logger2 = SQLBridgeLogger()
        
        assert logger1 is logger2
    
    def test_logger_initialization(self):
        """Test logger initialization with configuration"""
        # Create logger instance
        logger = SQLBridgeLogger()
        
        # Should have config loaded
        assert hasattr(logger, 'config')
        assert logger.config is not None
    
    def test_get_logger(self):
        """Test getting a logger instance"""
        bridge_logger = SQLBridgeLogger()
        logger = bridge_logger.get_logger("test_module")
        
        assert logger.name == "test_module"
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
    
    def test_get_security_logger(self):
        """Test getting security logger"""
        bridge_logger = SQLBridgeLogger()
        security_logger = bridge_logger.get_security_logger()
        
        assert security_logger.name == "security"
    
    def test_get_performance_logger(self):
        """Test getting performance logger"""
        bridge_logger = SQLBridgeLogger()
        perf_logger = bridge_logger.get_performance_logger()
        
        assert perf_logger.name == "performance"

class TestLoggerConvenienceFunctions:
    """Test convenience functions for logging"""
    
    def test_get_logger_function(self):
        """Test get_logger convenience function"""
        logger = get_logger("test_module")
        
        assert logger.name == "test_module"
    
    def test_get_security_logger_function(self):
        """Test get_security_logger convenience function"""
        logger = get_security_logger()
        
        assert logger.name == "security"
    
    def test_get_performance_logger_function(self):
        """Test get_performance_logger convenience function"""
        logger = get_performance_logger()
        
        assert logger.name == "performance"

class TestLoggingFunctionality:
    """Test actual logging functionality"""
    
    def test_log_query_execution_success(self):
        """Test logging successful query execution"""
        # Test that the function can be called without errors
        try:
            log_query_execution(
                query="SELECT * FROM users",
                database="test_db",
                user_id="test_user",
                execution_time_ms=15.5,
                result_count=10,
                success=True
            )
            assert True  # Function executed without error
        except Exception:
            assert False, "log_query_execution should not raise exception"
    
    def test_log_query_execution_failure(self):
        """Test logging failed query execution"""
        # Test that the function can be called without errors
        try:
            log_query_execution(
                query="SELECT * FROM invalid_table",
                database="test_db",
                user_id="test_user",
                execution_time_ms=5.0,
                result_count=0,
                success=False,
                error_msg="Table does not exist"
            )
            assert True  # Function executed without error
        except Exception:
            assert False, "log_query_execution should not raise exception"
    
    def test_log_security_event(self):
        """Test logging security events"""
        # Test that the function can be called without errors
        try:
            log_security_event(
                event_type="blocked_query",
                severity="warning",
                message="Dangerous query blocked",
                user_id="suspicious_user",
                additional_data={"query": "DROP TABLE users"}
            )
            assert True  # Function executed without error
        except Exception:
            assert False, "log_security_event should not raise exception"

class TestLogEntryStructure:
    """Test log entry data structure"""
    
    def test_log_entry_creation(self):
        """Test LogEntry dataclass creation"""
        from utils.logger import LogEntry
        
        entry = LogEntry(
            timestamp="2023-01-01T12:00:00",
            level="INFO",
            logger_name="test",
            message="Test message",
            user_id="test_user",
            operation="test_operation"
        )
        
        assert entry.timestamp == "2023-01-01T12:00:00"
        assert entry.level == "INFO"
        assert entry.user_id == "test_user"
        assert entry.operation == "test_operation"

class TestSecurityAuditFilter:
    """Test security audit logging filter"""
    
    def test_security_audit_filter(self):
        """Test SecurityAuditFilter adds security context"""
        from utils.logger import SecurityAuditFilter
        import logging
        
        filter_instance = SecurityAuditFilter()
        
        # Create a mock log record
        record = logging.LogRecord(
            name="security",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Security event",
            args=(),
            exc_info=None
        )
        
        # Add security event flag
        record.security_event = True
        
        # Apply filter
        result = filter_instance.filter(record)
        
        assert result == True  # Should allow the record
        assert hasattr(record, 'audit_level')

class TestPerformanceFormatter:
    """Test performance logging formatter"""
    
    def test_performance_formatter_json_output(self):
        """Test PerformanceFormatter produces valid JSON"""
        from utils.logger import PerformanceFormatter
        import logging
        
        formatter = PerformanceFormatter()
        
        # Create a mock log record with extra context
        record = logging.LogRecord(
            name="performance",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Query executed",
            args=(),
            exc_info=None
        )
        
        # Add extra context
        record.user_id = "test_user"
        record.execution_time_ms = 15.5
        record.database = "test_db"
        
        # Format the record
        formatted = formatter.format(record)
        
        # Should be valid JSON
        try:
            log_data = json.loads(formatted)
            assert log_data["message"] == "Query executed"
            assert log_data["user_id"] == "test_user"
            assert log_data["execution_time_ms"] == 15.5
        except json.JSONDecodeError:
            pytest.fail("Formatted log should be valid JSON")