import asyncio
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent
from agents.mcp import MCPServerStdio
from collections import deque
from config import REDIS_CONFIG, MCP_CONFIG, OPENAI_CONFIG, get_mcp_path


async def build_agent():
    server = MCPServerStdio(
        params={
            "command": MCP_CONFIG["command"],
            "args": [
                "--directory", get_mcp_path(),
                "run", "main.py"
            ],
            "env": REDIS_CONFIG,
        }
    )

    await server.connect()
    agent = Agent(
        name="Redis Assistant",
        instructions="You are a helpful assistant capable of reading and writing to Redis. Store every question and answer in the Redis Stream app:logger and use the conversation history to answer questions.",
        description="An assistant that can read and write to Redis, using conversation history for context.",
        mcp_servers=[server],
        model=OPENAI_CONFIG["model"]
    )

    return agent


# CLI interaction
async def cli(agent, max_history=30):
    print(" Redis Assistant CLI — Ask me something (type 'exit' to quit):\n")
    conversation_history = deque(maxlen=max_history)

    while True:
        q = input("❓> ")
        if q.strip().lower() in {"exit", "quit"}:
            break

        if (len(q.strip()) > 0):
            # Format the context into a single string
            history = ""
            for turn in conversation_history:
                prefix = "User" if turn["role"] == "user" else "Assistant"
                history += f"{prefix}: {turn['content']}\n"

            context = f"Conversation history:\n{history.strip()}\nNew question:\n{q.strip()}"
            result = Runner.run_streamed(agent, context)

            response_text = ""
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    print(event.data.delta, end="", flush=True)
                    response_text += event.data.delta
            print("\n")

            # Add the user's message and the assistant's reply in history !!
            conversation_history.append({"role": "user", "content": q})
            conversation_history.append({"role": "assistant", "content": response_text})


# Main entry point
async def main():
    print(f" Connecting to Redis at {REDIS_CONFIG['REDIS_HOST']}:{REDIS_CONFIG['REDIS_PORT']}")
    print(f" Using MCP server from: {get_mcp_path()}\n")

    try:
        agent = await build_agent()
        await cli(agent)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())