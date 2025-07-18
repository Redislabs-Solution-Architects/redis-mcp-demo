# Redis Vector Search CLI

Natural language movie search powered by Redis vector embeddings and MCP (Model Context Protocol).

## Loading Movie Data

To load the movie dataset into Redis with vector search:
1. Clone the Redis Search Showcase repository:
   ```bash
   git clone https://github.com/Redislabs-Solution-Architects/redis-search-showcase
   cd redis-search-showcase
   ```
2. Run the setup script and choose **Flow 2** when prompted:
   ```bash
   python3 run.py setup
   ```


## Setup Instructions

### 1. Get Redis Cloud Database (Free)
- Go to https://app.redislabs.com
- Create account and new database
- Copy: endpoint, port, password

### 2. Get OpenAI API Key
- Go to https://platform.openai.com/api-keys
- Create new API key -> Ensure you have credit 

### 3. Clone Redis MCP Server
In order to connect to Redis, an MCP Server needs to be downloaded and running. The following commands download the MCP Redis Server Repo. In Step 5, you will begin running the server. 

```bash
git clone https://github.com/redis/mcp-redis.git
cd mcp-redis
uv venv && source .venv/bin/activate && uv sync
```

### 4. Load Data

To load the movie dataset into Redis with vector search:
1. Clone the Redis Search Showcase repository:
   ```bash
   git clone https://github.com/Redislabs-Solution-Architects/redis-search-showcase
   cd redis-search-showcase
   ```
2. Run the setup script and choose **Flow 2** when prompted:
   ```bash
   python3 run.py setup
   ```


### 5. Configure Demo
Update `config.py`:
```python
MCP_CONFIG = {
    "command": "/opt/homebrew/bin/uv",  # Result of: which uv
    "mcp_redis_path": "/path/to/mcp-redis"  # Update this path
}
```
### 6. Run Demo (2 Terminals)

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
python3 vector_search_cli.py
```

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