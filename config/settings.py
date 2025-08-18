"""
Database configuration settings manager
Loads and validates environment variables for database connections
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class DatabaseConfig:
    """
    Database configuration data class with validation
    
    Attributes:
        db_type: Type of database (postgresql, mysql, sqlite, sqlserver)
        connection_string: Full connection string (optional - takes priority)
        host: Database server hostname
        port: Database server port
        name: Database name
        user: Database username  
        password: Database password
        max_query_length: Maximum allowed SQL query length
        query_timeout: Query timeout in seconds
        max_rows_returned: Maximum rows returned per query
    """
    db_type: str
    connection_string: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    name: str = ""
    user: Optional[str] = None
    password: Optional[str] = None
    max_query_length: int = 10000
    query_timeout: int = 30
    max_rows_returned: int = 1000
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
    
    def _validate_config(self):
        """
        Validates database configuration parameters
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        # Validate database type
        valid_db_types = ["postgresql", "mysql", "sqlite", "sqlserver"]
        if self.db_type not in valid_db_types:
            raise ValueError(f"Invalid DB_TYPE. Must be one of: {valid_db_types}")
        
        # If connection_string is provided, use it (minimal validation)
        if self.connection_string:
            if len(self.connection_string.strip()) == 0:
                raise ValueError("CONNECTION_STRING cannot be empty")
            # Basic validation - should contain key connection elements
            conn_str = self.connection_string.lower()
            if self.db_type == "sqlserver" and "server=" not in conn_str:
                raise ValueError("CONNECTION_STRING for SQL Server should contain 'Server='")
            # Validate limits and return early
            self._validate_limits()
            return
        
        # SQLite only needs db_name (file path)
        if self.db_type == "sqlite":
            if not self.name:
                raise ValueError("DB_NAME (file path) is required for SQLite when not using CONNECTION_STRING")
            self._validate_limits()
            return
        
        # Other databases need host, name, user, password (when not using connection_string)
        required_fields = {
            "host": self.host,
            "name": self.name, 
            "user": self.user,
            "password": self.password
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            raise ValueError(f"Missing required database configuration (or provide CONNECTION_STRING): {missing_fields}")
        
        # Validate port ranges
        if self.port and not (1 <= self.port <= 65535):
            raise ValueError("Database port must be between 1 and 65535")
        
        self._validate_limits()
    
    def _validate_limits(self):
        """Validate query limits and timeouts"""
        if self.max_query_length <= 0:
            raise ValueError("MAX_QUERY_LENGTH must be positive")
        if self.query_timeout <= 0:
            raise ValueError("QUERY_TIMEOUT must be positive")
        if self.max_rows_returned <= 0:
            raise ValueError("MAX_ROWS_RETURNED must be positive")

    def get_connection_string(self) -> str:
        """
        Generates SQLAlchemy connection string for the database
        Priority: CONNECTION_STRING > individual components
        
        Returns:
            str: SQLAlchemy connection string
            
        Raises:
            ValueError: If database type is not supported
        """
        # Priority 1: Use CONNECTION_STRING if provided
        if self.connection_string:
            return self._adapt_connection_string_for_sqlalchemy()
        
        # Priority 2: Build from individual components
        if self.db_type == "postgresql":
            return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        
        elif self.db_type == "mysql":
            return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        
        elif self.db_type == "sqlite":
            return f"sqlite+aiosqlite:///{self.name}"
        
        elif self.db_type == "sqlserver":
            if self.port:
                return f"mssql+aioodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?driver=ODBC+Driver+17+for+SQL+Server"
            else:
                return f"mssql+aioodbc://{self.user}:{self.password}@{self.host}/{self.name}?driver=ODBC+Driver+17+for+SQL+Server"
        
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _adapt_connection_string_for_sqlalchemy(self) -> str:
        """
        Adapts native connection string to SQLAlchemy format
        
        Returns:
            str: SQLAlchemy compatible connection string
        """
        conn_str = self.connection_string
        
        if self.db_type == "sqlserver":
            # Convert native SQL Server connection string to SQLAlchemy format
            # Example: "Server=localhost;Database=mydb;User Id=user;Password=pass;TrustServerCertificate=true"
            # To: "mssql+aioodbc://user:pass@localhost/mydb?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
            
            # Extract components using simple parsing
            parts = {}
            for part in conn_str.split(';'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    parts[key.strip().lower()] = value.strip()
            
            server = parts.get('server', 'localhost')
            database = parts.get('database', '')
            user_id = parts.get('user id', parts.get('uid', ''))
            password = parts.get('password', parts.get('pwd', ''))
            trust_cert = parts.get('trustservercertificate', 'false').lower() == 'true'
            
            # Build SQLAlchemy connection string
            sqlalchemy_str = f"mssql+aioodbc://{user_id}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
            if trust_cert:
                sqlalchemy_str += "&TrustServerCertificate=yes"
            
            # Add any other parameters
            for key, value in parts.items():
                if key not in ['server', 'database', 'user id', 'uid', 'password', 'pwd', 'trustservercertificate']:
                    sqlalchemy_str += f"&{key}={value}"
            
            return sqlalchemy_str
        
        # For other database types, assume the connection string is already SQLAlchemy compatible
        return conn_str

def load_database_config() -> DatabaseConfig:
    """
    Loads database configuration from environment variables
    Priority: CONNECTION_STRING > individual DB_* variables
    
    Returns:
        DatabaseConfig: Validated database configuration
        
    Raises:
        ValueError: If configuration is invalid or missing
    """
    try:
        config = DatabaseConfig(
            db_type=os.getenv("DB_TYPE", "").lower(),
            connection_string=os.getenv("CONNECTION_STRING"),  # NEW: Primary option
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "0")) if os.getenv("DB_PORT") else None,
            name=os.getenv("DB_NAME", ""),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            max_query_length=int(os.getenv("MAX_QUERY_LENGTH", "10000")),
            query_timeout=int(os.getenv("QUERY_TIMEOUT", "30")),
            max_rows_returned=int(os.getenv("MAX_ROWS_RETURNED", "1000"))
        )
        return config
    
    except ValueError as e:
        raise ValueError(f"Database configuration error: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load database configuration: {e}")

@dataclass  
class MCPServerConfig:
    """
    MCP Server configuration data class
    
    Attributes:
        name: Server name
        version: Server version
        log_level: Logging level
        log_file: Log file path
    """
    name: str = "SQLBridgeMCP"
    version: str = "1.0.0"
    log_level: str = "INFO"
    log_file: str = "logs/sqlbridge.log"

def load_mcp_config() -> MCPServerConfig:
    """
    Loads MCP server configuration from environment variables
    
    Returns:
        MCPServerConfig: MCP server configuration
    """
    return MCPServerConfig(
        name=os.getenv("MCP_SERVER_NAME", "SQLBridgeMCP"),
        version=os.getenv("MCP_SERVER_VERSION", "1.0.0"), 
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        log_file=os.getenv("LOG_FILE", "logs/sqlbridge.log")
    )

# Global configuration instances (lazy loading)
_db_config: Optional[DatabaseConfig] = None
_mcp_config: Optional[MCPServerConfig] = None

def get_database_config() -> DatabaseConfig:
    """
    Gets the global database configuration instance (singleton pattern)
    
    Returns:
        DatabaseConfig: Database configuration
    """
    global _db_config
    if _db_config is None:
        _db_config = load_database_config()
    return _db_config

def get_mcp_config() -> MCPServerConfig:
    """
    Gets the global MCP server configuration instance (singleton pattern)
    
    Returns:
        MCPServerConfig: MCP server configuration
    """
    global _mcp_config
    if _mcp_config is None:
        _mcp_config = load_mcp_config()
    return _mcp_config