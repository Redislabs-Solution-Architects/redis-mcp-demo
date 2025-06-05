"""
Shared MCP utilities for Redis MCP server initialization and validation
"""

import os
from agents.mcp import MCPServerStdio


def validate_environment(mcp_path: str) -> bool:
    """Validate required environment and MCP server path
    
    Args:
        mcp_path: Path to the MCP server directory
        
    Returns:
        bool: True if environment is valid, False otherwise
    """
    if not os.path.exists(mcp_path):
        print(f" Error: MCP Redis path not found: {mcp_path}")
        print("Please update the mcp_redis_path in config.py")
        return False
    return True


async def initialize_mcp_server(command: str, mcp_path: str, script_path: str, env_config: dict):
    """Initialize and connect to Redis MCP server
    
    Args:
        command: Command to run (e.g., "/opt/homebrew/bin/uv")
        mcp_path: Path to MCP server directory
        script_path: Script path relative to mcp_path (e.g., "src/main.py" or "main.py")
        env_config: Environment configuration dictionary
        
    Returns:
        MCPServerStdio: Connected MCP server instance
    """
    print(f" Connecting to Redis MCP server at: {mcp_path}")
    
    server = MCPServerStdio(
        params={
            "command": command,
            "args": ["--directory", mcp_path, "run", script_path],
            "env": env_config,
        }
    )
    await server.connect()
    return server