"""
Main entry point for SQL MCP server
This file starts the server and connects it with Claude Code
"""
import asyncio
import sys
import os

# Add src to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from server import create_mcp_server

def main():
    """
    Main function that starts the MCP server
    """
    # Create the MCP server
    server = create_mcp_server()
    
    # Start the server directly (FastMCP handles asyncio internally)
    print("Starting MCP server for SQL...")
    server.run()

if __name__ == "__main__":
    # Run the main function directly
    main()