"""
Database operations module
Provides high-level database operations for MCP tools
"""
import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .connection import get_connection_manager, DatabaseError, DatabaseConnectionManager
from config.settings import get_database_config

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """
    Data class for SQL query results
    
    Attributes:
        success: Whether the query was successful
        data: Query result data
        row_count: Number of rows returned
        execution_time_ms: Query execution time in milliseconds
        error: Error message if query failed
        metadata: Additional metadata about the query
    """
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SQLOperations:
    """
    High-level SQL operations class for MCP tools
    Provides safe and validated database operations
    """
    
    def __init__(self):
        """Initialize SQL operations"""
        self._connection_manager: Optional[DatabaseConnectionManager] = None
        self._config = get_database_config()
    
    async def _get_connection_manager(self) -> DatabaseConnectionManager:
        """Get or initialize connection manager"""
        if self._connection_manager is None:
            self._connection_manager = await get_connection_manager()
        return self._connection_manager
    
    def _validate_query(self, query: str) -> None:
        """
        Validate SQL query for security and compliance
        
        Args:
            query: SQL query string to validate
            
        Raises:
            ValueError: If query is invalid or unsafe
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Check query length
        if len(query) > self._config.max_query_length:
            raise ValueError(f"Query exceeds maximum length of {self._config.max_query_length} characters")
        
        # Only allow SELECT queries for security
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed for security reasons")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'\bDELETE\b',
            r'\bUPDATE\b', 
            r'\bINSERT\b',
            r'\bDROP\b',
            r'\bCREATE\b',
            r'\bALTER\b',
            r'\bTRUNCATE\b',
            r'\bEXEC\b',
            r'\bEXECUTE\b',
            r'--',  # SQL comments
            r'/\*',  # SQL comments
            r'\bxp_\w+',  # SQL Server extended procedures
            r'\bsp_\w+',  # SQL Server stored procedures
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper):
                raise ValueError(f"Query contains potentially dangerous pattern: {pattern}")
        
        # Basic SQL injection prevention
        suspicious_patterns = [
            r"'[^']*'[^']*'",  # Multiple single quotes
            r';\s*\w+',  # Semicolon followed by commands
            r'\bunion\s+select\b',  # UNION SELECT attacks
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query_upper):
                raise ValueError(f"Query contains suspicious pattern that may indicate SQL injection")
        
        logger.debug(f"Query validation passed: {query[:100]}...")
    
    async def execute_query(self, query: str, database: str = "default") -> QueryResult:
        """
        Execute a SQL query safely with validation and error handling
        
        Args:
            query: SQL SELECT query to execute
            database: Database identifier (for logging/metadata)
            
        Returns:
            QueryResult: Result object containing query results and metadata
        """
        import time
        start_time = time.time()
        
        try:
            # Validate query first
            self._validate_query(query)
            
            # Get connection manager
            connection_manager = await self._get_connection_manager()
            
            # Execute query
            logger.info(f"Executing query on database '{database}': {query[:100]}...")
            results = await connection_manager.execute_query(query)
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000
            
            # Limit results to prevent memory issues
            limited_results = results[:self._config.max_rows_returned]
            was_limited = len(results) > self._config.max_rows_returned
            
            logger.info(f"Query executed successfully. Returned {len(limited_results)} rows in {execution_time:.2f}ms")
            
            return QueryResult(
                success=True,
                data=limited_results,
                row_count=len(limited_results),
                execution_time_ms=round(execution_time, 2),
                metadata={
                    "database": database,
                    "query_hash": hash(query),
                    "was_limited": was_limited,
                    "total_rows_found": len(results),
                    "max_rows_returned": self._config.max_rows_returned
                }
            )
            
        except ValueError as e:
            # Validation error
            logger.warning(f"Query validation failed: {e}")
            return QueryResult(
                success=False,
                error=f"Query validation failed: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            
        except DatabaseError as e:
            # Database connection/execution error
            logger.error(f"Database error during query execution: {e}")
            return QueryResult(
                success=False,
                error=f"Database error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error during query execution: {e}")
            return QueryResult(
                success=False,
                error=f"Unexpected error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
    
    async def list_tables(self, database: str = "default") -> QueryResult:
        """
        List all available tables in the database
        
        Args:
            database: Database identifier (for logging/metadata)
            
        Returns:
            QueryResult: Result object containing list of table names
        """
        import time
        start_time = time.time()
        
        try:
            connection_manager = await self._get_connection_manager()
            
            logger.info(f"Listing tables for database '{database}'")
            table_names = await connection_manager.get_table_names()
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"Found {len(table_names)} tables in {execution_time:.2f}ms")
            
            return QueryResult(
                success=True,
                data=[{"table_name": name} for name in table_names],
                row_count=len(table_names),
                execution_time_ms=round(execution_time, 2),
                metadata={
                    "database": database,
                    "operation": "list_tables",
                    "table_count": len(table_names)
                }
            )
            
        except DatabaseError as e:
            logger.error(f"Database error while listing tables: {e}")
            return QueryResult(
                success=False,
                error=f"Database error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error while listing tables: {e}")
            return QueryResult(
                success=False,
                error=f"Unexpected error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
    
    async def list_tables_from_database(self, target_database: str) -> QueryResult:
        """
        List all available tables from a specific database
        
        Args:
            target_database: Name of the database to query
            
        Returns:
            QueryResult: Result object containing list of table names
        """
        import time
        start_time = time.time()
        
        try:
            # Validate database name to prevent injection
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', target_database):
                raise ValueError("Invalid database name format")
            
            connection_manager = await self._get_connection_manager()
            
            logger.info(f"Listing tables from specific database '{target_database}'")
            
            # Use a query that works across different databases
            if self._config.db_type == "sqlserver":
                query = f"""
                SELECT TABLE_NAME 
                FROM {target_database}.INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
                """
            elif self._config.db_type == "postgresql":
                query = f"""
                SELECT tablename as TABLE_NAME
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tableowner != 'postgres'
                ORDER BY tablename
                """
            elif self._config.db_type == "mysql":
                query = f"SHOW TABLES FROM {target_database}"
            else:
                raise ValueError(f"Database switching not supported for {self._config.db_type}")
            
            results = await connection_manager.execute_query(query)
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"Found {len(results)} tables in database '{target_database}' in {execution_time:.2f}ms")
            
            return QueryResult(
                success=True,
                data=results,
                row_count=len(results),
                execution_time_ms=round(execution_time, 2),
                metadata={
                    "database": target_database,
                    "operation": "list_tables_from_database",
                    "table_count": len(results)
                }
            )
            
        except ValueError as e:
            logger.warning(f"Database listing validation failed: {e}")
            return QueryResult(
                success=False,
                error=f"Validation error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            
        except DatabaseError as e:
            logger.error(f"Database error while listing tables from '{target_database}': {e}")
            return QueryResult(
                success=False,
                error=f"Database error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error while listing tables from '{target_database}': {e}")
            return QueryResult(
                success=False,
                error=f"Unexpected error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
    
    async def list_all_databases(self) -> QueryResult:
        """
        List all available databases in the SQL Server instance
        
        Returns:
            QueryResult: Result object containing list of database names
        """
        import time
        start_time = time.time()
        
        try:
            connection_manager = await self._get_connection_manager()
            
            logger.info("Listing all available databases")
            
            # Query to get all databases
            if self._config.db_type == "sqlserver":
                query = "SELECT name as database_name FROM sys.databases WHERE database_id > 4 ORDER BY name"
            elif self._config.db_type == "postgresql":
                query = "SELECT datname as database_name FROM pg_database WHERE datistemplate = false ORDER BY datname"
            elif self._config.db_type == "mysql":
                query = "SHOW DATABASES"
            else:
                raise ValueError(f"Database listing not supported for {self._config.db_type}")
            
            results = await connection_manager.execute_query(query)
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"Found {len(results)} databases in {execution_time:.2f}ms")
            
            return QueryResult(
                success=True,
                data=results,
                row_count=len(results),
                execution_time_ms=round(execution_time, 2),
                metadata={
                    "operation": "list_all_databases",
                    "database_count": len(results)
                }
            )
            
        except DatabaseError as e:
            logger.error(f"Database error while listing databases: {e}")
            return QueryResult(
                success=False,
                error=f"Database error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error while listing databases: {e}")
            return QueryResult(
                success=False,
                error=f"Unexpected error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
    
    async def describe_table(self, table_name: str, include_sample_data: bool = False) -> QueryResult:
        """
        Get schema information for a specific table
        
        Args:
            table_name: Name of the table to describe
            include_sample_data: Whether to include sample data from the table
            
        Returns:
            QueryResult: Result object containing table schema and optionally sample data
        """
        import time
        start_time = time.time()
        
        try:
            if not table_name or not table_name.strip():
                raise ValueError("Table name is required")
            
            # Validate table name to prevent injection
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
                raise ValueError("Invalid table name format")
            
            connection_manager = await self._get_connection_manager()
            
            logger.info(f"Describing table '{table_name}' (include_sample_data: {include_sample_data})")
            
            # Get table schema
            schema = await connection_manager.get_table_schema(table_name)
            
            result_data = {
                "table_name": table_name,
                "schema": schema,
                "column_count": len(schema)
            }
            
            # Get sample data if requested
            if include_sample_data:
                try:
                    # Limit sample data to 5 rows for performance
                    sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                    sample_results = await connection_manager.execute_query(sample_query)
                    result_data["sample_data"] = sample_results[:5]  # Extra safety
                except Exception as e:
                    logger.warning(f"Failed to get sample data for table {table_name}: {e}")
                    result_data["sample_data_error"] = str(e)
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"Table description completed in {execution_time:.2f}ms")
            
            return QueryResult(
                success=True,
                data=[result_data],
                row_count=1,
                execution_time_ms=round(execution_time, 2),
                metadata={
                    "operation": "describe_table",
                    "table_name": table_name,
                    "include_sample_data": include_sample_data,
                    "column_count": len(schema)
                }
            )
            
        except ValueError as e:
            logger.warning(f"Table description validation failed: {e}")
            return QueryResult(
                success=False,
                error=f"Validation error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            
        except DatabaseError as e:
            logger.error(f"Database error while describing table: {e}")
            return QueryResult(
                success=False,
                error=f"Database error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error while describing table: {e}")
            return QueryResult(
                success=False,
                error=f"Unexpected error: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
    
    async def check_database_health(self) -> QueryResult:
        """
        Check database connection health and return status
        
        Returns:
            QueryResult: Result object containing health status information
        """
        import time
        start_time = time.time()
        
        try:
            connection_manager = await self._get_connection_manager()
            
            logger.info("Checking database health")
            health_info = await connection_manager.check_health()
            
            execution_time = (time.time() - start_time) * 1000
            
            is_healthy = health_info.get("status") == "healthy"
            
            logger.info(f"Database health check completed: {health_info.get('status', 'unknown')}")
            
            return QueryResult(
                success=True,
                data=[health_info],
                row_count=1,
                execution_time_ms=round(execution_time, 2),
                metadata={
                    "operation": "health_check",
                    "is_healthy": is_healthy
                }
            )
            
        except Exception as e:
            logger.error(f"Error during database health check: {e}")
            return QueryResult(
                success=False,
                error=f"Health check failed: {e}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2),
                data=[{
                    "status": "unhealthy",
                    "error": str(e)
                }]
            )

# Global SQL operations instance
_sql_operations: Optional[SQLOperations] = None

def get_sql_operations() -> SQLOperations:
    """
    Get the global SQL operations instance (singleton pattern)
    
    Returns:
        SQLOperations: SQL operations instance
    """
    global _sql_operations
    if _sql_operations is None:
        _sql_operations = SQLOperations()
    return _sql_operations