"""
Pytest configuration and shared fixtures for SQLBridgeMCP tests
"""
import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def event_loop():
    """Event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_database_connection():
    """Mock database connection"""
    mock_connection = AsyncMock()
    mock_connection.execute_query = AsyncMock(return_value=[{"id": 1, "name": "Test"}])
    mock_connection.get_table_names = AsyncMock(return_value=["users", "products"])
    mock_connection.check_health = AsyncMock(return_value={"status": "healthy"})
    return mock_connection

@pytest.fixture
def test_queries():
    """Test SQL queries"""
    return {
        "valid": ["SELECT * FROM users", "SELECT COUNT(*) FROM products"],
        "invalid": ["DELETE FROM users", "DROP TABLE products", "SELECT * FROM users; DROP TABLE users;--"]
    }