"""
Main MCP server for SQL database connections
Handles available tools for any MCP compatible client
Using FastMCP from version 1.13.0
"""
import json
import asyncio
from typing import Dict, Any, List
from mcp.server import FastMCP

from database.operations import get_sql_operations

def create_mcp_server() -> FastMCP:
    """
    Factory Pattern: Creates and configures MCP server with SQL tools
    
    Returns:
        FastMCP: Configured MCP server ready to use
    """
    # Create MCP server instance with FastMCP (simplified API in 1.13.0)
    server = FastMCP("SQLBridgeMCP")
    
    # ==========================================
    # Tool 1: Execute SQL queries
    # ==========================================
    @server.tool()
    async def execute_sql_query(query: str, database: str = "default") -> Dict[str, Any]:
        """
        Executes a safe SELECT SQL query on the database.
        
        Args:
            query: The SQL SELECT query to execute (read-only allowed)
            database: Database name (optional, default: "default")
            
        Returns:
            Dict with query result and metadata
        """
        print(f"Executing SQL query: {query[:50]}...")
        
        try:
            # Use real database operations
            sql_ops = get_sql_operations()
            result = await sql_ops.execute_query(query, database)
            
            # Convert QueryResult to dictionary format
            return {
                "success": result.success,
                "data": result.data,
                "row_count": result.row_count,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error,
                "metadata": result.metadata or {},
                "database": database
            }
            
        except Exception as e:
            print(f"Error executing query: {e}")
            return {
                "success": False,
                "error": f"Query execution failed: {e}",
                "database": database
            }
    
    # ==========================================
    # Tool 2: List tables
    # ==========================================
    @server.tool()
    async def list_tables(database: str = "default") -> Dict[str, Any]:
        """
        Lists all available tables in the database.
        
        Args:
            database: Database name (optional, default: "default")
            
        Returns:
            Dict with list of available tables
        """
        print(f"Listing tables from database: {database}")
        
        try:
            # Use real database operations
            sql_ops = get_sql_operations()
            result = await sql_ops.list_tables(database)
            
            # Convert QueryResult to dictionary format
            tables = [row["table_name"] for row in result.data] if result.data else []
            
            return {
                "success": result.success,
                "tables": tables,
                "count": result.row_count,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error,
                "metadata": result.metadata or {},
                "database": database
            }
            
        except Exception as e:
            print(f"Error listing tables: {e}")
            return {
                "success": False,
                "error": f"Failed to list tables: {e}",
                "database": database
            }
    
    # ==========================================
    # Tool 3: Describe table
    # ==========================================
    @server.tool()
    async def describe_table(table_name: str, include_sample_data: bool = False) -> Dict[str, Any]:
        """
        Gets the schema and structure of a specific table.
        
        Args:
            table_name: Name of the table to describe
            include_sample_data: Include sample data from table (default: False)
            
        Returns:
            Dict with table schema and optionally sample data
        """
        print(f"Describing table: {table_name}")
        
        if not table_name or not table_name.strip():
            return {
                "success": False,
                "error": "Table name is required"
            }
        
        try:
            # Use real database operations
            sql_ops = get_sql_operations()
            result = await sql_ops.describe_table(table_name, include_sample_data)
            
            # Convert QueryResult to dictionary format
            return {
                "success": result.success,
                "table_name": table_name,
                "schema": result.data,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error,
                "metadata": result.metadata or {},
                "include_sample_data": include_sample_data
            }
            
        except Exception as e:
            print(f"Error describing table: {e}")
            return {
                "success": False,
                "error": f"Failed to describe table: {e}",
                "table_name": table_name
            }
    
    # ==========================================
    # Tool 4: Check database health
    # ==========================================
    @server.tool()
    async def database_health() -> Dict[str, Any]:
        """
        Checks database connection status and health.
        
        Returns:
            Dict with database status information
        """
        print("Checking database health")
        
        try:
            # Use real database operations
            sql_ops = get_sql_operations()
            result = await sql_ops.check_database_health()
            
            # Convert QueryResult to dictionary format
            return {
                "success": result.success,
                "health_data": result.data,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error,
                "metadata": result.metadata or {}
            }
            
        except Exception as e:
            print(f"Error checking database health: {e}")
            return {
                "success": False,
                "error": f"Database health check failed: {e}"
            }
    
    # ==========================================
    # Tool 5: List all databases
    # ==========================================
    @server.tool()
    async def list_all_databases() -> Dict[str, Any]:
        """
        Lists all available databases in the SQL Server instance.
        
        Returns:
            Dict with list of available databases
        """
        print("Listing all available databases")
        
        try:
            # Use real database operations
            sql_ops = get_sql_operations()
            result = await sql_ops.list_all_databases()
            
            # Convert QueryResult to dictionary format
            databases = [row["database_name"] for row in result.data] if result.data else []
            
            return {
                "success": result.success,
                "databases": databases,
                "count": result.row_count,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error,
                "metadata": result.metadata or {}
            }
            
        except Exception as e:
            print(f"Error listing databases: {e}")
            return {
                "success": False,
                "error": f"Failed to list databases: {e}"
            }
    
    # ==========================================
    # Tool 6: List tables from specific database
    # ==========================================
    @server.tool()
    async def list_tables_from_database(database_name: str) -> Dict[str, Any]:
        """
        Lists all tables from a specific database.
        
        Args:
            database_name: Name of the database to query
            
        Returns:
            Dict with list of tables from the specified database
        """
        print(f"Listing tables from database: {database_name}")
        
        if not database_name or not database_name.strip():
            return {
                "success": False,
                "error": "Database name is required"
            }
        
        try:
            # Use real database operations
            sql_ops = get_sql_operations()
            result = await sql_ops.list_tables_from_database(database_name)
            
            # Convert QueryResult to dictionary format
            tables = [row["TABLE_NAME"] for row in result.data] if result.data else []
            
            return {
                "success": result.success,
                "database_name": database_name,
                "tables": tables,
                "count": result.row_count,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error,
                "metadata": result.metadata or {}
            }
            
        except Exception as e:
            print(f"Error listing tables from database {database_name}: {e}")
            return {
                "success": False,
                "error": f"Failed to list tables from database {database_name}: {e}",
                "database_name": database_name
            }

    print("MCP Server created with 6 SQL tools available")
    return server

# ==========================================
# Local testing utility function
# ==========================================

async def test_server_locally():
    """
    Function to test MCP server locally without external client
    Useful for development and debugging
    """
    print("Starting local MCP server test...")
    
    # Create server
    server = create_mcp_server()
    
    print("Available tools:")
    # In FastMCP, tools are registered automatically
    print("  - execute_sql_query")
    print("  - list_tables") 
    print("  - describe_table")
    print("  - database_health")
    print("  - list_all_databases")
    print("  - list_tables_from_database")
    
    # Simulate some test calls
    print("\nTesting tools...")
    
    # Test SQL query
    try:
        # Access the function registered in the server
        query_result = await server._tools["execute_sql_query"]["function"](
            "SELECT * FROM users WHERE active = true", 
            "test_db"
        )
        print(f"execute_sql_query: {query_result['success']}")
    except Exception as e:
        print(f"Error testing execute_sql_query: {e}")
    
    # Test table listing
    try:
        tables_result = await server._tools["list_tables"]["function"]("test_db")
        print(f"list_tables: {len(tables_result.get('tables', []))} tables")
    except Exception as e:
        print(f"Error testing list_tables: {e}")
    
    print("Local test completed successfully")

if __name__ == "__main__":
    # Allow running server directly for testing
    print("SQLBridgeMCP Server - Local test mode")
    print("Using FastMCP from version 1.13.0")
    asyncio.run(test_server_locally())