# Shared MCP Utilities Usage

## For vector-search-mcp

```python
from shared.mcp_utils import validate_environment, initialize_mcp_server

# Usage in vector-search-mcp
mcp_path = get_mcp_path()
if not validate_environment(mcp_path):
    return

server = await initialize_mcp_server(
    command=MCP_CONFIG["command"],
    mcp_path=mcp_path,
    script_path="src/main.py",  # vector-search uses src/main.py
    env_config=REDIS_CONFIG
)
```

## For conversation-context (example refactor)

```python
from shared.mcp_utils import validate_environment, initialize_mcp_server

# Usage in conversation-context
mcp_path = get_mcp_path()
if not validate_environment(mcp_path):
    return

server = await initialize_mcp_server(
    command=MCP_CONFIG["command"],
    mcp_path=mcp_path,
    script_path="main.py",  # conversation-context uses main.py
    env_config=REDIS_CONFIG
)
```

## Benefits

- **DRY Principle**: No duplicate MCP initialization code
- **Consistency**: Same validation and error handling across projects
- **Maintainability**: Single place to update MCP connection logic
- **Flexibility**: Parameterized for different script paths and configurations