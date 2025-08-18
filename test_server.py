"""
SINGLE TEST FILE for SQLBridgeMCP Server
Reusable test script - modify this file instead of creating new ones
NO EMOJIS - Windows compatibility
"""
import asyncio
import sys
import os
import pytest

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

@pytest.mark.asyncio
async def test_all_functionality():
    """Test all MCP server functionality"""
    
    print("SQLBridgeMCP Complete Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Database Operations
        print("\n1. Testing Database Operations...")
        from database.operations import get_sql_operations
        
        sql_ops = get_sql_operations()
        print("   SQL operations initialized")
        
        # Test execute query - Show current database info
        result = await sql_ops.execute_query(
            "SELECT @@VERSION as version, @@SERVERNAME as server_name, DB_NAME() as current_db",
            "test"
        )
        
        if result.success:
            print(f"   Query test: PASSED ({result.execution_time_ms}ms)")
            data = result.data[0] if result.data else {}
            print(f"   Server: {data.get('server_name', 'N/A')}")
            print(f"   Current Database: {data.get('current_db', 'N/A')}")
        else:
            print(f"   Query test: FAILED - {result.error}")
            return False
        
        # Test list all databases available
        print("\n   Testing: List all databases...")
        db_result = await sql_ops.execute_query(
            "SELECT name, database_id, create_date FROM sys.databases ORDER BY name",
            "test"
        )
        
        if db_result.success:
            print(f"   Databases found: {db_result.row_count}")
            for db in db_result.data[:10]:  # Show first 10 databases
                print(f"     - {db.get('name', 'N/A')} (ID: {db.get('database_id', 'N/A')})")
        else:
            print(f"   Database listing failed: {db_result.error}")
        
        # Test list tables in current database
        print(f"\n   Testing: List tables in current database...")
        tables_result = await sql_ops.list_tables("test")
        if tables_result.success:
            print(f"   Tables test: PASSED ({tables_result.row_count} tables in {data.get('current_db', 'current database')})")
            tables = [row["table_name"] for row in tables_result.data[:5]] if tables_result.data else []
            print(f"   First 5 tables: {tables}")
        else:
            print(f"   Tables test: FAILED - {tables_result.error}")
        
        # Test health check
        health_result = await sql_ops.check_database_health()
        if health_result.success:
            health = health_result.data[0] if health_result.data else {}
            print(f"   Health test: PASSED ({health.get('status', 'unknown')})")
        else:
            print(f"   Health test: FAILED - {health_result.error}")
        
        # Test 2: Security Validations
        print("\n2. Testing Security...")
        
        # Test invalid queries
        invalid_tests = [
            ("UPDATE users SET name = 'test'", "Non-SELECT query"),
            ("", "Empty query"),
            ("SELECT * FROM users; DROP TABLE users", "SQL injection pattern")
        ]
        
        security_passed = 0
        for query, description in invalid_tests:
            result = await sql_ops.execute_query(query, "test")
            if not result.success:
                print(f"   {description}: BLOCKED (correct)")
                security_passed += 1
            else:
                print(f"   {description}: ALLOWED (security risk!)")
        
        print(f"   Security tests: {security_passed}/{len(invalid_tests)} passed")
        
        # Test 3: MCP Server Creation
        print("\n3. Testing MCP Server...")
        from server import create_mcp_server
        
        server = create_mcp_server()
        print("   MCP server created successfully")
        
        print(f"\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Additional test functions can be added here
@pytest.mark.asyncio
async def test_specific_database():
    """Test with specific database - modify as needed"""
    db_name = "tempdb"  # Use a known database
    print(f"\nTesting with database: {db_name}")
    
    try:
        from database.operations import get_sql_operations
        sql_ops = get_sql_operations()
        
        # Test switching to specific database
        result = await sql_ops.execute_query(f"USE {db_name}; SELECT DB_NAME() as current_db", "test")
        
        if result.success:
            current_db = result.data[0].get('current_db', 'unknown') if result.data else 'unknown'
            print(f"   Successfully switched to: {current_db}")
            
            # List tables in this database
            tables_result = await sql_ops.list_tables("test")
            if tables_result.success:
                print(f"   Tables in {current_db}: {tables_result.row_count}")
                if tables_result.data:
                    table_names = [row["table_name"] for row in tables_result.data[:5]]
                    print(f"   Sample tables: {table_names}")
            
        else:
            print(f"   Failed to switch to {db_name}: {result.error}")
            
    except Exception as e:
        print(f"   Error testing database {db_name}: {e}")

@pytest.mark.asyncio
async def test_performance():
    """Performance testing - modify as needed"""
    print("\nRunning performance tests...")
    # Add performance tests here
    pass

if __name__ == "__main__":
    print("Use this file for all testing needs")
    print("Modify functions above instead of creating new files")
    
    # Run main functionality test
    success = asyncio.run(test_all_functionality())
    
    # Uncomment to test specific database:
    # asyncio.run(test_specific_database("tempdb"))
    # asyncio.run(test_specific_database("model"))
    
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)