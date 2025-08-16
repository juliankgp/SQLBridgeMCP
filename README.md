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

### 2. **Configure your database**
```bash
cp .env.example .env
# Edit .env with YOUR database credentials
```

### 3. **Connect to Claude Code**
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "sql-bridge": {
      "command": "python",
      "args": ["/path/to/SQLBridgeMCP/main.py"],
      "env": {
        "DB_TYPE": "postgresql",
        "DB_HOST": "your-server",
        "DB_NAME": "your-database"
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

## 📖 Available Tools

Your AI can use these tools to interact with your database:

- **`execute_sql_query`** - Run SELECT queries safely
- **`list_tables`** - See available tables
- **`describe_table`** - Get table schema and sample data
- **`database_health`** - Check connection status

## 🚀 Advanced Usage

### Custom Applications
```python
from mcp import MCPClient

client = MCPClient(server_path="./main.py")
result = await client.call_tool("execute_sql_query", {
    "query": "SELECT COUNT(*) FROM orders WHERE date > '2024-01-01'"
})
```

### Multiple Databases
Configure different MCP servers for different databases in your Claude Code config.

### Production Deployment
- Use Docker for containerization
- Configure SSL for database connections
- Set up monitoring and logging
- Create read-only database users

## 📋 Configuration Examples

### PostgreSQL
```bash
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=myuser
DB_PASSWORD=mypass
```

### MySQL
```bash
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mydb
DB_USER=myuser
DB_PASSWORD=mypass
```

### SQLite (local file)
```bash
DB_TYPE=sqlite
DB_NAME=/path/to/database.db
```

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