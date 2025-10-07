# Dynamic Tool Selection by Redis

Model Context Protocol (MCP) tool selection using Redis vector search.

## Background

MCP servers expose numerous tools to LLM applications, creating a context scaling challenge. As tool inventories grow , sending all tools to the LLM for every request becomes inefficient: increasing latency, token consumption, and costs. 

This demo implements a two-stage optimization: Redis vector search pre-filters tools based on semantic similarity to the query, reducing the LLM's context from 170+ tools to 2-3 relevant ones. Combined with semantic caching for repeated queries, which achieves latency reduction while maintaining selection accuracy.

## Architecture

### Core Components

- **FastAPI Backend** (`app.py`): Main application server handling API requests and orchestrating tool selection
- **Vector Search Index**: Redis HNSW index for semantic similarity search across MCP tools
- **Semantic Cache**: TTL-based cache for similar query responses
- **Embedding Service**: SentenceTransformers for generating 384-dimensional embeddings
- **LLM Integration**: OpenAI GPT-4 for final tool selection from pre-filtered candidates

## Installation

### Configuration

1. Copy the example configuration file:
```bash
cp config.py.example config.py
```

2. Edit `config.py` and replace all instances of `"STUB_VALUE"` with your actual credentials:
   - Redis URL, host, port, and password
   - OpenAI API key

### Start

```bash
./setup.sh
```

### Tool Selection Pipeline

1. **Query Embedding**: Generate vector representation of user query
2. **Vector Search**: Find top-k similar tools using Redis VSS (8ms average)
3. **LLM Refinement**: Send pre-filtered tools to GPT-4 for final selection
4. **Response Caching**: Store query request responses with embedding for future similarity matching


