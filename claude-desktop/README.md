# Redis Infrastructure Prototyping with Claude Desktop

**Rapidly prototype Redis infrastructure through conversation.** Create databases, run health checks, seed test data, and discover optimal patterns. All within a single ChatBot conversation.
**Value:**
- **Database setup:** "Create an e-commerce database" → Done in seconds
- **Health monitoring:** "Check my Redis Database" → Instant status reports  
- **Data seeding:** "Add 1000 realistic users" → No need to create time consuming scripts to simulate user data
- **Pattern discovery:** "What's the best structure for leaderboards?" → AI suggests optimal data storage and retrieval patterns


## What You Need
- Claude Desktop installed
- Redis Cloud Account

## Choose Your Setup
Pick what you want to demo:

| Setup | What It Does | Good For |
|-------|--------------|----------|
| **redis-mcp** | Control Redis data (get/set/lists/etc.) | Showing data operations, caching, queries |
| **redis-mcp-cloud** | Manage Redis Cloud (create/delete databases) | Showing database management, subscriptions |
| **Both** | Complete workflow | Creating databases then using them |

## Setup 1: Redis Data Operations (redis-mcp)

For demos focused on working with Redis data.

### Download and Install
```bash
git clone https://github.com/redis/mcp-redis.git
cd mcp-redis
uv venv
source .venv/bin/activate
uv sync
```

### Get Your Redis Info
1. Open [Redis Cloud Console](https://app.redislabs.com)
2. Click on your database
3. Copy the endpoint, port, and password

### Configure Claude Desktop
Find your config file:
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this (replace the placeholder values):
```json
{
  "mcpServers": {
    "redis-data-operations": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "--directory",
        "/Users/yourname/path/to/mcp-redis",
        "run",
        "src/main.py"
      ],
      "env": {
        "REDIS_HOST": "redis-12345.cloud.redislabs.com",
        "REDIS_PORT": "12345",
        "REDIS_PWD": "your_actual_password",
        "REDIS_SSL": "true"
      }
    }
  }
}
```

**Update these:**
- `/Users/yourname/path/to/mcp-redis` - where you cloned mcp-redis
- `/opt/homebrew/bin/uv` - run `which uv` to get the right path
- `redis-12345.cloud.redislabs.com` - your Redis endpoint
- `12345` - your Redis port
- `your_actual_password` - your Redis password

## Setup 2: Redis Cloud Management (redis-mcp-cloud)

For demos focused on creating and managing Redis databases.

### Download and Build
```bash
git clone https://github.com/redis/mcp-redis-cloud.git
cd mcp-redis-cloud
npm install
npm run build
```

### Get API Keys
1. Go to [Redis Cloud Console](https://app.redislabs.com)
2. Click your account name → Account Settings
3. Go to API Keys tab
4. Click "Generate API Key"
5. Save both the Account Key and User Key

### Configure Claude Desktop
Add this to your config file:
```json
{
  "mcpServers": {
    "redis-cloud-management": {
      "command": "node",
      "args": [
        "--experimental-fetch",
        "/Users/yourname/path/to/mcp-redis-cloud/dist/index.js"
      ],
      "env": {
        "API_KEY": "your_account_key_here",
        "SECRET_KEY": "your_user_key_here"
      }
    }
  }
}
```

**Update these:**
- `/Users/yourname/path/to/mcp-redis-cloud` - where you cloned mcp-redis-cloud
- `your_account_key_here` - your Account Key from Redis Cloud
- `your_user_key_here` - your User Key from Redis Cloud

## Setup 3: Both Together

For the full developer experience demo.

Follow both setups above, then combine the configs:
```json
{
  "mcpServers": {
    "redis-data-operations": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "--directory",
        "/Users/yourname/path/to/mcp-redis",
        "run",
        "src/main.py"
      ],
      "env": {
        "REDIS_HOST": "redis-12345.cloud.redislabs.com",
        "REDIS_PORT": "12345",
        "REDIS_PWD": "your_actual_password",
        "REDIS_SSL": "true"
      }
    },
    "redis-cloud-management": {
      "command": "node",
      "args": [
        "--experimental-fetch",
        "/Users/yourname/path/to/mcp-redis-cloud/dist/index.js"
      ],
      "env": {
        "API_KEY": "your_account_key_here",
        "SECRET_KEY": "your_user_key_here"
      }
    }
  }
}
```

## Test Everything Works

1. Quit Claude Desktop completely!
2. Start it again
3. Open a new chat
4. Try these:

**Test redis-mcp:**
```
Can you connect to Redis?
```

**Test redis-mcp-cloud:**
```
Show me my Redis Cloud account info
```

**Test both:**
```
What Redis capabilities do you have?
```

Claude should respond with what it can do, not error messages.

## Ready to Demo

Once this is working, check out [demo-prompts.md](demo-prompts.md) for commands you can copy-paste to show off Redis MCP.