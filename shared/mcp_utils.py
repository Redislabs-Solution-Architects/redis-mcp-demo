"""
Shared MCP utilities for Redis MCP server init and validation
"""

import os
from agents.mcp import MCPServerStdio


def validate_environment(mcp_path: str) -> bool:
   
    if not os.path.exists(mcp_path):
        print(f" Error: MCP Redis path not found: {mcp_path}")
        print("Please update the mcp_redis_path in config.py")
        return False
    return True


async def initialize_mcp_server(command: str, mcp_path: str, script_path: str, env_config: dict):
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