"""
Aibolit AI Medical Clinic — Startup script.

Usage:
    python run.py

This script ensures correct module resolution regardless of
working directory or OS. Use it in Claude Desktop MCP config:

    {
      "mcpServers": {
        "aibolit-clinic": {
          "command": "python",
          "args": ["C:\\path\\to\\aibolit-claude\\run.py"]
        }
      }
    }
"""
import sys
import os

# Ensure the project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.mcp_server import main

if __name__ == "__main__":
    main()
