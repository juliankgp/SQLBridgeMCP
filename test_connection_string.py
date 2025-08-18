"""
Test simple para verificar que CONNECTION_STRING funciona correctamente
"""
import os
import sys
import tempfile

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_connection_string_priority():
    """Test que CONNECTION_STRING tiene prioridad sobre variables individuales"""
    
    # Guardar valores originales
    original_env = {}
    env_vars = ['DB_TYPE', 'CONNECTION_STRING', 'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    for var in env_vars:
        original_env[var] = os.environ.get(var)
    
    try:
        # Test 1: CONNECTION_STRING tiene prioridad
        os.environ['DB_TYPE'] = 'sqlserver'
        os.environ['CONNECTION_STRING'] = 'Server=test_server;Database=test_db;User Id=test_user;Password=test_pass;TrustServerCertificate=true'
        os.environ['DB_HOST'] = 'wrong_host'  # Esto debería ser ignorado
        os.environ['DB_USER'] = 'wrong_user'  # Esto debería ser ignorado
        
        from config.settings import load_database_config
        
        # Recargar configuración
        import importlib
        import config.settings as settings_module
        importlib.reload(settings_module)
        from config.settings import load_database_config
        
        config = load_database_config()
        
        # Verificar que usa CONNECTION_STRING
        assert config.connection_string is not None
        assert 'test_server' in config.connection_string
        assert 'test_db' in config.connection_string
        
        # Verificar que get_connection_string() funciona
        conn_str = config.get_connection_string()
        assert 'mssql+aioodbc://' in conn_str
        assert 'test_user:test_pass@test_server' in conn_str
        
        print("Test 1 PASSED: CONNECTION_STRING tiene prioridad")
        
        # Test 2: Fallback a variables individuales
        del os.environ['CONNECTION_STRING']
        os.environ['DB_HOST'] = 'fallback_host'
        os.environ['DB_NAME'] = 'fallback_db'
        os.environ['DB_USER'] = 'fallback_user'  
        os.environ['DB_PASSWORD'] = 'fallback_pass'
        
        # Recargar configuración
        importlib.reload(settings_module)
        from config.settings import load_database_config
        config2 = load_database_config()
        
        # Verificar que usa variables individuales
        assert config2.connection_string is None
        assert config2.host == 'fallback_host'
        assert config2.name == 'fallback_db'
        assert config2.user == 'fallback_user'
        
        conn_str2 = config2.get_connection_string()
        assert 'fallback_user:fallback_pass@fallback_host' in conn_str2
        
        print("Test 2 PASSED: Fallback a variables individuales funciona")
        
        # Test 3: Parsing de SQL Server connection string
        os.environ['CONNECTION_STRING'] = 'Server=localhost,1433;Database=MyDB;User Id=sa;Password=MyPass123;TrustServerCertificate=true;Encrypt=false'
        
        importlib.reload(settings_module)
        from config.settings import load_database_config
        config3 = load_database_config()
        
        conn_str3 = config3.get_connection_string()
        assert 'mssql+aioodbc://' in conn_str3
        assert 'sa:MyPass123@localhost' in conn_str3
        assert 'MyDB' in conn_str3
        assert 'TrustServerCertificate=yes' in conn_str3
        
        print("Test 3 PASSED: Parsing complejo de SQL Server funciona")
        print("\nTodos los tests de CONNECTION_STRING PASARON!")
        
        return True
        
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Restaurar valores originales
        for var, value in original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

if __name__ == "__main__":
    print("Testing CONNECTION_STRING functionality...")
    success = test_connection_string_priority()
    print(f"\n{'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)