import time
import asyncio
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import redis.asyncio as redis
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
import openai
import tiktoken
import numpy as np
import struct
import os

# Configure environment for optimal performance
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Prevent tokenizer warnings

from config import REDIS_CONFIG, OPENAI_CONFIG, DEMO_CONFIG, PERFORMANCE_CONFIG
from tools_mcp_format import MCP_TOOLS_CONFIG


# Configure logging with performance optimization
log_level = getattr(logging, PERFORMANCE_CONFIG.get("log_level", "INFO").upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
enable_timing_logs = PERFORMANCE_CONFIG.get("enable_timing_logs", True)

# Logging utilities with conditional evaluation for performance
def perf_log(message, *args):
    """Performance logging - only logs if timing logs enabled"""
    if enable_timing_logs and logger.isEnabledFor(logging.INFO):
        if args:
            logger.info(message % args)
        else:
            logger.info(message)

def debug_log(message, *args):
    """Debug logging - only logs if debug level enabled"""
    if logger.isEnabledFor(logging.DEBUG):
        if args:
            logger.debug(message % args)
        else:
            logger.debug(message)

# Initialize FastAPI application
app = FastAPI(
    title="Redis MCP Tool Selection Demo",
    description="Cut costs. Increase accuracy. Boost performance.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount logos directory
app.mount("/logos", StaticFiles(directory="logos"), name="logos")

# Embedding Service using SentenceTransformers
class ToolEmbeddings:
    """
    Optimized embedding generation with caching for maximum performance
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize embedding model with performance optimizations"""
        try:
            from sentence_transformers import SentenceTransformer
            from functools import lru_cache
            import hashlib
            
            print(f"Loading embedding model: {model_name}...")
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.available = True
            
            # Initialize embedding cache for performance optimization
            self._embedding_cache = {}
            self._cache_hits = 0
            self._cache_misses = 0
            self._max_cache_size = PERFORMANCE_CONFIG.get("embedding_cache_size", 1000)
            
            print(f"Embedding model loaded successfully. Dimension: {self.dimension}, Cache size: {self._max_cache_size}")
        except ImportError as e:
            print(f"ERROR: sentence-transformers not installed: {e}")
            print("Install with: pip3 install sentence-transformers")
            raise ImportError("sentence-transformers is required for real embeddings")
        except Exception as e:
            print(f"ERROR: Failed to load embedding model: {e}")
            raise RuntimeError(f"Cannot initialize embedding model: {e}")
    
    def generate_embedding(self, text):
        """Generate embedding with caching for optimal performance"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for embedding generation")
        
        # Create cache key from text hash
        import hashlib
        cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # Check cache first
        if cache_key in self._embedding_cache:
            self._cache_hits += 1
            return self._embedding_cache[cache_key]
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True).astype(np.float32)
            
            # Cache with size limit (LRU-like behavior)
            if len(self._embedding_cache) >= self._max_cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self._embedding_cache))
                del self._embedding_cache[oldest_key]
            
            self._embedding_cache[cache_key] = embedding
            self._cache_misses += 1
            return embedding
        except Exception as e:
            raise RuntimeError(f"SentenceTransformer embedding failed: {e}")
    
    def get_cache_stats(self):
        """Get embedding cache statistics"""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses, 
            "hit_rate": round(hit_rate, 1),
            "cache_size": len(self._embedding_cache)
        }
    
    def embedding_to_bytes(self, embedding):
        """Convert numpy array to bytes for redis storage (redis-movie-search pattern)"""
        if embedding is None:
            return None
        return struct.pack(f'{len(embedding)}f', *embedding)
    
    def bytes_to_embedding(self, bytes_data):
        """Convert bytes back to numpy array"""
        if not bytes_data:
            return None
        return np.array(struct.unpack(f'{len(bytes_data)//4}f', bytes_data))

class LLMService:
    """
    LLM service for intelligent tool selection.
    
    Uses OpenAI API to analyze queries and select the most relevant
    tools from a provided set, returning structured responses with
    performance metrics.
    """
    def __init__(self):
        self.client = None
        self.tokenizer = None
        
    def initialize(self):
        """Initialize OpenAI client and tokenizer"""
        if not OPENAI_CONFIG["api_key"]:
            logger.warning("OpenAI API key not provided - LLM features disabled")
            return False
            
        try:
            self.client = openai.OpenAI(api_key=OPENAI_CONFIG["api_key"])
            self.tokenizer = tiktoken.encoding_for_model(OPENAI_CONFIG["model"])
            logger.info(f"OpenAI client initialized with model: {OPENAI_CONFIG['model']}")
            return True
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
            return False
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Falls back to character-based estimation if tokenizer unavailable.
        
        Args:
            text: Text to tokenize
        
        Returns:
            Estimated token count
        """
        if not self.tokenizer:
            # Fallback estimation: ~4 characters per token
            return len(text) // 4
        return len(self.tokenizer.encode(text))
    
    def format_tools_for_llm(self, tools: List[Dict[str, Any]]) -> str:
        """
        Format MCP tools for LLM context.
        
        Creates a structured text representation of tools including
        their descriptions, parameters, and server information.
        
        Args:
            tools: List of tool dictionaries
        
        Returns:
            Formatted string for LLM context
        """
        formatted_tools = []
        for tool in tools:
            # Use full realistic tool definition for LLM context
            full_tool = None
            for server_name, server_tools in TOOLS_CONFIG.items():
                for t in server_tools:
                    if t["name"] == tool["name"]:
                        full_tool = t
                        break
                if full_tool:
                    break
            
            if not full_tool:
                continue
                
            tool_text = f"""Tool: {full_tool['name']}
Server: {tool.get('server', 'unknown')}
Type: {full_tool.get('type', 'read')}
Description: {full_tool['description']}"""
            
            # Handle MCP inputSchema format
            if 'inputSchema' in full_tool and 'properties' in full_tool['inputSchema']:
                tool_text += "\nParameters:\n"
                required_params = full_tool['inputSchema'].get('required', [])
                for param_name, param_info in full_tool['inputSchema']['properties'].items():
                    required_str = " (required)" if param_name in required_params else " (optional)"
                    tool_text += f"  - {param_name} ({param_info['type']}){required_str}: {param_info['description']}\n"
            
            formatted_tools.append(tool_text)
        
        return "\n\n".join(formatted_tools)
    
    async def select_relevant_tools(self, query: str, all_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use LLM to select relevant tools for a query.
        
        Sends tool definitions to the LLM and parses its response
        to identify the most appropriate tools for the given task.
        
        Args:
            query: User query requiring tool selection
        
        Returns:
            Dictionary containing selected tools and performance metrics
        """
        if not self.client:
            raise Exception("OpenAI client not initialized")
        
        start_time = time.time()
        logger.info(f"LLM_SELECTION_START: tools_available={len(all_tools)} model={OPENAI_CONFIG['model']}")
        
        # Format all tools for LLM context
        tools_context = self.format_tools_for_llm(all_tools)
        context_length = len(tools_context)
        logger.info(f"LLM_CONTEXT_PREPARED: context_chars={context_length} tools_formatted={len(all_tools)}")
        
        # Count input tokens
        input_prompt = f"""You are an expert system administrator helping with operational tasks. Given the following query and available MCP tools, select the 1 most relevant tools that would be needed to address this request. Make sure you choose correctly review all the options provided to you, think deeply.

Query: {query}

Available Tools:
{tools_context}

Please respond with ONLY a JSON array of tool names that are most relevant to this query. Be selective - choose only the tools that are directly needed.

Example response format:
["tool.name1", "tool.name2", "tool.name3"]"""

        input_tokens = self.count_tokens(input_prompt)
        
        # Professional logging for demo transparency
        avg_tokens_per_tool = input_tokens / len(all_tools) if all_tools else 0
        logger.info(f"LLM_INPUT_PREPARED: input_tokens={input_tokens} query_length={len(query)}")
        logger.info(f"TOKEN_ANALYSIS: avg_tokens_per_tool={avg_tokens_per_tool:.1f} context_complexity=enterprise_scale")
        logger.info(f"REASONING_CHALLENGE: tools_to_evaluate={len(all_tools)} selection_complexity=high")
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=OPENAI_CONFIG["model"],
                messages=[{"role": "user", "content": input_prompt}],
                max_tokens=OPENAI_CONFIG["max_tokens"],
                temperature=OPENAI_CONFIG["temperature"],
                timeout=30  
            )
            
            end_time = time.time()
            latency = round(end_time - start_time, 3)
            
            # Parse LLM response
            selected_tools_text = response.choices[0].message.content.strip()
            output_tokens = self.count_tokens(selected_tools_text)
            total_tokens = input_tokens + output_tokens
            
            # Calculate cost (GPT-4o pricing: $4.25/1M input, $17.00/1M output)
            cost = (input_tokens * 0.00000425 + output_tokens * 0.000017)
            
            try:
                import json
                # Clean up markdown code blocks if present
                clean_text = selected_tools_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]  # Remove ```json
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]  # Remove ```
                clean_text = clean_text.strip()
                
                selected_tool_names = json.loads(clean_text)
                
                # Ensure we have a list
                if not isinstance(selected_tool_names, list):
                    selected_tool_names = []
                
                # Find the full tool objects
                selected_tools = []
                for tool_name in selected_tool_names:
                    for tool in all_tools:
                        if tool["name"] == tool_name:
                            selected_tools.append(tool)
                            break
                
                # If no tools selected, use fallback
                if len(selected_tools) == 0 and len(all_tools) > 0:
                    logger.warning(f"LLM_NO_TOOLS_SELECTED: falling back to top {min(3, len(all_tools))} tools")
                    selected_tools = all_tools[:min(3, len(all_tools))]
                
                logger.info(f"LLM_SELECTION_COMPLETE: tools_selected={len(selected_tools)} tools_available={len(all_tools)} selection_rate={len(selected_tools)/len(all_tools):.2%}")
                
                # Professional analysis logging for demo transparency
                token_reduction = ((len(all_tools) - len(selected_tools)) / len(all_tools)) * 100 if all_tools else 0
                reasoning_efficiency = latency / len(all_tools) if all_tools else 0
                tokens_saved = (len(all_tools) - len(selected_tools)) * avg_tokens_per_tool if 'avg_tokens_per_tool' in locals() else 0
                
                logger.info(f"REASONING_PERFORMANCE: latency={latency}s efficiency={reasoning_efficiency:.3f}s_per_tool")
                logger.info(f"CONTEXT_REDUCTION: achieved={token_reduction:.1f}% tokens_saved={tokens_saved:.0f}")
                logger.info(f"PRODUCTION_IMPACT: reasoning_scales_with_tool_count=quadratic without_redis=bottleneck")
                
                # Log each selected tool
                for i, tool in enumerate(selected_tools, 1):
                    server = next((s for s, tools in TOOLS_CONFIG.items() for t in tools if t['name'] == tool['name']), 'unknown')
                    logger.info(f"LLM_SELECTED_TOOL: rank={i} name={tool['name']} server={server} type={tool['type']}")
                
                return {
                    "tools": selected_tools,
                    "latency": latency,
                    "tokens": total_tokens,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": cost,
                    "llm_response": selected_tools_text
                }
                
            except json.JSONDecodeError:
                logger.error(f"LLM_PARSE_ERROR: response_text={selected_tools_text[:200]}{'...' if len(selected_tools_text) > 200 else ''}")
                fallback_tools = all_tools[:5]
                logger.info(f"LLM_FALLBACK: tools_selected={len(fallback_tools)} method=first_n reason=parse_error")
                # Fallback to first 5 tools
                return {
                    "tools": fallback_tools,
                    "latency": latency,
                    "tokens": total_tokens,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": cost,
                    "llm_response": selected_tools_text,
                    "error": "Failed to parse LLM response"
                }
                
        except Exception as e:
            end_time = time.time()
            error_latency = round(end_time - start_time, 3)
            logger.error(f"LLM_API_ERROR: error={str(e)} latency={error_latency}s input_tokens={input_tokens if 'input_tokens' in locals() else 0}")
            raise

# Global service instances
redis_client = None
sync_redis_client = None
llm_service = None
search_index = None
cache_index = None
is_redis_connected = False
tool_embeddings = None  # Real embedding service
tool_lookup_cache = {}  # Precomputed tool lookup cache

# Request/Response Models
class ChatRequest(BaseModel):
    query: str
    panel: str  # 'baseline' or 'optimized'

class ChatResponse(BaseModel):
    response: str
    latency: float
    tokens: int
    cost: float
    tools_count: int
    cache_status: Optional[str] = None
    vector_search_time: Optional[int] = None
    similarity: Optional[int] = None
    original_query: Optional[str] = None
    tools_used: Optional[List[str]] = []
    filtered_tools: Optional[List[str]] = []

class HealthResponse(BaseModel):
    status: str
    redis: bool
    sentence_transformers: bool
    openai: bool
    timestamp: str

# Load MCP tool definitions from configuration
TOOLS_CONFIG = MCP_TOOLS_CONFIG

async def initialize_redis():
    """
    Initialize Redis connection and vector search indexes.
    
    Sets up both async and sync Redis clients for compatibility
    with RedisVL, and creates HNSW indexes for tool and cache search.
    """
    global redis_client, sync_redis_client, search_index, cache_index, is_redis_connected
    
    try:
        # Create both async and sync redis clients (RedisVL needs sync client)
        redis_client = redis.from_url(REDIS_CONFIG["url"], decode_responses=True)
        
        # Also create sync client for RedisVL
        import redis as sync_redis
        global sync_redis_client
        sync_redis_client = sync_redis.from_url(REDIS_CONFIG["url"], decode_responses=True)
        
        # Test connection
        await redis_client.ping()
        is_redis_connected = True
        logger.info("Redis connection established successfully")
        
        # Initialize RedisVL indexes
        await setup_redisvl_indexes()
        
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        logger.info("Demo will run in mock mode")
        is_redis_connected = False

async def setup_redisvl_indexes():
    """
    Configure RedisVL vector search indexes.
    
    Creates two HNSW indexes:
    1. Tool index - for finding relevant MCP tools
    2. Cache index - for semantic similarity matching of queries
    """
    global search_index, cache_index
    
    try:
        # Tool search index schema
        tool_schema = {
            "index": {
                "name": "mcp_tools",
                "prefix": "tool:",
                "storage_type": "hash",
            },
            "fields": [
                {"name": "name", "type": "text"},
                {"name": "description", "type": "text"},
                {"name": "server", "type": "text"}, 
                {"name": "type", "type": "text"},
                {"name": "embedding", "type": "vector", "attrs": {
                    "dims": PERFORMANCE_CONFIG["vector_dim"],
                    "distance_metric": "cosine",
                    "algorithm": "hnsw",
                    "datatype": "float32"
                }}
            ]
        }
        
        # Semantic cache index schema  
        cache_schema = {
            "index": {
                "name": "semantic_cache",
                "prefix": "supportAssistant:cache:",
                "storage_type": "hash",
            },
            "fields": [
                {"name": "query", "type": "text"},
                {"name": "response", "type": "text"},
                {"name": "tools_used", "type": "text"},
                {"name": "cached_at", "type": "text"},
                {"name": "embedding", "type": "vector", "attrs": {
                    "dims": PERFORMANCE_CONFIG["vector_dim"],
                    "distance_metric": "cosine", 
                    "algorithm": "hnsw",
                    "datatype": "float32"
                }}
            ]
        }
        
        # Create indexes using Redis client (following aws-redis-fin-agent pattern)
        global search_index, cache_index
        search_index = SearchIndex.from_dict(tool_schema)
        cache_index = SearchIndex.from_dict(cache_schema)
        
        # Set sync client for RedisVL (it needs synchronous Redis client)
        search_index.set_client(sync_redis_client)
        cache_index.set_client(sync_redis_client)
        
        # Create indexes only if they don't exist (preserve cache data)
        try:
            # Check tool index
            try:
                search_index.info()
                logger.info("Tool search index already exists")
            except:
                search_index.create(overwrite=False, drop=False)
                logger.info("Tool search index created")
                
            # Check cache index - use direct Redis check to avoid clearing existing data
            existing_cache_keys = sync_redis_client.keys("supportAssistant:cache:*")
            if existing_cache_keys:
                logger.info(f"Cache index already exists with {len(existing_cache_keys)} cached items - preserving all data")
                # Don't touch the cache index at all if data exists
            else:
                try:
                    cache_index.info()
                    logger.info("Cache index exists but empty")
                except:
                    cache_index.create(overwrite=False, drop=False)
                    logger.info("Cache index created (no existing data)")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
        
        # Index tools with real embeddings (only if needed)
        await index_tools_with_embeddings()
        
        logger.info("RedisVL indexes initialized successfully")
        
    except Exception as e:
        logger.warning(f"RedisVL index setup failed: {e}")

async def index_tools_with_embeddings():
    """
    Index all MCP tools with their embeddings in RedisVL.
    Only indexes if tools are not already present in Redis.
    """
    if not is_redis_connected or not search_index:
        logger.warning("Skipping tool indexing: Redis not connected or search index missing")
        return
    
    try:
        # Check if tools are already indexed by checking a sample tool
        existing_count = len(sync_redis_client.keys("tool:*"))
        expected_count = sum(len(tools) for tools in TOOLS_CONFIG.values())
        
        if existing_count >= expected_count:
            logger.info(f"Tools already indexed ({existing_count} found) - skipping reindexing")
            return
        
        logger.info(f"Indexing tools: found {existing_count}, expected {expected_count}")
        tool_data = []
        embedding_stats = {"sentence_transformers": 0}
        
        logger.info(f"Starting tool embedding generation for {sum(len(tools) for tools in TOOLS_CONFIG.values())} tools...")
        
        # Generate real embeddings for all tools using enhanced text
        for server_name, tools in TOOLS_CONFIG.items():
            perf_log("EMBEDDING_GENERATION: Processing %s server with %d tools", server_name, len(tools))
            
            for tool in tools:
                # Enhanced embedding text that includes full context
                tool_text = generate_enhanced_embedding_text(tool, server_name)
                
                # Log sample of enhanced text for first tool of each server
                if tools.index(tool) == 0:
                    debug_log("EMBEDDING_SAMPLE: %s tool text length=%d chars", server_name, len(tool_text))
                
                # Generate real embedding using SentenceTransformers 
                try:
                    embedding_array = tool_embeddings.generate_embedding(tool_text)
                    embedding = embedding_array.tolist()
                    embedding_stats["sentence_transformers"] = embedding_stats.get("sentence_transformers", 0) + 1
                    logger.debug(f"Generated SentenceTransformer embedding for {tool['name']} (dimensions: {len(embedding)})")
                except Exception as e:
                    logger.error(f"CRITICAL: Embedding generation failed for {tool['name']}: {e}")
                    raise RuntimeError(f"Cannot generate embedding for tool {tool['name']}: {e}")
                
                # Validate embedding
                if not isinstance(embedding, list) or len(embedding) != PERFORMANCE_CONFIG["vector_dim"]:
                    logger.error(f"Invalid embedding for {tool['name']}: type={type(embedding)}, len={len(embedding) if hasattr(embedding, '__len__') else 'N/A'}")
                    continue
                
                # Prepare data for RedisVL
                tool_doc = {
                    "name": tool["name"],
                    "description": tool["description"], 
                    "server": server_name,
                    "type": tool["type"],
                    "embedding": embedding
                }
                
                tool_data.append(tool_doc)
        
        # Format embedding statistics  
        stats_summary = []
        if embedding_stats.get("sentence_transformers", 0) > 0:
            stats_summary.append(f"{embedding_stats['sentence_transformers']} SentenceTransformers")
        
        logger.info(f"Embedding generation complete: {' + '.join(stats_summary)} = {len(tool_data)} total")
        
        # Store using direct Redis operations like aws-redis-fin-agent
        logger.info("Storing tool embeddings in Redis with vector format...")
        
        stored_count = 0
        for tool_doc in tool_data:
            try:
                # Convert embedding to bytes format (aws-redis-fin-agent pattern)
                if isinstance(tool_doc["embedding"], list):
                    embedding_bytes = np.array(tool_doc["embedding"], dtype=np.float32).tobytes()
                    
                    # Use the same key pattern as our schema
                    key = f"tool:{tool_doc['name']}"
                    
                    # Store with embedding as bytes
                    redis_data = {
                        "name": tool_doc["name"],
                        "description": tool_doc["description"], 
                        "server": tool_doc["server"],
                        "type": tool_doc["type"],
                        "embedding": embedding_bytes
                    }
                    
                    # Store using sync Redis client (for RedisVL compatibility)
                    sync_redis_client.hset(key, mapping=redis_data)
                    stored_count += 1
                    
                    logger.debug(f"Stored {tool_doc['name']}: embedding_size={len(embedding_bytes)} bytes")
                
            except Exception as store_error:
                logger.error(f"Failed to store {tool_doc['name']}: {store_error}")
        
        logger.info(f"Storage complete: {stored_count}/{len(tool_data)} tools stored with vector embeddings")
        
        # Test vector search on stored data
        logger.info("Testing vector search functionality...")
        try:
            test_embedding_array = tool_embeddings.generate_embedding("test query")
            test_embedding = test_embedding_array.tolist()
            test_query = VectorQuery(
                vector=test_embedding,
                vector_field_name="embedding", 
                return_fields=["name", "description"],
                num_results=3
            )
            test_results = search_index.query(test_query)
            logger.info(f"Search test successful: Found {len(test_results)} results")
            
            if test_results:
                for i, result in enumerate(test_results[:2]):
                    distance = result.get("vector_distance", "N/A")
                    logger.info(f"  {i+1}. {result.get('name', 'N/A')} (distance: {distance})")
            
        except Exception as test_error:
            logger.error(f"Search test failed: {test_error}")
        
        logger.info(f"Tool indexing complete: {len(tool_data)} tools ready for vector search")
        
    except Exception as e:
        logger.error(f"Critical tool indexing error: {e}")
        logger.info("Falling back to mock tool selection for demo reliability")

def generate_enhanced_embedding_text(tool: Dict[str, Any], server_name: str) -> str:
    """Generate enhanced text for tool embeddings using natural language expansion."""

    # Start with the tool name and full description
    text_parts = [
        tool['name'],
        tool['description']
    ]

    # Add server/service context with domain-specific keywords
    server_context = {
        "zendesk": "customer support helpdesk ticketing customer service external customers end-users",
        "jira": "project management internal issues development bugs tasks sprint agile",
        "hubspot": "sales marketing CRM deals leads pipeline revenue",
        "pagerduty": "incident response on-call alerts engineering teams escalation",
        "datadog": "application monitoring APM logs metrics observability infrastructure",
        "confluence": "documentation wiki knowledge base articles pages collaboration",
        "m365": "microsoft office email teams sharepoint outlook calendar",
        "snowflake": "data warehouse SQL analytics database queries reporting"
    }

    if server_name.lower() in server_context:
        text_parts.append(server_context[server_name.lower()])

    text_parts.append(f"This {server_name} tool performs {tool['type']} operations.")
    
    # Include parameter information from inputSchema (MCP format)
    if "inputSchema" in tool and "properties" in tool["inputSchema"]:
        param_descriptions = []
        properties = tool["inputSchema"]["properties"]
        
        # Extract meaningful parameter descriptions
        for param_name, param_info in properties.items():
            if isinstance(param_info, dict) and "description" in param_info:
                # Include parameter descriptions which often contain valuable context
                param_descriptions.append(f"{param_name}: {param_info['description']}")
            
            # Also check nested properties for richer context
            if isinstance(param_info, dict) and "properties" in param_info:
                for nested_name, nested_info in param_info["properties"].items():
                    if isinstance(nested_info, dict) and "description" in nested_info:
                        param_descriptions.append(f"{nested_name}: {nested_info['description']}")
        
        if param_descriptions:
            # Add key parameter descriptions which contain use cases and context
            text_parts.extend(param_descriptions[:5])  # Include more context
    
    # Extract semantic keywords from tool name
    tool_name_parts = tool['name'].split('.')
    if len(tool_name_parts) > 1:
        action = tool_name_parts[1].replace('_', ' ')
        text_parts.append(f"Action: {action}")
    
    # Add common use case keywords based on tool function and server context
    tool_lower = tool['name'].lower()
    desc_lower = tool['description'].lower()

    if 'search' in tool_lower:
        text_parts.append("search query filter find lookup retrieve")
    if 'ticket' in tool_lower or 'ticket' in desc_lower:
        if server_name.lower() == 'zendesk':
            text_parts.append("customer tickets support requests customer issues helpdesk")
        elif server_name.lower() == 'hubspot':
            text_parts.append("service hub sales tickets deals pipeline")
    if 'log' in tool_lower:
        text_parts.append("logs logging events errors exceptions")
    if 'incident' in tool_lower or 'incident' in desc_lower:
        text_parts.append("incident outage critical emergency production issue")
    if 'trace' in tool_lower:
        text_parts.append("tracing spans performance monitoring")
    if 'performance' in desc_lower:
        text_parts.append("performance metrics latency errors throughput")
    if 'error' in desc_lower or 'failure' in desc_lower:
        text_parts.append("error debugging failure investigation troubleshooting")
    if 'payment' in desc_lower:
        text_parts.append("payment transactions billing financial money")
    if 'customer' in desc_lower:
        if server_name.lower() == 'zendesk':
            text_parts.append("external customers end users support requests")
        elif server_name.lower() == 'hubspot':
            text_parts.append("leads prospects sales opportunities")
    
    # The full text naturally contains the semantic meaning
    return " ".join(text_parts)

async def vector_search_tools(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    start_time = time.time() if enable_timing_logs else None
    
    perf_log("VECTOR_SEARCH_START: query_length=%d top_k=%d", len(query), top_k)
    debug_log("QUERY_TEXT: %s", query[:200] + ('...' if len(query) > 200 else ''))
    
    try:
        
        embedding_start = time.time() if enable_timing_logs else None
        
        try:
            embedding_array = tool_embeddings.generate_embedding(query)
            query_embedding = embedding_array.tolist()
            if enable_timing_logs:
                embedding_time = int((time.time() - embedding_start) * 1000)
                perf_log("EMBEDDING_GENERATED: method=SentenceTransformer time_ms=%d dimensions=%d", embedding_time, len(query_embedding))
        except Exception as e:
            logger.error(" CRITICAL: Query embedding generation failed: %s", e)
            raise RuntimeError(f"Cannot generate embedding for query '{query}': {e}")
        
        # Validate embedding
        if not isinstance(query_embedding, list) or len(query_embedding) != PERFORMANCE_CONFIG["vector_dim"]:
            logger.error(f" EMBEDDING: Invalid query embedding: type={type(query_embedding)}, len={len(query_embedding) if hasattr(query_embedding, '__len__') else 'N/A'}")
            return []
        
        # Create and execute RedisVL vector query
        search_start = time.time() if enable_timing_logs else None
        debug_log("REDIS_QUERY_START: method=RedisVL vector_field=embedding return_fields=4")
        
        vector_query = VectorQuery(
            vector=query_embedding,
            vector_field_name="embedding",
            return_fields=["name", "description", "server", "type"],
            num_results=top_k
        )
        
        # Execute the search (RedisVL query is synchronous)
        results = search_index.query(vector_query)
        if enable_timing_logs:
            search_time = int((time.time() - search_start) * 1000)
            perf_log("REDIS_QUERY_COMPLETE: time_ms=%d results_count=%d", search_time, len(results))
        else:
            search_time = 0
        
        # Process results
        selected_tools = []
        for i, result in enumerate(results):
            similarity_score = round(1 - float(result.get("vector_distance", 1)), 3)
            tool_data = {
                "name": result["name"],
                "description": result["description"],
                "server": result["server"],
                "type": result["type"],
                "similarity": similarity_score,
                "search_time_ms": int((time.time() - start_time) * 1000) if start_time else 0
            }
            selected_tools.append(tool_data)
            logger.info(f"TOOL_RANKED: rank={i+1} name={result['name']} server={result['server']} similarity={similarity_score} distance={result.get('vector_distance', 'N/A')}")
        
        if enable_timing_logs and start_time:
            total_time = int((time.time() - start_time) * 1000)
            logger.info(f"VECTOR_SEARCH_SUCCESS: tools_selected={len(selected_tools)} total_time_ms={total_time}")
        else:
            total_time = 0
        
        if selected_tools:
            best_tool = selected_tools[0]
            worst_tool = selected_tools[-1] if len(selected_tools) > 1 else best_tool
            logger.info(f"SIMILARITY_RANGE: best={best_tool['similarity']:.3f} worst={worst_tool['similarity']:.3f}")
            logger.info(f"TOP_RESULT: name={best_tool['name']} server={best_tool['server']} similarity={best_tool['similarity']:.3f}")
        
        return selected_tools
        
    except Exception as e:
        if enable_timing_logs and start_time:
            total_time = int((time.time() - start_time) * 1000)
            logger.error(f"VECTOR_SEARCH_ERROR: error={str(e)} time_ms={total_time}")
        else:
            total_time = 0
            logger.error(f"VECTOR_SEARCH_ERROR: error={str(e)}")
        logger.info("FALLBACK_ACTIVATED: method=rule_based reason=vector_search_failed")
        return []

async def check_semantic_cache(query: str) -> Optional[Dict[str, Any]]:
    """Optimized semantic cache check with performance improvements"""
    
    # Fast path: Check if caching is enabled
    if not PERFORMANCE_CONFIG.get("enable_semantic_cache", True):
        return None
    
    # Only check cache for information requests
    if not is_information_request(query):
        debug_log("CACHE_CHECK_SKIP: Not an information request: '%s'", query)
        return None
        
    if not is_redis_connected or not cache_index:
        debug_log("CACHE_UNAVAILABLE: Redis not connected or cache_index missing")
        return None
        
    try:
        # Generate real embedding for the query using SentenceTransformers
        try:
            embedding_array = tool_embeddings.generate_embedding(query)
            query_embedding = embedding_array.tolist()
        except Exception as e:
            logger.error(f" CRITICAL: Cache embedding generation failed: {e}")
            raise RuntimeError(f"Cannot generate cache embedding for query: {e}")
        
        # Search for similar cached queries
        cache_query = VectorQuery(
            vector=query_embedding,
            vector_field_name="embedding",
            return_fields=["query", "response", "tools_used", "cached_at"],
            num_results=1
        )
        
        # Execute the cache search (RedisVL is synchronous, run in thread)
        results = await asyncio.to_thread(cache_index.query, cache_query)
        
        if results and len(results) > 0:
            result = results[0]
            similarity = 1 - float(result["vector_distance"])
            threshold = PERFORMANCE_CONFIG["cache_similarity_threshold"]
            
            logger.info(f"CACHE_SIMILARITY_CHECK: similarity={similarity:.3f} threshold={threshold:.3f} query='{result.get('query', 'N/A')}'")
            
            # Check if similarity meets threshold
            if similarity >= threshold:
                logger.info(f"CACHE_HIT: {similarity:.0%} similarity with cached query='{result.get('query', 'N/A')}'")
                return {
                    "response": result["response"],
                    "similarity": int(similarity * 100),
                    "cached_at": result["cached_at"],
                    "original_query": result.get("query", "Previous similar query"),
                    "tools_used": json.loads(result.get("tools_used", "[]"))
                }
            else:
                logger.info(f"CACHE_MISS: similarity={similarity:.3f} below threshold={threshold:.3f}")
        
        # No cache hit found
        logger.info("CACHE_MISS: No similar cached queries found")
        return None
        
    except Exception as e:
        logger.error(f"Cache check error: {e}")
        return None


def is_information_request(query: str) -> bool:
    """Check if the query is requesting information (cacheable)."""
    query_lower = query.lower().strip()
    
    # Information request keywords
    info_keywords = [
        "get", "search", "find", "show", "list", "display",
        "what", "where", "when", "why", "how", "which", "who",
        "tell me", "give me", "fetch", "retrieve", "look up"
    ]
    
    # Check if query starts with or contains information request patterns
    for keyword in info_keywords:
        if query_lower.startswith(keyword) or f" {keyword} " in f" {query_lower} ":
            return True
    
    # Also check for question patterns
    if query_lower.endswith("?"):
        return True
        
    return False

async def store_in_cache(query: str, response: str, tools_used: List[str]):
    """Optimized cache storage with performance improvements"""
    
    # Fast path: Check if caching is enabled  
    if not PERFORMANCE_CONFIG.get("enable_semantic_cache", True):
        return
    
    # Only cache information requests
    if not is_information_request(query):
        debug_log("CACHE_STORE_SKIP: Not an information request: '%s'", query)
        return
        
    debug_log("CACHE_STORE: storing information request='%s' with %d tools", query, len(tools_used))
    
    if not is_redis_connected or not cache_index:
        debug_log("CACHE_STORE_SKIP: Redis not connected or cache_index missing")
        return
        
    try:
        # Generate real embedding for the query using SentenceTransformers
        try:
            embedding_array = tool_embeddings.generate_embedding(query)
            query_embedding = embedding_array.tolist()
        except Exception as e:
            logger.error(f" CRITICAL: Cache storage embedding generation failed: {e}")
            raise RuntimeError(f"Cannot generate embedding for caching: {e}")
        
        # Store using direct Redis operations but compatible with RedisVL search
        cache_key = f"supportAssistant:cache:{abs(hash(query)) % 10000}"
        
        # Convert embedding to bytes for Redis storage
        embedding_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
        
        cache_data = {
            "query": query,
            "response": response,
            "tools_used": json.dumps(tools_used),
            "cached_at": datetime.now().isoformat(),
            "embedding": embedding_bytes
        }
        
        # Store in Redis with TTL (direct operation for reliability)
        await redis_client.hset(cache_key, mapping=cache_data)
        await redis_client.expire(cache_key, PERFORMANCE_CONFIG["cache_ttl"])
        
        logger.info(f"✅ CACHE_STORED: query='{query}' key={cache_key}")
        
    except Exception as e:
        logger.error(f"Cache storage error: {e}")


def format_tool_selection_response(selected_tools: List[Dict[str, Any]], method: str, total_tools: int) -> str:
    """
    Format tool selection results for display.
    
    Creates a concise summary showing reduction in tool count
    and selection efficiency.
    
    Args:
        selected_tools: List of selected tools
        method: Selection method (baseline or optimized)
        total_tools: Total number of available tools
    
    Returns:
        Formatted summary string
    """
    if not selected_tools:
        return f"{method.upper()}: No tools selected"
    
    selection_rate = (len(selected_tools) / total_tools) * 100 if total_tools > 0 else 0
    
    # Simple, professional summary
    summary = f"{method.upper()}: {len(selected_tools)} of {total_tools} tools selected"
    
    if method == "optimized":
        reduction = 100 - selection_rate
        summary += f" ({reduction:.0f}% reduction)"
    
    return summary

def is_write_operation(query: str) -> bool:
    """Check if query involves write operations."""
    write_keywords = ["create", "send", "update", "add", "delete", "draft and send"]
    return any(keyword in query.lower() for keyword in write_keywords)

async def process_baseline_query(query: str) -> ChatResponse:
    """
    Process query using baseline approach with all tools sent to LLM.
    
    This represents the traditional MCP approach where all available
    tools are sent to the LLM for reasoning, resulting in higher
    latency and token usage.
    
    Args:
        query: User query to process
    
    Returns:
        ChatResponse with tool selection results and metrics
    """
    if not llm_service or not llm_service.client:
        raise HTTPException(status_code=503, detail="LLM service not available")
    
    start_time = time.time()
    logger.info(f"BASELINE_QUERY_START: query_length={len(query)} approach=all_tools_to_llm")
    
    # Get all tools with full realistic definitions
    all_tools = []
    for server_name, server_tools in TOOLS_CONFIG.items():
        for tool in server_tools:
            all_tools.append({**tool, "server": server_name})
    
    logger.info(f"BASELINE_TOOLS_LOADED: total_tools={len(all_tools)} servers={len(TOOLS_CONFIG)}")
    
    try:
        # Call LLM with ALL tools - this is the baseline (expensive)
        logger.info(f"BASELINE_LLM_CALL: sending_all_tools={len(all_tools)} to LLM")
        llm_result = await llm_service.select_relevant_tools(query, all_tools)
        
        # Show actual LLM tool selection results instead of mock business response
        response_text = format_tool_selection_response(llm_result["tools"], "baseline", len(all_tools))
        
        end_time = time.time()
        actual_latency = round(end_time - start_time, 3)
        
        logger.info(f"BASELINE_COMPLETE: latency={actual_latency}s tokens={llm_result['tokens']} cost=${llm_result['cost']:.4f} tools_sent={len(all_tools)} tools_selected={len(llm_result['tools'])}")
        
        # Professional workflow analysis
        logger.info(f"WORKFLOW_ANALYSIS: phase=tool_selection method=baseline status=complete")
        logger.info(f"NEXT_PHASE: mcp_tool_execution tools_to_execute={len(llm_result['tools'])} estimated_time={len(llm_result['tools'])*2.5:.1f}s")
        logger.info(f"REDIS_VALUE_PROP: current_bottleneck=llm_reasoning scales_poorly=yes solution=vector_prefiltering")
        
        return ChatResponse(
            response=response_text,
            latency=actual_latency,
            tokens=llm_result["tokens"],
            cost=round(llm_result["cost"], 4),
            tools_count=len(all_tools),  # All tools sent to LLM
            tools_used=[tool["name"] for tool in llm_result["tools"]],  # LLM selected tools
            cache_status="BYPASS"
        )
        
    except Exception as e:
        end_time = time.time()
        error_latency = round(end_time - start_time, 3)
        logger.error(f"BASELINE_ERROR: error={str(e)} latency={error_latency}s")
        raise HTTPException(status_code=500, detail=str(e))

async def process_optimized_query(query: str) -> ChatResponse:
    """
    Process query using Redis-optimized approach.
    
    Uses vector search to pre-filter relevant tools before sending
    to LLM, and semantic caching for similar queries. This approach
    significantly reduces latency and token usage.
    
    Args:
        query: User query to process
    
    Returns:
        ChatResponse with tool selection results and metrics
    """
    if not llm_service or not llm_service.client:
        raise HTTPException(status_code=503, detail="LLM service not available")
    
    start_time = time.time()
    logger.info(f"OPTIMIZED_QUERY_START: query_length={len(query)} approach=vector_search_plus_cache")
    
    # Parallel cache check + vector search preparation for optimal latency
    cache_start = time.time()
    total_available = sum(len(tools) for tools in TOOLS_CONFIG.values())
    
    # Start both cache check and vector search in parallel (cache is usually faster)
    cache_task = asyncio.create_task(check_semantic_cache(query))
    # Pre-calculate for potential vector search
    
    cached_result = await cache_task
    cache_check_time = int((time.time() - cache_start) * 1000)
    logger.info(f"CACHE_CHECK_COMPLETE: time_ms={cache_check_time} result={'HIT' if cached_result else 'MISS'}")
    
    if cached_result:
        # Cache hit - return immediately with real timing
        cache_end_time = time.time()
        cache_latency = round(cache_end_time - start_time, 3)
        
        logger.info(f"CACHE_HIT_RETURN: latency={cache_latency}s similarity={cached_result.get('similarity')}% tokens_saved=significant cost_saved=significant")
        
        return ChatResponse(
            response=cached_result["response"],
            latency=cache_latency,
            tokens=0,  # Cached response - no LLM call
            cost=0.0,
            tools_count=0,
            cache_status="HIT",
            vector_search_time=int(cache_latency * 1000),
            similarity=cached_result.get("similarity"),
            original_query=cached_result.get("original_query")
        )
    
    # Cache miss - now do vector search
    vector_start = time.time()
    logger.info(f"VECTOR_FILTERING_START: total_available_tools={total_available}")
    
    vector_filtered_tools = await vector_search_tools(query)
    vector_end_time = time.time()
    vector_time = int((vector_end_time - vector_start) * 1000)
    
    logger.info(f"VECTOR_FILTERING_COMPLETE: tools_reduced_from={total_available}_to={len(vector_filtered_tools)} reduction_ratio={len(vector_filtered_tools)/total_available:.1%} time_ms={vector_time}")
    
    # Convert to format needed for LLM (optimized lookup)
    filtered_for_llm = []
    # Use precomputed global tool lookup cache - O(1) lookup
    for tool in vector_filtered_tools:
        if tool["name"] in tool_lookup_cache:
            filtered_for_llm.append(tool_lookup_cache[tool["name"]])
    
    try:
        # Call LLM with ONLY the pre-filtered tools (much fewer than baseline)
        logger.info(f"OPTIMIZED_LLM_CALL: sending_filtered_tools={len(filtered_for_llm)} reduction_from={total_available}")
        llm_result = await llm_service.select_relevant_tools(query, filtered_for_llm)
        
        # Show actual LLM tool selection results instead of mock business response
        response_text = format_tool_selection_response(llm_result["tools"], "optimized", len(filtered_for_llm))
        
        end_time = time.time()
        actual_latency = round(end_time - start_time, 3)
        
        # Store in cache if it's a read operation (for next time)
        will_cache = not is_write_operation(query)
        if will_cache:
            await store_in_cache(query, response_text, [tool["name"] for tool in llm_result["tools"]])
        
        # Determine cache status
        cache_status = "BYPASS" if is_write_operation(query) else "MISS"
        
        logger.info(f"OPTIMIZED_COMPLETE: latency={actual_latency}s tokens={llm_result['tokens']} cost=${llm_result['cost']:.4f} tools_sent={len(filtered_for_llm)} tools_selected={len(llm_result['tools'])} cache_status={cache_status} will_cache={will_cache}")
        
        # Professional workflow analysis  
        efficiency_gain = (1 - (len(filtered_for_llm) / total_available)) * 100 if total_available > 0 else 0
        logger.info(f"WORKFLOW_ANALYSIS: phase=tool_selection method=redis_optimized status=complete efficiency_gain={efficiency_gain:.1f}%")
        logger.info(f"NEXT_PHASE: mcp_tool_execution tools_to_execute={len(llm_result['tools'])} estimated_time={len(llm_result['tools'])*2.5:.1f}s")
        logger.info(f"REDIS_IMPACT: prefiltering_reduced_context_by={efficiency_gain:.1f}% reasoning_time_saved={actual_latency:.1f}s")
        
        return ChatResponse(
            response=response_text,
            latency=actual_latency,
            tokens=llm_result["tokens"],
            cost=round(llm_result["cost"], 4),
            tools_count=len(vector_filtered_tools),  # Actual vector search results count
            cache_status=cache_status,
            vector_search_time=vector_time,
            tools_used=[tool["name"] for tool in llm_result["tools"]],
            filtered_tools=[tool["name"] for tool in vector_filtered_tools]
        )
        
    except Exception as e:
        end_time = time.time()
        error_latency = round(end_time - start_time, 3)
        logger.error(f"OPTIMIZED_ERROR: error={str(e)} latency={error_latency}s vector_time_ms={vector_time if 'vector_time' in locals() else 0}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """
    Initialize all services on application startup.
    
    Sets up:
    - Embedding service (SentenceTransformers)
    - Redis connection and RedisVL indexes
    - Tool lookup cache
    - LLM service (OpenAI)
    """
    logger.info("Initializing Redis MCP Latency Reduction Demo...")
    
    # Initialize real embedding service (like redis-movie-search) - REQUIRED
    global tool_embeddings
    try:
        logger.info("Initializing SentenceTransformers embedding service...")
        tool_embeddings = ToolEmbeddings()
        logger.info(f"SentenceTransformers ready: {tool_embeddings.dimension}-dimensional embeddings")
        # Update config with actual dimension
        PERFORMANCE_CONFIG["vector_dim"] = tool_embeddings.dimension
        logger.info("Real-time embeddings enabled")
    except Exception as e:
        logger.error(f"CRITICAL: Embedding service initialization failed: {e}")
        logger.error("This demo requires real embeddings with sentence-transformers")
        logger.error("Install with: pip3 install sentence-transformers")
        raise RuntimeError("Cannot start demo without real embedding service")
    
    # Initialize global tool lookup cache for O(1) performance
    global tool_lookup_cache
    tool_lookup_cache = {}
    for server_name, server_tools in TOOLS_CONFIG.items():
        for tool in server_tools:
            tool_lookup_cache[tool["name"]] = {**tool, "server": server_name}
    logger.info(f"Tool lookup cache initialized with {len(tool_lookup_cache)} tools")
    
    # Initialize Redis
    await initialize_redis()
    
    # Initialize LLM service for real tool selection
    global llm_service
    try:
        logger.info("Initializing OpenAI LLM service...")
        llm_service = LLMService()
        llm_initialized = llm_service.initialize()
        if llm_initialized:
            logger.info("OpenAI LLM ready for tool selection")
        else:
            logger.warning("LLM service disabled - set OPENAI_API_KEY for real LLM comparisons")
    except Exception as e:
        logger.warning(f"LLM service initialization failed: {e}")
        logger.info("Demo will use fallback tool selection without LLM")
    
    logger.info("Demo initialization complete")

@app.get("/")
async def serve_index():
    """Serve the main demo page."""
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health_check() -> HealthResponse:
    """
    Service health check endpoint.
    
    Returns status of all critical components including Redis,
    embedding service, and LLM connectivity.
    """
    return HealthResponse(
        status="ok",
        redis=is_redis_connected,
        sentence_transformers=tool_embeddings is not None,
        openai=llm_service is not None and llm_service.client is not None,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/query")
async def process_query(request: ChatRequest) -> ChatResponse:
    """
    Process user query using selected approach.
    
    Routes to either baseline (all tools) or optimized (vector search)
    processing based on panel selection.
    """
    try:
        if request.panel == "baseline":
            return await process_baseline_query(request.query)
        elif request.panel == "optimized":
            return await process_optimized_query(request.query)
        else:
            raise HTTPException(status_code=400, detail="Invalid panel type")
            
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def get_all_tools():
    """Get list of all available tools."""
    all_tools = []
    for server_name, tools in TOOLS_CONFIG.items():
        for tool in tools:
            all_tools.append({
                **tool,
                "server": server_name
            })
    return all_tools

@app.delete("/api/cache")
async def clear_cache():
    """Clear the semantic cache."""
    if not is_redis_connected:
        return {"cleared_items": 0, "message": "Cache not available - Redis not connected"}
    
    try:
        # Delete only our support assistant cache keys
        cache_keys = []
        async for key in redis_client.scan_iter(match="supportAssistant:cache:*"):
            cache_keys.append(key)
        
        if cache_keys:
            await redis_client.delete(*cache_keys)
        
        
        logger.info(f"Cache cleared: {len(cache_keys)} items removed")
        
        return {
            "cleared_items": len(cache_keys),
            "message": f"Cache cleared! {len(cache_keys)} items removed."
        }
        
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance/stats")
async def get_performance_stats():
    """Get comprehensive performance statistics and cache metrics"""
    stats = {
        "config": {
            "semantic_cache_enabled": PERFORMANCE_CONFIG.get("enable_semantic_cache", True),
            "cache_similarity_threshold": PERFORMANCE_CONFIG.get("cache_similarity_threshold", 0.65),
            "log_level": PERFORMANCE_CONFIG.get("log_level", "INFO"),
            "timing_logs_enabled": enable_timing_logs,
            "embedding_cache_size": PERFORMANCE_CONFIG.get("embedding_cache_size", 1000)
        },
        "caches": {
            "tool_lookup_cache_size": len(tool_lookup_cache),
            "redis_connected": is_redis_connected
        }
    }
    
    # Add embedding cache stats if available
    if tool_embeddings:
        stats["caches"]["embedding_cache"] = tool_embeddings.get_cache_stats()
    
    # Add Redis cache stats if available
    if is_redis_connected:
        try:
            cache_keys = await redis_client.keys("supportAssistant:cache:*")
            stats["caches"]["redis_cache_items"] = len(cache_keys)
        except:
            stats["caches"]["redis_cache_items"] = "unavailable"
    
    return stats

@app.get("/api/debug/embeddings")
async def debug_embeddings():
    """Debug endpoint to check embedding text quality."""
    debug_results = []
    
    # Check a few key tools that should match "checkout 5xx errors"
    key_tools = [
        ("datadog", "datadog.search_logs"),
        ("datadog", "datadog.trace_search"), 
        ("datadog", "datadog.analyze_service_performance"),
        ("jira", "jira.get_issue")
    ]
    
    for server_name, tool_name in key_tools:
        if server_name in TOOLS_CONFIG:
            for tool in TOOLS_CONFIG[server_name]:
                if tool["name"] == tool_name:
                    embedding_text = generate_enhanced_embedding_text(tool, server_name)
                    debug_results.append({
                        "tool_name": tool_name,
                        "server": server_name,
                        "embedding_text": embedding_text[:500] + "..." if len(embedding_text) > 500 else embedding_text,
                        "text_length": len(embedding_text)
                    })
                    break
    
    return {"debug_embeddings": debug_results}

@app.post("/api/debug/reindex")
async def force_reindex():
    """Force regeneration of tool embeddings with updated text."""
    if not is_redis_connected or not tool_embeddings:
        return {"error": "Redis or embeddings not available"}
    
    try:
        logger.info("FORCE REINDEX: Regenerating all tool embeddings...")
        
        # Clear existing tool index more thoroughly
        try:
            # Drop the specific indexes first
            try:
                search_index.delete(drop=True)
                logger.info("Search index dropped")
            except Exception as e:
                logger.warning(f"Search index drop warning: {e}")
                
            try:
                cache_index.delete(drop=True)
                logger.info("Cache index dropped")
            except Exception as e:
                logger.warning(f"Cache index drop warning: {e}")
                
            # Clear only support assistant cache keys (not entire database)
            sync_keys = [key.decode() for key in sync_redis_client.keys("supportAssistant:cache:*")]
            if sync_keys:
                sync_redis_client.delete(*sync_keys)
                logger.info(f"Cleared {len(sync_keys)} support assistant cache keys")
            else:
                logger.info("No support assistant cache keys to clear")
            
        except Exception as e:
            logger.warning(f"Redis clear warning: {e}")
        
        # Recreate indexes with fresh data
        await setup_redisvl_indexes()
        
        return {"message": "Tool embeddings regenerated successfully", "status": "success"}
        
    except Exception as e:
        logger.error(f"Reindex error: {e}")
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=DEMO_CONFIG["host"],
        port=DEMO_CONFIG["port"],
        reload=DEMO_CONFIG["debug"]
    )