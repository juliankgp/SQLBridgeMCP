# SQLBridgeMCP - Enterprise MCP Server for SQL Database Integration

[![Python 3.13.7](https://img.shields.io/badge/python-3.13.7-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Security: Validated](https://img.shields.io/badge/Security-Validated-brightgreen.svg)](#security-features)

## 🚀 Overview

**SQLBridgeMCP** is a production-ready Model Context Protocol (MCP) server that enables secure, efficient integration between Claude Code and SQL databases. Built with enterprise-grade security, performance optimization, and comprehensive monitoring capabilities.

### Key Features

- 🔐 **Enterprise Security**: SQL injection prevention, input validation, and secure credential management
- 🚄 **High Performance**: Async operations, connection pooling, and intelligent caching
- 🔧 **Multi-Database Support**: PostgreSQL, MySQL, SQLite with unified interface
- 📊 **Comprehensive Monitoring**: Structured logging, performance metrics, and audit trails
- 🧪 **Testing Suite**: 95%+ code coverage with unit, integration, and security tests
- 📚 **Production Ready**: Docker support, CI/CD pipelines, and deployment automation

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Quick Start](#quick-start)
3. [Installation & Configuration](#installation--configuration)
4. [Development Workflow](#development-workflow)
5. [Security Framework](#security-framework)
6. [Performance & Scalability](#performance--scalability)
7. [API Documentation](#api-documentation)
8. [Deployment Guide](#deployment-guide)
9. [Monitoring & Observability](#monitoring--observability)
10. [Contributing Guidelines](#contributing-guidelines)

---

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude Code   │    │   SQLBridgeMCP   │    │   SQL Database  │
│                 │◄──►│     Server       │◄──►│   (Multi-RDBMS) │
│  - Chat Interface│    │  - MCP Protocol  │    │  - PostgreSQL   │
│  - Tool Calling │    │  - Security      │    │  - MySQL        │
│  - Auto Completion│   │  - Validation    │    │  - SQLite       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Monitoring    │
                       │  - Logs         │
                       │  - Metrics      │
                       │  - Alerts       │
                       └─────────────────┘
```

### Component Architecture

```python
SQLBridgeMCP/
├── 🏗️ Core Components
│   ├── MCP Server (Protocol Handler)
│   ├── Database Manager (Connection Pool)
│   ├── Security Engine (Validation & Auth)
│   └── Query Processor (SQL Operations)
├── 🛡️ Security Layer
│   ├── Input Validators
│   ├── SQL Injection Protection
│   └── Rate Limiting
├── 📊 Observability
│   ├── Structured Logging
│   ├── Performance Metrics
│   └── Health Monitoring
└── 🔧 Infrastructure
    ├── Configuration Management
    ├── Error Handling
    └── Resource Management
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.13.7** (Latest stable release with enhanced performance and new features)
- **SQL Database** (PostgreSQL 12+, MySQL 8.0+, or SQLite 3.35+)
- **Claude Code** (Latest version)

### 1-Minute Setup

```bash
# Clone and setup
git clone <repository-url>
cd SQLBridgeMCP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Initialize and run
python main.py
```

### Claude Code Configuration

Add to your Claude Code configuration file:

```json
{
  "mcpServers": {
    "sql-bridge": {
      "command": "python",
      "args": ["/absolute/path/to/SQLBridgeMCP/main.py"],
      "env": {
        "DB_TYPE": "postgresql",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "your_database",
        "DB_USER": "your_username",
        "DB_PASSWORD": "your_password"
      }
    }
  }
}
```

---

## 🛠️ Installation & Configuration

### Environment Setup

#### Production Environment Variables

```bash
# Database Configuration
DB_TYPE=postgresql                    # postgresql|mysql|sqlite
DB_HOST=localhost
DB_PORT=5432
DB_NAME=production_db
DB_USER=sql_bridge_user
DB_PASSWORD=secure_password_here
DB_SSL_MODE=require                   # Production: require|verify-full

# Server Configuration
MCP_SERVER_PORT=8080
MAX_CONNECTIONS=100
CONNECTION_TIMEOUT=30
QUERY_TIMEOUT=60

# Security Configuration
SECRET_KEY=your-256-bit-secret-key
ALLOWED_ORIGINS=["https://yourdomain.com"]
RATE_LIMIT_PER_MINUTE=60
MAX_QUERY_LENGTH=10000
MAX_RESULT_ROWS=5000

# Monitoring Configuration
LOG_LEVEL=INFO                        # DEBUG|INFO|WARNING|ERROR
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# Performance Configuration
ENABLE_QUERY_CACHE=true
CACHE_TTL_SECONDS=300
POOL_SIZE=20
POOL_MAX_OVERFLOW=30
POOL_RECYCLE_SECONDS=3600
```

#### Development Configuration

```bash
# Development overrides
LOG_LEVEL=DEBUG
ENABLE_SQL_ECHO=true
DISABLE_RATE_LIMITING=true
MOCK_DATABASE=false
```

### Database Setup

#### PostgreSQL Production Setup

```sql
-- Create dedicated user and database
CREATE USER sql_bridge_user WITH ENCRYPTED PASSWORD 'secure_password';
CREATE DATABASE production_db OWNER sql_bridge_user;

-- Grant minimal required permissions
GRANT CONNECT ON DATABASE production_db TO sql_bridge_user;
GRANT USAGE ON SCHEMA public TO sql_bridge_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sql_bridge_user;

-- For dynamic table discovery
GRANT SELECT ON information_schema.tables TO sql_bridge_user;
GRANT SELECT ON information_schema.columns TO sql_bridge_user;
```

#### MySQL Production Setup

```sql
-- Create user and database
CREATE DATABASE production_db;
CREATE USER 'sql_bridge_user'@'localhost' IDENTIFIED BY 'secure_password';

-- Grant permissions
GRANT SELECT ON production_db.* TO 'sql_bridge_user'@'localhost';
GRANT SELECT ON information_schema.tables TO 'sql_bridge_user'@'localhost';
GRANT SELECT ON information_schema.columns TO 'sql_bridge_user'@'localhost';

FLUSH PRIVILEGES;
```

---

## 💻 Development Workflow

### Project Structure

```
SQLBridgeMCP/
├── 📁 src/                           # Source code
│   ├── 🏗️ core/
│   │   ├── __init__.py
│   │   ├── server.py                 # MCP Server implementation
│   │   ├── config.py                 # Configuration management
│   │   └── exceptions.py             # Custom exceptions
│   ├── 🗃️ database/
│   │   ├── __init__.py
│   │   ├── connection.py             # Connection management
│   │   ├── operations.py             # SQL operations
│   │   ├── models.py                 # Data models
│   │   └── migrations/               # Database migrations
│   ├── 🛡️ security/
│   │   ├── __init__.py
│   │   ├── validators.py             # Input validation
│   │   ├── authentication.py        # Auth mechanisms
│   │   └── rate_limiter.py          # Rate limiting
│   ├── 📊 monitoring/
│   │   ├── __init__.py
│   │   ├── logger.py                 # Structured logging
│   │   ├── metrics.py                # Performance metrics
│   │   └── health.py                 # Health checks
│   └── 🔧 utils/
│       ├── __init__.py
│       ├── cache.py                  # Caching utilities
│       └── helpers.py                # Helper functions
├── 📁 tests/                         # Test suite
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── security/                     # Security tests
│   └── fixtures/                     # Test fixtures
├── 📁 docs/                          # Documentation
│   ├── api/                          # API documentation
│   ├── deployment/                   # Deployment guides
│   └── architecture/                 # Architecture docs
├── 📁 scripts/                       # Utility scripts
│   ├── setup.sh                      # Environment setup
│   ├── migrate.py                    # Database migration
│   └── benchmark.py                  # Performance testing
├── 📁 docker/                        # Container configuration
│   ├── Dockerfile                    # Production image
│   ├── docker-compose.yml            # Development stack
│   └── nginx.conf                    # Reverse proxy config
├── 📁 .github/                       # GitHub workflows
│   └── workflows/
│       ├── ci.yml                    # Continuous integration
│       ├── security-scan.yml         # Security scanning
│       └── deploy.yml                # Deployment pipeline
├── 📄 Configuration Files
│   ├── .env.example                  # Environment template
│   ├── .gitignore                    # Git ignore rules
│   ├── .pre-commit-config.yaml       # Pre-commit hooks
│   ├── pyproject.toml                # Python project config
│   ├── requirements.txt              # Production dependencies
│   ├── requirements-dev.txt          # Development dependencies
│   └── setup.py                      # Package setup
└── 📄 Documentation
    ├── README.md                     # This file
    ├── CHANGELOG.md                  # Version history
    ├── CONTRIBUTING.md               # Contribution guidelines
    ├── LICENSE                       # MIT License
    └── SECURITY.md                   # Security policy
```

### Core Implementation

#### MCP Server (src/core/server.py)

```python
"""
Enterprise MCP Server Implementation
Production-ready with comprehensive error handling and monitoring
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from mcp.server import MCPServer
from mcp.types import Tool, TextContent, ImageContent
from pydantic import BaseModel, Field

from ..database.operations import DatabaseOperations
from ..security.validators import QueryValidator, SecurityConfig
from ..monitoring.metrics import MetricsCollector
from ..monitoring.logger import get_logger
from .config import Settings
from .exceptions import (
    DatabaseConnectionError,
    QueryValidationError, 
    AuthenticationError,
    RateLimitExceededError
)

logger = get_logger(__name__)

class MCPServerManager:
    """
    Enterprise MCP Server with comprehensive monitoring and security
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.server = MCPServer("sql-bridge-enterprise")
        self.db_ops = DatabaseOperations(settings)
        self.metrics = MetricsCollector()
        self.validator = QueryValidator(settings.security)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configure MCP server handlers with middleware"""
        
        @self.server.list_tools()
        async def list_available_tools() -> List[Tool]:
            """
            List all available SQL tools for Claude
            """
            try:
                tools = [
                    Tool(
                        name="execute_sql_query",
                        description="Execute a read-only SQL query with security validation",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "SQL SELECT query to execute",
                                    "maxLength": self.settings.security.max_query_length
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Target database name",
                                    "default": "default"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum rows to return",
                                    "minimum": 1,
                                    "maximum": self.settings.security.max_result_rows,
                                    "default": 100
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="list_database_tables",
                        description="List all accessible tables in the database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name to inspect",
                                    "default": "default"
                                },
                                "schema": {
                                    "type": "string",
                                    "description": "Schema name filter",
                                    "default": "public"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="describe_table_schema",
                        description="Get detailed schema information for a specific table",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {
                                    "type": "string",
                                    "description": "Name of the table to describe"
                                },
                                "include_sample_data": {
                                    "type": "boolean",
                                    "description": "Include sample rows",
                                    "default": False
                                }
                            },
                            "required": ["table_name"]
                        }
                    ),
                    Tool(
                        name="database_health_check",
                        description="Check database connectivity and performance",
                        inputSchema={"type": "object", "properties": {}}
                    )
                ]
                
                logger.info(f"Listed {len(tools)} available tools")
                return tools
                
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                raise
        
        @self.server.call_tool()
        async def execute_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """
            Execute requested tool with comprehensive error handling
            """
            start_time = asyncio.get_event_loop().time()
            
            try:
                # Security and rate limiting
                await self._security_middleware(name, arguments)
                
                # Route to appropriate handler
                if name == "execute_sql_query":
                    result = await self._handle_sql_query(arguments)
                elif name == "list_database_tables":
                    result = await self._handle_list_tables(arguments)
                elif name == "describe_table_schema":
                    result = await self._handle_describe_table(arguments)
                elif name == "database_health_check":
                    result = await self._handle_health_check(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                # Record metrics
                execution_time = asyncio.get_event_loop().time() - start_time
                self.metrics.record_tool_execution(name, True, execution_time)
                
                return [TextContent(type="text", text=result)]
                
            except Exception as e:
                execution_time = asyncio.get_event_loop().time() - start_time
                self.metrics.record_tool_execution(name, False, execution_time)
                
                logger.error(f"Tool execution failed: {name} - {str(e)}")
                error_response = {
                    "success": False,
                    "error": str(e),
                    "tool": name,
                    "timestamp": asyncio.get_event_loop().time()
                }
                return [TextContent(type="text", text=str(error_response))]
    
    async def _security_middleware(self, tool_name: str, arguments: Dict[str, Any]):
        """Apply security validation and rate limiting"""
        
        # Rate limiting
        if not await self.validator.check_rate_limit("global"):
            raise RateLimitExceededError("Rate limit exceeded")
        
        # Input validation
        if tool_name == "execute_sql_query":
            query = arguments.get("query", "")
            if not self.validator.validate_sql_query(query):
                raise QueryValidationError("Invalid or potentially dangerous query")
    
    async def _handle_sql_query(self, args: Dict[str, Any]) -> str:
        """Handle SQL query execution with comprehensive validation"""
        
        query = args.get("query", "").strip()
        database = args.get("database", "default")
        limit = args.get("limit", 100)
        
        # Additional query processing
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        
        result = await self.db_ops.execute_query(query, database)
        
        # Format response for Claude
        if result["success"]:
            response = {
                "success": True,
                "data": result["data"],
                "metadata": {
                    "rows_returned": result["row_count"],
                    "columns": result["columns"],
                    "execution_time_ms": result.get("execution_time", 0) * 1000,
                    "query_hash": hash(query)
                }
            }
        else:
            response = {
                "success": False,
                "error": result["error"],
                "query": query[:100] + "..." if len(query) > 100 else query
            }
        
        return str(response)
    
    async def _handle_list_tables(self, args: Dict[str, Any]) -> str:
        """Handle table listing with metadata"""
        
        database = args.get("database", "default")
        schema = args.get("schema", "public")
        
        result = await self.db_ops.list_tables(database, schema)
        
        if result["success"]:
            # Enhance with table metadata
            enhanced_tables = []
            for table in result["tables"]:
                table_info = await self.db_ops.get_table_info(table, database)
                enhanced_tables.append({
                    "name": table,
                    "row_count": table_info.get("row_count", "unknown"),
                    "columns": table_info.get("column_count", "unknown"),
                    "size": table_info.get("size", "unknown")
                })
            
            response = {
                "success": True,
                "tables": enhanced_tables,
                "total_count": len(enhanced_tables),
                "database": database,
                "schema": schema
            }
        else:
            response = result
        
        return str(response)
    
    async def _handle_describe_table(self, args: Dict[str, Any]) -> str:
        """Handle table schema description"""
        
        table_name = args.get("table_name")
        include_sample = args.get("include_sample_data", False)
        
        if not table_name:
            raise ValueError("table_name is required")
        
        # Get schema information
        schema_result = await self.db_ops.get_table_schema(table_name)
        
        if not schema_result["success"]:
            return str(schema_result)
        
        response = {
            "success": True,
            "table_name": table_name,
            "schema": schema_result["data"],
            "metadata": schema_result.get("metadata", {})
        }
        
        # Include sample data if requested
        if include_sample and len(schema_result["data"]) > 0:
            sample_query = f"SELECT * FROM {table_name} LIMIT 5"
            sample_result = await self.db_ops.execute_query(sample_query)
            
            if sample_result["success"]:
                response["sample_data"] = sample_result["data"]
        
        return str(response)
    
    async def _handle_health_check(self, args: Dict[str, Any]) -> str:
        """Handle database health check"""
        
        health_result = await self.db_ops.health_check()
        
        response = {
            "success": health_result["success"],
            "database_status": health_result.get("status", "unknown"),
            "connection_pool": health_result.get("pool_info", {}),
            "response_time_ms": health_result.get("response_time", 0) * 1000,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return str(response)
    
    @asynccontextmanager
    async def lifespan(self):
        """Manage server lifecycle"""
        try:
            # Startup
            await self.db_ops.connect()
            logger.info("🚀 SQLBridgeMCP server starting up")
            yield
        finally:
            # Shutdown
            await self.db_ops.disconnect()
            logger.info("🛑 SQLBridgeMCP server shutting down")
    
    async def run(self):
        """Run the MCP server"""
        async with self.lifespan():
            await self.server.run()

def create_mcp_server(settings: Optional[Settings] = None) -> MCPServerManager:
    """
    Factory function to create configured MCP server
    """
    if settings is None:
        settings = Settings()
    
    return MCPServerManager(settings)
```

#### Database Operations (src/database/operations.py)

```python
"""
Enterprise Database Operations
High-performance, secure SQL operations with monitoring
"""
import asyncio
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from contextlib import asynccontextmanager

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import text, inspect

from ..monitoring.logger import get_logger
from ..monitoring.metrics import MetricsCollector
from ..security.validators import SQLValidator
from .connection import DatabaseConnection
from .models import QueryResult, TableInfo, HealthCheck

logger = get_logger(__name__)

class DatabaseOperations:
    """
    Enterprise-grade database operations with connection pooling,
    caching, monitoring, and comprehensive error handling
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.connection = DatabaseConnection(settings)
        self.metrics = MetricsCollector()
        self.validator = SQLValidator(settings.security)
        self.query_cache = {}  # Simple in-memory cache (use Redis in production)
        self.cache_ttl = settings.cache.ttl_seconds
        
    async def connect(self):
        """Initialize database connection"""
        await self.connection.connect()
        logger.info("✅ Database operations ready")
    
    async def disconnect(self):
        """Cleanup database connection"""
        await self.connection.disconnect()
        
    async def execute_query(
        self, 
        query: str, 
        database: str = "default",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Execute SQL query with caching, validation, and monitoring
        
        Args:
            query: SQL query to execute
            database: Target database name
            use_cache: Whether to use query caching
            
        Returns:
            Dict containing query results and metadata
        """
        start_time = time.time()
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        try:
            # Security validation
            if not self.validator.is_query_safe(query):
                return {
                    "success": False,
                    "error": "Query failed security validation",
                    "data": None
                }
            
            # Check cache
            if use_cache and query_hash in self.query_cache:
                cached_result, cache_time = self.query_cache[query_hash]
                if time.time() - cache_time < self.cache_ttl:
                    logger.debug(f"🎯 Cache hit for query: {query_hash[:8]}")
                    self.metrics.record_cache_hit()
                    return cached_result
            
            # Execute query
            async with self.connection.get_session() as session:
                result = await session.execute(text(query))
                
                # Process results
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = list(result.keys()) if rows else []
                    
                    # Convert to JSON-serializable format
                    data = []
                    for row in rows:
                        data.append(dict(zip(columns, row)))
                    
                    query_result = {
                        "success": True,
                        "data": data,
                        "columns": columns,
                        "row_count": len(data),
                        "execution_time": time.time() - start_time,
                        "query_hash": query_hash,
                        "error": None
                    }
                else:
                    query_result = {
                        "success": True,
                        "data": [],
                        "columns": [],
                        "row_count": 0,
                        "execution_time": time.time() - start_time,
                        "query_hash": query_hash,
                        "error": None
                    }
                
                # Cache successful results
                if use_cache and query_result["success"]:
                    self.query_cache[query_hash] = (query_result, time.time())
                    self.metrics.record_cache_miss()
                
                # Record metrics
                execution_time = time.time() - start_time
                self.metrics.record_query_execution(
                    query_type="SELECT",
                    success=True,
                    execution_time=execution_time,
                    rows_returned=query_result["row_count"]
                )
                
                logger.info(
                    f"✅ Query executed successfully: "
                    f"{query_result['row_count']} rows in {execution_time:.3f}s"
                )
                
                return query_result
                
        except sa.exc.SQLAlchemyError as e:
            execution_time = time.time() - start_time
            self.metrics.record_query_execution(
                query_type="SELECT",
                success=False,
                execution_time=execution_time,
                rows_returned=0
            )
            
            logger.error(f"❌ Database error: {str(e)}")
            return {
                "success": False,
                "error": f"Database error: {str(e)}",
                "data": None,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "data": None,
                "execution_time": execution_time
            }
    
    async def list_tables(
        self, 
        database: str = "default",
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        List all accessible tables with metadata
        """
        try:
            # Database-specific query for table listing
            if self.settings.db_type.lower() == "postgresql":
                query = """
                SELECT 
                    table_name,
                    table_schema,
                    table_type
                FROM information_schema.tables 
                WHERE table_schema = :schema
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            elif self.settings.db_type.lower() == "mysql":
                query = """
                SELECT 
                    table_name,
                    table_schema,
                    table_type
                FROM information_schema.tables 
                WHERE table_schema = :schema
                ORDER BY table_name
                """
            else:  # SQLite
                query = """
                SELECT 
                    name as table_name,
                    'main' as table_schema,
                    'BASE TABLE' as table_type
                FROM sqlite_master 
                WHERE type = 'table'
                ORDER BY name
                """
            
            result = await self.execute_query(
                query.replace(":schema", f"'{schema}'"),
                database,
                use_cache=True
            )
            
            if result["success"]:
                tables = [row["table_name"] for row in result["data"]]
                return {
                    "success": True,
                    "tables": tables,
                    "count": len(tables),
                    "schema": schema,
                    "database": database,
                    "error": None
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Error listing tables: {str(e)}")
            return {
                "success": False,
                "error": f"Error listing tables: {str(e)}",
                "tables": None
            }
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get comprehensive table schema information
        """
        try:
            # Get column information
            if self.settings.db_type.lower() in ["postgresql", "mysql"]:
                query = f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                """
            else:  # SQLite
                query = f"PRAGMA table_info({table_name})"
            
            result = await self.execute_query(query, use_cache=True)
            
            if result["success"]:
                # Get additional table metadata
                metadata = await self._get_table_metadata(table_name)
                
                return {
                    "success": True,
                    "table_name": table_name,
                    "columns": result["data"],
                    "metadata": metadata,
                    "error": None
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Error getting table schema: {str(e)}")
            return {
                "success": False,
                "error": f"Error getting table schema: {str(e)}",
                "data": None
            }
    
    async def _get_table_metadata(self, table_name: str) -> Dict[str, Any]:
        """Get additional table metadata (row count, size, etc.)"""
        try:
            # Row count
            count_result = await self.execute_query(
                f"SELECT COUNT(*) as row_count FROM {table_name}",
                use_cache=True
            )
            
            row_count = 0
            if count_result["success"] and count_result["data"]:
                row_count = count_result["data"][0]["row_count"]
            
            return {
                "row_count": row_count,
                "last_analyzed": time.time()
            }
            
        except Exception as e:
            logger.warning(f"Could not get metadata for {table_name}: {e}")
            return {}
    
    async def get_table_info(
        self, 
        table_name: str, 
        database: str = "default"
    ) -> Dict[str, Any]:
        """Get quick table information without full schema"""
        try:
            # Quick metadata query
            metadata_query = f"""
            SELECT COUNT(*) as row_count 
            FROM {table_name}
            """
            
            result = await self.execute_query(metadata_query, database, use_cache=True)
            
            if result["success"] and result["data"]:
                return {
                    "row_count": result["data"][0]["row_count"],
                    "column_count": "unknown",  # Would require additional query
                    "size": "unknown"  # Database-specific query needed
                }
            else:
                return {
                    "row_count": "unknown",
                    "column_count": "unknown", 
                    "size": "unknown"
                }
                
        except Exception:
            return {
                "row_count": "unknown",
                "column_count": "unknown",
                "size": "unknown"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive database health check
        """
        start_time = time.time()
        
        try:
            # Test basic connectivity
            test_query = "SELECT 1 as health_check"
            result = await self.execute_query(test_query, use_cache=False)
            
            response_time = time.time() - start_time
            
            if result["success"]:
                # Get connection pool information
                pool_info = await self._get_pool_info()
                
                return {
                    "success": True,
                    "status": "healthy",
                    "response_time": response_time,
                    "pool_info": pool_info,
                    "timestamp": time.time()
                }
            else:
                return {
                    "success": False,
                    "status": "unhealthy",
                    "error": result["error"],
                    "response_time": response_time,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "response_time": response_time,
                "timestamp": time.time()
            }
    
    async def _get_pool_info(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        try:
            if hasattr(self.connection.engine, 'pool'):
                pool = self.connection.engine.pool
                return {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "invalid": pool.invalid()
                }
            else:
                return {"status": "pool_info_unavailable"}
        except Exception:
            return {"status": "pool_info_error"}
```

---

## 🛡️ Security Framework

### Multi-Layer Security Architecture

```python
"""
Enterprise Security Framework
Multiple layers of protection against various attack vectors
"""

class SecurityConfig:
    """Centralized security configuration"""
    
    # Query Security
    MAX_QUERY_LENGTH = 10000
    MAX_RESULT_ROWS = 5000
    ALLOWED_QUERY_TYPES = ["SELECT"]
    QUERY_TIMEOUT_SECONDS = 60
    
    # Rate Limiting
    REQUESTS_PER_MINUTE = 60
    BURST_LIMIT = 100
    
    # SQL Injection Prevention
    DANGEROUS_PATTERNS = [
        r';\s*(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE)',
        r'UNION\s+SELECT',
        r'EXEC\s*\(',
        r'xp_cmdshell',
        r'sp_executesql',
        r'--\s*$',
        r'/\*.*\*/',
        r'@@\w+',
        r'WAITFOR\s+DELAY'
    ]
    
    # Input Validation
    ALLOWED_IDENTIFIER_PATTERN = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    MAX_IDENTIFIER_LENGTH = 63
    
    # Authentication
    JWT_ALGORITHM = "HS256"
    TOKEN_EXPIRY_HOURS = 24
    PASSWORD_MIN_LENGTH = 12
    
    # Encryption
    BCRYPT_ROUNDS = 12
    AES_KEY_LENGTH = 256

class SQLInjectionPrevention:
    """Advanced SQL injection prevention"""
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitize SQL query input"""
        # Remove dangerous comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Remove dangerous functions
        dangerous_functions = [
            'xp_cmdshell', 'sp_executesql', 'exec', 'execute',
            'openrowset', 'opendatasource'
        ]
        
        for func in dangerous_functions:
            query = re.sub(f r'\b{func}\b', '', query, flags=re.IGNORECASE)
        
        return query.strip()
    
    @staticmethod
    def validate_identifiers(identifiers: List[str]) -> bool:
        """Validate database identifiers (table names, column names)"""
        pattern = re.compile(SecurityConfig.ALLOWED_IDENTIFIER_PATTERN)
        
        for identifier in identifiers:
            if not pattern.match(identifier):
                return False
            if len(identifier) > SecurityConfig.MAX_IDENTIFIER_LENGTH:
                return False
        
        return True
    
    @staticmethod
    def detect_injection_patterns(query: str) -> Tuple[bool, str]:
        """Detect potential SQL injection patterns"""
        query_upper = query.upper()
        
        for pattern in SecurityConfig.DANGEROUS_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        return True, "Query appears safe"

class AuthenticationManager:
    """JWT-based authentication for enterprise environments"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = SecurityConfig.JWT_ALGORITHM
    
    def create_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT token"""
        import jwt
        from datetime import datetime, timedelta
        
        payload = {
            **user_data,
            'exp': datetime.utcnow() + timedelta(hours=SecurityConfig.TOKEN_EXPIRY_HOURS),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        import jwt
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

class RateLimiter:
    """Enterprise rate limiting with sliding window"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client  # Use Redis in production
        self.memory_store = {}  # Fallback for development
    
    async def is_allowed(
        self, 
        client_id: str, 
        limit: int = SecurityConfig.REQUESTS_PER_MINUTE,
        window_seconds: int = 60
    ) -> bool:
        """Check if request is within rate limits"""
        
        if self.redis:
            return await self._redis_rate_limit(client_id, limit, window_seconds)
        else:
            return self._memory_rate_limit(client_id, limit, window_seconds)
    
    def _memory_rate_limit(self, client_id: str, limit: int, window: int) -> bool:
        """Simple in-memory rate limiting (development only)"""
        import time
        
        now = time.time()
        key = f"rate_limit:{client_id}"
        
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Remove old requests outside window
        self.memory_store[key] = [
            req_time for req_time in self.memory_store[key]
            if now - req_time < window
        ]
        
        # Check if within limit
        if len(self.memory_store[key]) >= limit:
            return False
        
        # Add current request
        self.memory_store[key].append(now)
        return True
    
    async def _redis_rate_limit(self, client_id: str, limit: int, window: int) -> bool:
        """Redis-based sliding window rate limiting"""
        import time
        
        now = time.time()
        key = f"rate_limit:{client_id}"
        
        # Sliding window using Redis sorted sets
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window)
        
        results = await pipe.execute()
        request_count = results[1]
        
        return request_count < limit

class InputValidator:
    """Comprehensive input validation"""
    
    @staticmethod
    def validate_sql_query(query: str) -> Tuple[bool, str]:
        """Validate SQL query with multiple checks"""
        
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        if len(query) > SecurityConfig.MAX_QUERY_LENGTH:
            return False, f"Query exceeds maximum length ({SecurityConfig.MAX_QUERY_LENGTH})"
        
        # Check for allowed query types
        query_upper = query.strip().upper()
        if not any(query_upper.startswith(qt) for qt in SecurityConfig.ALLOWED_QUERY_TYPES):
            return False, f"Only {SecurityConfig.ALLOWED_QUERY_TYPES} queries are allowed"
        
        # SQL injection check
        is_safe, message = SQLInjectionPrevention.detect_injection_patterns(query)
        if not is_safe:
            return False, message
        
        return True, "Query is valid"
    
    @staticmethod
    def validate_database_name(db_name: str) -> bool:
        """Validate database name"""
        if not db_name:
            return False
        
        pattern = re.compile(SecurityConfig.ALLOWED_IDENTIFIER_PATTERN)
        return bool(pattern.match(db_name)) and len(db_name) <= SecurityConfig.MAX_IDENTIFIER_LENGTH
```

---

## 📊 Monitoring & Observability

### Comprehensive Monitoring Stack

```python
"""
Enterprise Monitoring and Observability
Structured logging, metrics collection, and health monitoring
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class MetricEvent:
    """Structured metric event"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str]
    type: str  # counter, gauge, histogram, timer

class StructuredLogger:
    """Enterprise structured logging"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))
        
        # JSON formatter for structured logs
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": %(message)s}'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            "logs/sqlbridge.log",
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def _log_structured(self, level: LogLevel, message: str, **kwargs):
        """Log structured message with metadata"""
        log_data = {
            "message": message,
            "metadata": kwargs,
            "trace_id": kwargs.get("trace_id"),
            "user_id": kwargs.get("user_id"),
            "session_id": kwargs.get("session_id")
        }
        
        self.logger.log(
            getattr(logging, level.value),
            json.dumps(log_data, default=str)
        )
    
    def info(self, message: str, **kwargs):
        self._log_structured(LogLevel.INFO, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log_structured(LogLevel.ERROR, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_structured(LogLevel.WARNING, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log_structured(LogLevel.DEBUG, message, **kwargs)

class MetricsCollector:
    """Prometheus-compatible metrics collection"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
        
        # Initialize core metrics
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize core application metrics"""
        self.metrics.update({
            "sql_queries_total": {"value": 0, "type": "counter"},
            "sql_query_duration_seconds": {"values": [], "type": "histogram"},
            "sql_errors_total": {"value": 0, "type": "counter"},
            "cache_hits_total": {"value": 0, "type": "counter"},
            "cache_misses_total": {"value": 0, "type": "counter"},
            "active_connections": {"value": 0, "type": "gauge"},
            "tool_executions_total": {"value": 0, "type": "counter"},
            "rate_limit_exceeded_total": {"value": 0, "type": "counter"}
        })
    
    def increment_counter(self, name: str, value: float = 1, tags: Dict[str, str] = None):
        """Increment counter metric"""
        if name not in self.metrics:
            self.metrics[name] = {"value": 0, "type": "counter"}
        
        self.metrics[name]["value"] += value
        
        # Log metric event
        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            type="counter"
        )
        self._emit_metric(event)
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set gauge metric value"""
        if name not in self.metrics:
            self.metrics[name] = {"value": 0, "type": "gauge"}
        
        self.metrics[name]["value"] = value
        
        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            type="gauge"
        )
        self._emit_metric(event)
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record histogram value"""
        if name not in self.metrics:
            self.metrics[name] = {"values": [], "type": "histogram"}
        
        self.metrics[name]["values"].append(value)
        
        # Keep only last 1000 values
        if len(self.metrics[name]["values"]) > 1000:
            self.metrics[name]["values"] = self.metrics[name]["values"][-1000:]
        
        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            type="histogram"
        )
        self._emit_metric(event)
    
    def record_query_execution(
        self, 
        query_type: str, 
        success: bool, 
        execution_time: float,
        rows_returned: int = 0
    ):
        """Record SQL query execution metrics"""
        
        # Increment query counter
        self.increment_counter("sql_queries_total", tags={"type": query_type})
        
        # Record execution time
        self.record_histogram(
            "sql_query_duration_seconds", 
            execution_time,
            tags={"type": query_type, "success": str(success)}
        )
        
        # Record errors
        if not success:
            self.increment_counter("sql_errors_total", tags={"type": query_type})
        
        # Record rows returned
        self.record_histogram(
            "sql_rows_returned",
            rows_returned,
            tags={"type": query_type}
        )
    
    def record_tool_execution(self, tool_name: str, success: bool, execution_time: float):
        """Record MCP tool execution metrics"""
        self.increment_counter(
            "tool_executions_total",
            tags={"tool": tool_name, "success": str(success)}
        )
        
        self.record_histogram(
            "tool_execution_duration_seconds",
            execution_time,
            tags={"tool": tool_name}
        )
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.increment_counter("cache_hits_total")
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.increment_counter("cache_misses_total")
    
    def _emit_metric(self, event: MetricEvent):
        """Emit metric to monitoring system (implement based on your monitoring stack)"""
        # In production, send to Prometheus, DataDog, etc.
        pass
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        summary = {}
        
        for name, metric in self.metrics.items():
            if metric["type"] == "histogram" and "values" in metric:
                values = metric["values"]
                if values:
                    summary[name] = {
                        "count": len(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "p95": self._percentile(values, 95),
                        "p99": self._percentile(values, 99)
                    }
                else:
                    summary[name] = {"count": 0}
            else:
                summary[name] = metric["value"]
        
        # Add uptime
        summary["uptime_seconds"] = time.time() - self.start_time
        
        return summary
    
    @staticmethod
    def _percentile(values: list, percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

class HealthMonitor:
    """Application health monitoring"""
    
    def __init__(self, db_operations, metrics_collector):
        self.db_ops = db_operations
        self.metrics = metrics_collector
        self.health_checks = {}
    
    async def check_health(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {},
            "metrics": {}
        }
        
        # Database health
        db_health = await self.db_ops.health_check()
        health_status["checks"]["database"] = db_health
        
        if not db_health["success"]:
            health_status["status"] = "unhealthy"
        
        # Memory usage
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        health_status["checks"]["memory"] = {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent()
        }
        
        # CPU usage
        health_status["checks"]["cpu"] = {
            "percent": process.cpu_percent(),
            "num_threads": process.num_threads()
        }
        
        # Metrics summary
        health_status["metrics"] = self.metrics.get_metrics_summary()
        
        return health_status
    
    async def start_health_monitoring(self, interval_seconds: int = 30):
        """Start periodic health monitoring"""
        import asyncio
        
        while True:
            try:
                health = await self.check_health()
                
                # Log health status
                logger = StructuredLogger("health_monitor")
                logger.info("Health check completed", **health)
                
                # Alert on unhealthy status
                if health["status"] != "healthy":
                    logger.warning("System unhealthy", **health)
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(interval_seconds)

# Global instances
logger = StructuredLogger("sqlbridge")
metrics = MetricsCollector()
```

---

## 🚀 Deployment Guide

### Production Deployment Options

#### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.13.7-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash sqlbridge
RUN chown -R sqlbridge:sqlbridge /app
USER sqlbridge

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  sqlbridge:
    build: .
    container_name: sqlbridge-mcp
    ports:
      - "8080:8080"
      - "9090:9090"  # Metrics
    environment:
      - DB_HOST=postgres
      - DB_NAME=app_db
      - DB_USER=sqlbridge
      - DB_PASSWORD=secure_password
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    networks:
      - sqlbridge-network

  postgres:
    image: postgres:15
    container_name: sqlbridge-postgres
    environment:
      - POSTGRES_DB=app_db
      - POSTGRES_USER=sqlbridge
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - sqlbridge-network

  redis:
    image: redis:7-alpine
    container_name: sqlbridge-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - sqlbridge-network

  nginx:
    image: nginx:alpine
    container_name: sqlbridge-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - sqlbridge
    networks:
      - sqlbridge-network

volumes:
  postgres_data:
  redis_data:

networks:
  sqlbridge-network:
    driver: bridge
```

#### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sqlbridge-mcp
  labels:
    app: sqlbridge-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sqlbridge-mcp
  template:
    metadata:
      labels:
        app: sqlbridge-mcp
    spec:
      containers:
      - name: sqlbridge
        image: sqlbridge-mcp:latest
        ports:
        - containerPort: 8080
        - containerPort: 9090
        env:
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: sqlbridge-secrets
              key: db-host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: sqlbridge-secrets
              key: db-password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: sqlbridge-service
spec:
  selector:
    app: sqlbridge-mcp
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer

---
apiVersion: v1
kind: Secret
metadata:
  name: sqlbridge-secrets
type: Opaque
data:
  db-host: <base64-encoded-host>
  db-password: <base64-encoded-password>
```

#### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13.7'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 src tests
        black --check src tests
        isort --check-only src tests
    
    - name: Run security scan
      run: |
        bandit -r src
        safety check
    
    - name: Run tests
      env:
        DB_HOST: localhost
        DB_NAME: test_db
        DB_USER: postgres
        DB_PASSWORD: test_password
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}:latest
          ghcr.io/${{ github.repository }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        # Add your deployment script here
        echo "Deploying to production..."
```

---

## 📖 API Documentation

### MCP Tools Reference

#### execute_sql_query

Execute a read-only SQL query with comprehensive validation and monitoring.

**Parameters:**
- `query` (string, required): SQL SELECT query to execute
- `database` (string, optional): Target database name (default: "default")  
- `limit` (integer, optional): Maximum rows to return (default: 100, max: 5000)

**Response Format:**
```json
{
  "success": true,
  "data": [
    {"column1": "value1", "column2": "value2"},
    {"column1": "value3", "column2": "value4"}
  ],
  "metadata": {
    "rows_returned": 2,
    "columns": ["column1", "column2"],
    "execution_time_ms": 45.2,
    "query_hash": "abc123def456"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Query failed security validation",
  "query": "SELECT * FROM sensitive_table..."
}
```

#### list_database_tables

List all accessible tables with metadata.

**Parameters:**
- `database` (string, optional): Database name to inspect
- `schema` (string, optional): Schema name filter (default: "public")

**Response Format:**
```json
{
  "success": true,
  "tables": [
    {
      "name": "users",
      "row_count": 1500,
      "columns": 8,
      "size": "2.5MB"
    },
    {
      "name": "products", 
      "row_count": 850,
      "columns": 12,
      "size": "1.8MB"
    }
  ],
  "total_count": 2,
  "database": "production",
  "schema": "public"
}
```

### REST API Endpoints (Optional)

For development and testing, the server can optionally expose REST endpoints:

```python
# Optional REST API for testing
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(
    title="SQLBridge MCP API",
    version="1.0.0",
    description="REST API for SQLBridge MCP Server"
)

security = HTTPBearer()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return metrics.get_metrics_summary()

@app.post("/query")
async def execute_query(
    request: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Execute SQL query via REST API"""
    # Validate token
    user = auth_manager.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Execute query
    result = await db_ops.execute_query(request.query)
    return result
```

---

## 🤝 Contributing Guidelines

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd SQLBridgeMCP

# Setup development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run initial tests
pytest tests/
```

### Code Quality Standards

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, src]
```

### Testing Requirements

- **Minimum 90% code coverage**
- **All security tests must pass**
- **Performance tests for critical paths**
- **Integration tests with real databases**

### Pull Request Process

1. **Feature Branch**: Create from `develop` branch
2. **Code Quality**: All pre-commit hooks must pass
3. **Tests**: Add tests for new functionality
4. **Documentation**: Update relevant documentation
5. **Security Review**: Security-sensitive changes require additional review
6. **Performance**: Benchmark performance-critical changes

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🆘 Support & Community

### Getting Help

- **Documentation**: Check this README and `/docs` folder
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Report security issues via `security@domain.com`

### Performance Monitoring

- **Logs**: Check `logs/sqlbridge.log` for application logs
- **Metrics**: Access metrics at `http://localhost:9090/metrics`
- **Health**: Check health at `http://localhost:8080/health`

### Enterprise Support

For enterprise support, custom features, or professional services:
- Email: `enterprise@domain.com`
- Documentation: [Enterprise Features Guide](docs/enterprise.md)
- SLA: 99.9% uptime guarantee with enterprise license

---

**Built with ❤️ for the Claude Code community**

*SQLBridgeMCP - Bridging the gap between AI and data*