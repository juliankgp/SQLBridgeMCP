# SQLBridgeMCP 🚀

**Connect any AI to your SQL database securely**

[![Python 3.13.7](https://img.shields.io/badge/python-3.13.7-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SQLBridgeMCP** is a secure bridge between AI assistants and your SQL databases. Configure once, use with any MCP-compatible AI tool.

## ✨ What can you do?

💬 **"Claude, how many active users do we have?"**  
📊 **"Show me sales by region for this month"**  
🔍 **"Find all orders over $1000 from last week"**  

## 🎯 Works with

**AI Tools:** Claude Code • Claude API • GPT with MCP • Custom Apps  
**Databases:** PostgreSQL • MySQL • SQLite • SQL Server  
**Your Data:** Private • Secure • Under your control

## 🚀 Quick Start

### 1. **Install**
```bash
git clone <this-repo>
cd SQLBridgeMCP
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. **Configure your database** (Choose one method)

**🚀 OPTION A: CONNECTION_STRING (Simpler)**
```bash
cp .env.example .env
# Edit .env with ONE line:
DB_TYPE=sqlserver
CONNECTION_STRING=Server=localhost;Database=mydb;User Id=user;Password=pass;TrustServerCertificate=true
```

**🔧 OPTION B: Individual Variables (Traditional)**
```bash
cp .env.example .env  
# Edit .env with separate variables:
DB_TYPE=sqlserver
DB_HOST=localhost
DB_NAME=mydb  
DB_USER=myuser
DB_PASSWORD=mypass
```

### 3. **Connect to Claude Code**

**🚀 With CONNECTION_STRING:**
```json
{
  "mcpServers": {
    "sql-bridge": {
      "command": "python",
      "args": ["/path/to/SQLBridgeMCP/main.py"],
      "env": {
        "DB_TYPE": "sqlserver",
        "CONNECTION_STRING": "Server=your-server;Database=your-db;User Id=user;Password=pass;TrustServerCertificate=true"
      }
    }
  }
}
```

**🔧 Or with individual variables:**
```json
{
  "mcpServers": {
    "sql-bridge": {
      "command": "python", 
      "args": ["/path/to/SQLBridgeMCP/main.py"],
      "env": {
        "DB_TYPE": "postgresql",
        "DB_HOST": "your-server",
        "DB_NAME": "your-database",
        "DB_USER": "your-user",
        "DB_PASSWORD": "your-password"
      }
    }
  }
}
```

### 4. **Start chatting with your data!**
*"Claude, show me the top 10 customers by revenue"* ✨

---

## 🔧 How it works

**You run your own server** → **Connects to your database** → **Works with any MCP client**

```
[Your AI Tool] ──► [Your SQLBridgeMCP] ──► [Your Database]
                     (Your Config)         (Your Data)
```

**🔒 Your data stays private** - No third parties, no cloud services, just you.

## 🗃️ Database Support

| Database | Easy Setup | Example |
|----------|------------|---------|
| **PostgreSQL** | ✅ | `DB_TYPE=postgresql` |
| **MySQL** | ✅ | `DB_TYPE=mysql` |
| **SQLite** | ✅ | `DB_TYPE=sqlite` |
| **SQL Server** | ✅ | `DB_TYPE=sqlserver` |

## 🛡️ Security

- **Read-only by default** - Only SELECT queries allowed
- **SQL injection protection** - Input validation and sanitization  
- **Your credentials** - Stored locally in your `.env` file
- **No data sharing** - Everything runs on your infrastructure

## 📖 Available MCP Tools

Your AI can use these 6 tools to interact with your database:

### **Core Database Operations**
- **`execute_sql_query`** - Execute SELECT queries safely with parameters
  - *Example: "Run a query to find active employees"*
- **`list_tables`** - List all tables in the current database
  - *Example: "What tables are available?"*
- **`describe_table`** - Get detailed table schema and optionally sample data
  - *Example: "Show me the structure of the Users table"*

### **Database Management** 
- **`database_health`** - Check connection status and performance metrics
  - *Example: "Is the database connection healthy?"*
- **`list_all_databases`** - Show all databases in the SQL Server instance
  - *Example: "What databases are available on this server?"*
- **`list_tables_from_database`** - List tables from a specific database
  - *Example: "Show tables in the 'Analytics' database"*

### **🛡️ Security Features**
- **Read-only access** - Only SELECT queries allowed
- **Input validation** - Prevents SQL injection attacks
- **Query limits** - Configurable timeouts and row limits
- **Audit logging** - All queries are logged for security

## 🚀 Advanced Usage

### **Example Usage with AI**

**💬 Natural Language Examples:**

*"How many active employees do we have?"*
→ Uses `execute_sql_query` with `SELECT COUNT(*) FROM Employees WHERE Active = 1`

*"Show me all the tables in our database"*
→ Uses `list_tables` to display all available tables

*"What's the structure of the Projects table?"*
→ Uses `describe_table` with `table_name="Projects"`

*"Is our database connection working properly?"*
→ Uses `database_health` to check status and performance

### **Custom Applications**
```python
# Example: Using MCP tools programmatically
import asyncio
from mcp_client import MCPClient

async def get_employee_count():
    client = MCPClient(server_path="./main.py")
    result = await client.call_tool("execute_sql_query", {
        "query": "SELECT COUNT(*) as total FROM Employees WHERE Active = 1"
    })
    return result["data"][0]["total"]

# Get table information
async def explore_database():
    client = MCPClient(server_path="./main.py")
    
    # List all tables
    tables = await client.call_tool("list_tables")
    print(f"Found {tables['count']} tables")
    
    # Get schema for specific table
    schema = await client.call_tool("describe_table", {
        "table_name": "Employees",
        "include_sample_data": True
    })
    print(f"Employees table has {len(schema['schema'])} columns")
```

### Multiple Databases
Configure different MCP servers for different databases in your Claude Code config.

### Production Deployment
- Use Docker for containerization
- Configure SSL for database connections
- Set up monitoring and logging
- Create read-only database users

## 📋 Configuration Examples

### 🚀 With CONNECTION_STRING (Recommended)

#### **SQL Server (Auto-parsing)**
```bash
DB_TYPE=sqlserver
CONNECTION_STRING=Server=localhost;Database=mydb;User Id=sa;Password=MyPass123;TrustServerCertificate=true
```

#### **PostgreSQL (SQLAlchemy format)**
```bash
DB_TYPE=postgresql  
CONNECTION_STRING=postgresql+psycopg://user:pass@localhost:5432/mydb
```

#### **MySQL (SQLAlchemy format)**
```bash
DB_TYPE=mysql
CONNECTION_STRING=mysql+aiomysql://user:pass@localhost:3306/mydb
```

### 🔧 With Individual Variables (Fallback)

#### **PostgreSQL**
```bash
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=myuser
DB_PASSWORD=mypass
```

#### **MySQL**
```bash
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mydb
DB_USER=myuser
DB_PASSWORD=mypass
```

#### **SQLite (always uses individual variables)**
```bash
DB_TYPE=sqlite
DB_NAME=/path/to/database.db
```

### 📋 **Configuration Priority**
1. **CONNECTION_STRING** (if provided) 
2. **Individual variables** (DB_HOST, DB_USER, etc.)
3. **Error** if neither is configured

## 🆘 Support

- **📚 Documentation**: See `GUIA_COMPLETA_MCP_SQL.md` for detailed setup
- **🐛 Issues**: Report problems via GitHub Issues  
- **💬 Questions**: Start a discussion in GitHub Discussions

## 🔗 Compatible MCP Clients

- **Claude Code** - Desktop app with native MCP support
- **Claude API** - Programmatic access via API
- **Custom Apps** - Any application implementing MCP protocol
- **VS Code Extensions** - With MCP support
- **Enterprise Tools** - Internal AI assistants

---

**Built with ❤️ for the MCP community**

*SQLBridgeMCP - Your personal bridge between AI and your data*