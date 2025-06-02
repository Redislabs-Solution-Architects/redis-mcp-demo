# Redis MCP: The Transformation

## Traditional Redis Integration

**Code Required (without_mcp.py):**
```python
# 1. Import and setup Redis (6 lines)
import redis, json, openai
from datetime import datetime

redis_client = redis.Redis(
    host=REDIS_CONFIG['REDIS_HOST'],
    port=int(REDIS_CONFIG['REDIS_PORT']),
    password=REDIS_CONFIG['REDIS_PWD'],
    decode_responses=True
)

# 2. Write storage function
def store_message(role, content):
    message_data = {
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat()
    }
    redis_client.xadd('chat:history', {'data': json.dumps(message_data)})

# 3. Write retrieval function
def get_conversation_history():
    messages = redis_client.xrange('chat:history', '-', '+')
    history = []
    for msg_id, data in messages:
        message = json.loads(data['data'])
        history.append(f"{message['role']}: {message['content']}")
    return "\n".join(history[-20:])

# 4. Orchestrate everything manually
store_message("user", user_input)
history = get_conversation_history()
ai_response = chat_with_ai(user_input, history)
store_message("assistant", ai_response)
```
---

## After w/ Redis MCP

**Code Required (redis_mcp_showcase.py):**
```python
# 1. Connect to Redis MCP server
server = MCPServerStdio(params={...})
await server.connect()

# 2. Tell AI what to do in plain English
agent = Agent(
    name="Redis AI",
    instructions="Store all conversations in Redis.",
    mcp_servers=[server]
)

# 3. Just chat. Redis data operations abstracted away
result = Runner.run_streamed(agent, user_input)
```
