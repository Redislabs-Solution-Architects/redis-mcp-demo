import asyncio
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent
from agents.mcp import MCPServerStdio
from config import REDIS_CONFIG, MCP_CONFIG, OPENAI_CONFIG, get_mcp_path


async def main():
    # connect to the MCP server
    server = MCPServerStdio(
        params={
            "command": MCP_CONFIG["command"],
            "args": ["--directory", get_mcp_path(), "run", "main.py"],
            "env": REDIS_CONFIG,
        }
    )
    await server.connect()
    
    # use OpenAI Agent with Redis MCP
    agent = Agent(
        name="Redis AI",
        instructions="You have persistent memory powered by Redis. Store all conversations in the Redis stream 'chat:history' and retrieve from it when answering questions.",
        mcp_servers=[server],
        model=OPENAI_CONFIG["model"]
    )
    
    print("Redis MCP Demo\n")
    
    while True:     # chatbot loop
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        # runner for orchestrating the agent
        result = Runner.run_streamed(agent, user_input)
        
        # Print response
        print("AI: ", end="")
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())