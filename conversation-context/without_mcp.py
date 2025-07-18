import redis
import json
import openai
from datetime import datetime
from config import REDIS_CONFIG, OPENAI_CONFIG

redis_client = redis.Redis(
    host=REDIS_CONFIG['REDIS_HOST'],
    port=int(REDIS_CONFIG['REDIS_PORT']),
    password=REDIS_CONFIG['REDIS_PWD'],
    decode_responses=True
)

client = openai.OpenAI()

# the function to store messages in Redis stream
def store_message(role, content):
    message_data = {
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat()
    }
    # Add message to Redis stream
    redis_client.xadd('chat:history', {'data': json.dumps(message_data)})


# function to retrieve conversation history from Redis
def get_conversation_history():
    messages = redis_client.xrange('chat:history', '-', '+')
    history = []
    
    for msg_id, data in messages:
        message = json.loads(data['data'])
        history.append(f"{message['role']}: {message['content']}")
    # Return the last 20 messages for LLM context, from redis stream
    return "\n".join(history[-20:])  

### function to send user input to OpenAI and get a response
def chat_with_ai(user_input, history):
    messages = [
        {"role": "system",
          "content": "You are a helpful assistant. Use the conversation history for context."},
        {"role": "user", 
         "content": f"Conversation history:\n{history}\n\nUser: {user_input}"}
    ]
    
    response = client.chat.completions.create(
        model=OPENAI_CONFIG["model"],
        messages=messages
    )
    return response.choices[0].message.content

def main():
    print(" Non-MCP Redis Demo.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        store_message("user", user_input)

        history = get_conversation_history()

        ai_response = chat_with_ai(user_input, history)

        store_message("assistant", ai_response)

        print(f"AI: {ai_response}\n")


if __name__ == "__main__":
    main()