# Redis MCP Conversation Demo

Shows how to use Redis with MCP (Model Context Protocol) for conversation storage. No Redis commands needed - just talk to the AI and it handles Redis operations automatically.

## What You Need

- Redis Cloud database (free tier works)
- OpenAI API key with billing enabled
- Python 3.8+
- uv package manager

## Setup

Clone the Redis MCP server:
```bash
git clone https://github.com/redis/mcp-redis.git
cd mcp-redis
uv venv && source .venv/bin/activate && uv sync
```

Get Redis Cloud credentials:
1. Create database at https://app.redislabs.com
2. Copy endpoint, port, password

Get OpenAI API key:
1. Get key from https://platform.openai.com/api-keys
2. Add billing at https://platform.openai.com/account/billing

Configure the demo:
```bash
cd redis-mcp-demo/conversation-context
cp config.py.example config.py
# Edit config.py with your Redis and path details
# Optionally change the OpenAI model (default: gpt-4o-mini)
```

## Run the Demo

Terminal 1 - Start Redis MCP server:
```bash
cd /path/to/mcp-redis
REDIS_HOST=your-endpoint REDIS_PORT=12345 REDIS_PWD=your-password uv run src/main.py
```

Terminal 2 - Run the assistant:
```bash
cd redis-mcp-demo/conversation-context
export OPENAI_API_KEY=your_key
python3 -m pip install -r requirements.txt
python redis_assistant.py
```

## Demo Commands

Try these in order:

**Test connection:**
```
❓> ping
```

**Store data:**
```
❓> Store my name as "John" with key "user:name"
```

**Get data:**
```
❓> Get the value for key "user:name"
```

**Create hash:**
```
❓> Create a user profile hash with name="John", role="Developer", location="SF"
```

**Make a list:**
```
❓> Create a list called "languages" with Python, JavaScript, Go
```

**Check conversation log:**
```
❓> What's in the app:logger stream?
```

**Complex query:**
```
❓> Get my profile and languages, then suggest what I should build next
```

## What This Shows

- Store and retrieve Redis data through conversation
- AI automatically logs all interactions to Redis streams
- No Redis expertise needed - just describe what you want
- Same Redis functionality, way easier to use

## Files

- `redis_assistant.py` - Main demo code
- `config.py.example` - Configuration template  
- `requirements.txt` - Dependencies

## Architecture

```
You type → AI Agent → MCP Server → Redis Cloud
```

The AI handles all Redis operations automatically. You just tell it what you want in plain English.