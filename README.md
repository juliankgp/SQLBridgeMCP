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
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### What is `pip install -r requirements.txt` and why is it needed?

Python doesn't come with everything pre-installed. This project depends on external libraries that need to be downloaded once before it can run. The `requirements.txt` file is just a list of those libraries with their minimum versions. Running `pip install -r requirements.txt` reads that list and installs all of them automatically.

**What gets installed:**

| Package | Why it's needed |
|---|---|
| `mcp` | The MCP protocol framework — this IS the server that Claude Code talks to |
| `sqlalchemy` | Unified interface to connect and query any SQL database |
| `pyodbc` / `aioodbc` | Drivers to connect specifically to SQL Server |
| `psycopg` | Driver to connect to PostgreSQL |
| `aiomysql` | Driver to connect to MySQL |
| `aiosqlite` | Driver to connect to SQLite |
| `pydantic` | Validates configuration values (catches bad credentials early) |
| `python-dotenv` | Reads your `.env` file so you don't have to set variables manually |
| `fastapi` / `uvicorn` | Optional REST API layer if you want to expose the server over HTTP |
| `pytest` | Only needed if you want to run the test suite |
| `redis` | Optional cache and rate limiting |
| `prometheus-client` | Optional metrics and monitoring |

> **You only need to run this once** per machine. After that the libraries are stored in the `venv` folder and available every time you start the server.

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

### 3. **Connect to your AI tool**

Choose your AI platform and follow the specific setup:

## **🤖 Claude Code**

### **⚡ Option A: Setup Script (Recommended)**

The script handles everything automatically: creates the virtual environment, installs dependencies, and registers the MCP server globally in Claude Code.

**Step 1:** Copy the example script and rename it:
```
setup_mcp.example.bat  →  setup_mcp.bat
```

**Step 2:** Open `setup_mcp.bat` and fill in your credentials:
```bat
set "DB_HOST=your-server.database.windows.net"
set "DB_NAME=your-database-name"
set "DB_USER=your-username"
set "DB_PASSWORD=your-password"
```

**Step 3:** Double-click `setup_mcp.bat` — the script will:
- Verify Python is installed
- Create the `venv` if it doesn't exist
- Install all dependencies from `requirements.txt`
- Register `sql-bridge` in Claude Code at user scope (`-s user`)

**Step 4:** Restart Claude Code completely (close and reopen).

**Step 5:** Test it:
```
Can you check the health of my SQL database?
```

> `setup_mcp.bat` is in `.gitignore` so your real credentials are never committed.

---

### **Option B: Manual CLI command**

If you prefer to set up manually, first create the venv and install dependencies:

```bash
cd SQLBridgeMCP
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Then register the MCP server at user scope (available in all projects):

```bash
claude mcp add sql-bridge \
  "C:\path\to\SQLBridgeMCP\venv\Scripts\python.exe" \
  "C:\path\to\SQLBridgeMCP\main.py" \
  -s user \
  -e DB_TYPE=sqlserver \
  -e DB_HOST=your-server.database.windows.net \
  -e DB_PORT=1433 \
  -e DB_NAME=your-database \
  -e DB_USER=your-user \
  -e DB_PASSWORD=your-password
```

> The `-s user` flag registers the server globally for your user (`~/.claude.json`), so it is available in every project — not just the folder where the command is run.

**Restart & Verify:**
- Close Claude Code entirely → Reopen
- Test: *"Can you check the health of my SQL database?"*

## **🌐 Claude API (Programmatic)**

```python
import anthropic
from mcp_client import MCPClient

# Start MCP server
mcp = MCPClient(server_path="./main.py")

# Use with Claude API
client = anthropic.Anthropic(api_key="your-key")
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": "How many active employees?"}],
    tools=mcp.get_tools()  # Pass MCP tools
)
```

## **🔧 VS Code (with MCP Extensions)**

```bash
# Install MCP extension for VS Code
code --install-extension mcp-integration

# Add to VS Code settings.json
{
  "mcp.servers": {
    "sql-bridge": {
      "command": "python",
      "args": ["/path/to/SQLBridgeMCP/main.py"],
      "env": {
        "DB_TYPE": "sqlserver",
        "CONNECTION_STRING": "your-connection-string"
      }
    }
  }
}
```

## **🤖 Other MCP-Compatible Clients**

**For any MCP client, use standard MCP protocol:**
```bash
# Start the server
python /path/to/SQLBridgeMCP/main.py

# The server exposes these MCP tools:
# - execute_sql_query
# - list_tables  
# - describe_table
# - database_health
# - list_all_databases
# - list_tables_from_database
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

## 🛠️ Troubleshooting

### **MCP Not Connecting?**
1. **Restart Claude Code completely** (close & reopen)
2. Check your `claude_desktop_config.json` syntax
3. Verify the path to `main.py` is correct (use full absolute path)
4. Ensure your `.env` file has correct credentials

### **Database Connection Issues?**
1. Test your CONNECTION_STRING/credentials outside MCP first
2. Check if your database server is running
3. Verify firewall/network access to database
4. Use individual variables if CONNECTION_STRING fails

### **Python/Dependencies Issues?**
```bash
# Verify Python and dependencies
python --version  # Should be 3.11+
pip install -r requirements.txt
python main.py  # Test server directly
```

### **Common Fixes:**
- **"No MCP icon"**: Restart Claude Code completely  
- **"Connection failed"**: Check database credentials
- **"Python not found"**: Use full path to python in config
- **"Module not found"**: Run `pip install -r requirements.txt`

## 🆘 Support

- **🐛 Issues**: Report problems via GitHub Issues  
- **💬 Questions**: Start a discussion in GitHub Discussions
- **📧 Direct support**: Check repository for contact info

## 🔗 Tested MCP Clients

| Platform | Setup Method | Status | Command |
|----------|-------------|---------|---------|
| **Claude Code** | `claude add mcp` | ✅ Verified | `claude add mcp sql-bridge --command python --args /path/main.py` |
| **Claude API** | Python SDK | ✅ Supported | Use `anthropic` library with MCP tools |
| **VS Code** | Extension | 🔄 Community | Install `mcp-integration` extension |
| **Custom Apps** | MCP Protocol | ✅ Standard | Implement MCP client specification |
| **OpenAI Compatible** | MCP Bridge | 🔄 Possible | Via MCP-to-OpenAI bridge tools |
| **Enterprise Tools** | Configuration | ✅ Flexible | Custom MCP client integration |

### **Quick Setup Commands:**

```bash
# Easiest (Windows): copy template, fill credentials, double-click
cp setup_mcp.example.bat setup_mcp.bat
# edit setup_mcp.bat with your credentials, then run it

# Manual test (any platform)
python /path/to/SQLBridgeMCP/main.py
```

---

**Built with ❤️ for the MCP community**

*SQLBridgeMCP - Your personal bridge between AI and your data*