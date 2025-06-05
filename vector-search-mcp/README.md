# Redis Vector Search CLI

Natural language movie search powered by Redis vector embeddings and MCP (Model Context Protocol).

## Prerequisites
- Redis database with movie data and vector embeddings
- OpenAI API key
- [mcp-redis](https://github.com/redis/mcp-redis) cloned locally

## Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY=your_openai_api_key

# Update config.py with your mcp-redis path
# Edit MCP_CONFIG["mcp_redis_path"] in config.py

# Run the CLI
python3 vector_search_cli.py
```

## Configuration

Update `config.py`:
```python
MCP_CONFIG = {
    "command": "/opt/homebrew/bin/uv",  # Result of: which uv
    "mcp_redis_path": "/path/to/mcp-redis"  # Update this path
}
```

Redis connection details are pre-configured for the demo database.

## Usage

```
 You: Find space adventure movies with aliens
 AI: Here are some great space adventure films featuring aliens...

 You: Show me romantic comedies set in Paris
 AI: I found several romantic comedies set in Paris...
```

Example queries:
- "Find movies about time travel"
- "Search for films similar to Blade Runner"

Type `exit` or `quit` to close.

## How It Works

1. **MCP Connection**: Connects to Redis through MCP server
2. **AI Agent**: OpenAI interprets natural language queries
3. **Vector Search**: Redis performs semantic search on movie embeddings
4. **Natural Response**: AI formats results conversationally

The CLI demonstrates natural language interaction with Redis vector search without writing complex queries.