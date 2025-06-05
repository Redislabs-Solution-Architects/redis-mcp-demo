"""
Redis Vector Search CLI - Interactive movie search using semantic embeddings
"""

import asyncio
import sys
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent
from config import REDIS_CONFIG, MCP_CONFIG, OPENAI_CONFIG, get_mcp_path
from embedding_tool import semantic_movie_search, get_movie_embeddings
from agent_instructions import MOVIE_SEARCH_AGENT_INSTRUCTIONS
from shared.mcp_utils import validate_environment, initialize_mcp_server


def initialize_embedding_model():
    """Load embedding model for semantic search"""
    print(" Initializing embedding model for semantic search...")
    get_movie_embeddings()


def create_movie_search_agent(server):
    """Create AI agent specialized for movie search"""
    return Agent(
        name="Movie Search AI",
        instructions=MOVIE_SEARCH_AGENT_INSTRUCTIONS,
        mcp_servers=[server],
        model=OPENAI_CONFIG["model"]
    )


def is_movie_search_query(user_input: str) -> bool:
    """Determine if user input is a movie search query"""
    movie_keywords = ["find", "show", "search", "want", "movies", "films", "movie", "film"]
    return any(keyword in user_input.lower() for keyword in movie_keywords)


def create_search_prompt(user_input: str) -> str:
    """Create enhanced prompt with vector search parameters"""
    search_params = semantic_movie_search(user_input, k=3)
    print(" Done: Converted to semantic search \n")

    return f"""User query: "{user_input}"

Perform semantic vector search using the vector_search_hash tool with these exact parameters:
- query_vector: {search_params['query_vector']}
- index_name: "{search_params['index_name']}"
- vector_field: "{search_params['vector_field']}"
- k: {search_params['k']}
- return_fields: {search_params['return_fields']} 

Return results quickly"""


async def handle_user_query(agent, user_input: str):
    """Process user query and return AI response"""
    if is_movie_search_query(user_input):
        prompt = create_search_prompt(user_input)
    else:
        prompt = user_input
    
    print(" Sending embeddeded vector to LLM \n")

    return Runner.run_streamed(agent, prompt)


async def print_streamed_response(result):
    """Print response"""
    print(" AI: ", end="")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print("\n")


def print_welcome_message():
    """ CLI welcome message and instructions"""
    print("\n ___Movie Vector Search CLI___")
    print("Ask me to find movies using natural language")
    print("Examples:")
    print("  - Find space adventure movies with aliens")
    print("  - Search for thriller movies about hackers")
    print("\nType 'exit' or 'quit' to exit.\n")


async def run_chat_loop(agent):
    """Main interactive chat loop"""
    print_welcome_message()
    
    while True:
        try:
            user_input = input(" You: ")
            
            if user_input.lower().strip() in ["exit", "quit", "q"]:
                break
                
            if not user_input.strip():
                continue
            
            result = await handle_user_query(agent, user_input)
            await print_streamed_response(result)
            
        except KeyboardInterrupt:
            print("\n bye")
            break
        except EOFError:
            break


async def main():
    """starting point"""
    mcp_path = get_mcp_path()
    
    if not validate_environment(mcp_path):
        return
    
    try:
        server = await initialize_mcp_server(
            command=MCP_CONFIG["command"],
            mcp_path=mcp_path,
            script_path="src/main.py",
            env_config=REDIS_CONFIG
        )
        initialize_embedding_model()
        agent = create_movie_search_agent(server)
        await run_chat_loop(agent)
        
    except Exception as e:
        print(f" Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())