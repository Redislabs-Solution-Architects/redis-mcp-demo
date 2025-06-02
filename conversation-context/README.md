# Conversation Context Demo

This demo shows how LLMs can directly read and write Redis data through natural language using MCP

## Simple Example of What It Does

- **LLM stores data:** Tell the AI "My name is Yusuf, I like to eat Oranges". it writes to Redis automatically
- **LLM retrieves data:** Ask "What's my name?". it reads from Redis and answers
- **Data persists:** Close the app, restart, ask again. data survives in Redis
- **Watch it happen:** Use RedisInsight to see Redis data updating in real-time

## Demo Files

- `redis_mcp_showcase.py` - LLM with Redis MCP (simple)
- `without_mcp.py` - Traditional Redis integration (complex)

## Setup Instructions

### 1. Get Redis Cloud Database (Free)
- Go to https://app.redislabs.com
- Create account and new database
- Copy: endpoint, port, password

### 2. Get OpenAI API Key
- Go to https://platform.openai.com/api-keys
- Create new API key -> Ensure you have credit 

### 3. Clone Redis MCP Server
```bash
git clone https://github.com/redis/mcp-redis.git
cd mcp-redis
uv venv && source .venv/bin/activate && uv sync
```

### 4. Configure Demo
```bash
cd redis-mcp-demo/conversation-context
cp config.py.example config.py
# Edit config.py - add your Redis credentials and MCP path
```

### 5. Run Demo (2 Terminals)

**Terminal 1** - Start MCP Server:
```bash
cd /path/to/mcp-redis
REDIS_HOST=your-endpoint REDIS_PORT=12345 REDIS_PWD=your-password uv run src/main.py
```

**Terminal 2** - Run Demo:
```bash
cd conversation-context
export OPENAI_API_KEY=your-key
pip install -r requirements.txt
python3 redis_mcp_showcase.py
```

## Quick Test

1. Say: "I like pizza"
2. **It remembers!** Check RedisInsight to see the Redis data.
3. Exit and restart
4. Ask: "What do I like?"

## Key Insight

**Without MCP:** Developers write Redis connection code, serialization, error handling.
**With MCP:** LLM handles all Redis operations through conversation. This enables any LLM application to have persistent memory powered by Redis with zero database code.