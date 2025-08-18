"""
Database connection manager
Handles database connections using SQLAlchemy with async support
"""
import asyncio
from typing import Optional, AsyncContextManager
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import text
import logging

from config.settings import get_database_config, DatabaseConfig

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """
    Manages database connections using SQLAlchemy async engine
    Implements singleton pattern for connection pooling
    """
    
    _instance: Optional['DatabaseConnectionManager'] = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker] = None
    
    def __new__(cls) -> 'DatabaseConnectionManager':
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection manager"""
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._config: Optional[DatabaseConfig] = None
    
    async def initialize(self) -> None:
        """
        Initialize database connection and engine
        
        Raises:
            DatabaseError: If connection initialization fails
        """
        try:
            # Load database configuration
            self._config = get_database_config()
            
            # Log configuration method being used
            if self._config.connection_string:
                logger.info(f"Initializing database connection for {self._config.db_type} using CONNECTION_STRING")
            else:
                logger.info(f"Initializing database connection for {self._config.db_type} using individual variables")
            
            # Create async engine with connection pooling
            connection_string = self._config.get_connection_string()
            
            # Engine configuration for different database types
            engine_kwargs = {
                "echo": False,  # Set to True for SQL query logging
                "pool_pre_ping": True,  # Verify connections before use
                "pool_recycle": 3600,   # Recycle connections every hour
            }
            
            # Database-specific configurations
            if self._config.db_type == "sqlite":
                engine_kwargs.update({
                    "pool_size": 1,
                    "max_overflow": 0,
                    "connect_args": {"check_same_thread": False}
                })
            else:
                engine_kwargs.update({
                    "pool_size": 5,
                    "max_overflow": 10
                })
            
            self._engine = create_async_engine(connection_string, **engine_kwargs)
            
            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            await self._test_connection()
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    async def _test_connection(self) -> None:
        """
        Test database connection with a simple query
        
        Raises:
            DatabaseError: If connection test fails
        """
        if not self._engine:
            raise DatabaseError("Database engine not initialized")
        
        try:
            async with self._engine.begin() as conn:
                # Simple test query for different database types
                if self._config.db_type == "postgresql":
                    result = await conn.execute(text("SELECT version()"))
                elif self._config.db_type == "mysql":
                    result = await conn.execute(text("SELECT version()"))
                elif self._config.db_type == "sqlite":
                    result = await conn.execute(text("SELECT sqlite_version()"))
                elif self._config.db_type == "sqlserver":
                    result = await conn.execute(text("SELECT @@version"))
                else:
                    result = await conn.execute(text("SELECT 1"))
                
                row = result.fetchone()
                logger.debug(f"Database connection test successful: {row}")
                
        except OperationalError as e:
            raise DatabaseError(f"Database connection test failed: {e}")
        except Exception as e:
            raise DatabaseError(f"Unexpected error during connection test: {e}")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncContextManager[AsyncSession]:
        """
        Get database session with automatic transaction management
        
        Yields:
            AsyncSession: SQLAlchemy async session
            
        Raises:
            DatabaseError: If session creation fails
        """
        if not self._session_factory:
            raise DatabaseError("Database connection not initialized. Call initialize() first.")
        
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def execute_query(self, query: str, params: Optional[dict] = None) -> list:
        """
        Execute a raw SQL query safely
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            list: Query results as list of dictionaries
            
        Raises:
            DatabaseError: If query execution fails
        """
        if not self._engine:
            raise DatabaseError("Database connection not initialized")
        
        try:
            async with self._engine.begin() as conn:
                # Execute query with timeout
                result = await asyncio.wait_for(
                    conn.execute(text(query), params or {}),
                    timeout=self._config.query_timeout
                )
                
                # Convert result to list of dictionaries
                rows = result.fetchall()
                columns = result.keys()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except asyncio.TimeoutError:
            raise DatabaseError(f"Query execution timed out after {self._config.query_timeout} seconds")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database query failed: {e}")
        except Exception as e:
            raise DatabaseError(f"Unexpected error during query execution: {e}")
    
    async def get_table_names(self) -> list[str]:
        """
        Get list of all table names in the database
        
        Returns:
            list[str]: List of table names
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            if self._config.db_type == "postgresql":
                query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
                """
            elif self._config.db_type == "mysql":
                query = "SHOW TABLES"
            elif self._config.db_type == "sqlite":
                query = """
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            elif self._config.db_type == "sqlserver":
                query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            else:
                raise DatabaseError(f"Unsupported database type: {self._config.db_type}")
            
            results = await self.execute_query(query)
            
            # Extract table names from results (different column names per DB type)
            if self._config.db_type == "mysql":
                table_key = list(results[0].keys())[0] if results else None
                return [row[table_key] for row in results] if table_key else []
            elif self._config.db_type in ["postgresql", "sqlserver"]:
                return [row["table_name"] for row in results]
            elif self._config.db_type == "sqlite":
                return [row["name"] for row in results]
            else:
                return []
                
        except Exception as e:
            raise DatabaseError(f"Failed to get table names: {e}")
    
    async def get_table_schema(self, table_name: str) -> list[dict]:
        """
        Get schema information for a specific table
        
        Args:
            table_name: Name of the table
            
        Returns:
            list[dict]: List of column information dictionaries
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            if self._config.db_type == "postgresql":
                query = """
                SELECT column_name, data_type, is_nullable, column_default,
                       CASE WHEN column_name IN (
                           SELECT column_name FROM information_schema.key_column_usage 
                           WHERE table_name = :table_name AND constraint_name LIKE '%_pkey'
                       ) THEN true ELSE false END as is_primary_key
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                ORDER BY ordinal_position
                """
            elif self._config.db_type == "sqlite":
                query = f"PRAGMA table_info({table_name})"
            else:
                # Simplified schema for other databases
                query = """
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                ORDER BY ordinal_position
                """
            
            if self._config.db_type == "sqlite":
                results = await self.execute_query(query)
                # Transform SQLite PRAGMA results to standard format
                return [
                    {
                        "column_name": row["name"],
                        "data_type": row["type"],
                        "is_nullable": "YES" if row["notnull"] == 0 else "NO",
                        "is_primary_key": bool(row["pk"])
                    }
                    for row in results
                ]
            else:
                results = await self.execute_query(query, {"table_name": table_name})
                return results
                
        except Exception as e:
            raise DatabaseError(f"Failed to get table schema for {table_name}: {e}")
    
    async def check_health(self) -> dict:
        """
        Check database connection health and return status information
        
        Returns:
            dict: Health status information
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Test simple query
            await self.execute_query("SELECT 1 as health_check")
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "database_type": self._config.db_type,
                "response_time_ms": round(response_time, 2),
                "connection_pool_size": self._engine.pool.size() if self._engine else 0,
                "checked_out_connections": self._engine.pool.checkedout() if self._engine else 0
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_type": self._config.db_type if self._config else "unknown"
            }
    
    async def close(self) -> None:
        """Close database connections and cleanup resources"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connections closed")

class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass

# Global connection manager instance
_connection_manager: Optional[DatabaseConnectionManager] = None

async def get_connection_manager() -> DatabaseConnectionManager:
    """
    Get the global database connection manager instance
    
    Returns:
        DatabaseConnectionManager: Connection manager instance
    """
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = DatabaseConnectionManager()
        await _connection_manager.initialize()
    return _connection_manager

async def close_database_connections():
    """Close all database connections"""
    global _connection_manager
    if _connection_manager:
        await _connection_manager.close()
        _connection_manager = None