# Redis MCP Demos

Model Context Protocol (MCP) enables LLM agents to interact with external tools and services. 
These demos showcase Redis in two ways: 
1) Optimizing MCP agent workflows through intelligent tool filtering
2) Interacting with Redis MCP servers in a variety of use cases.
## Demos

### Optimizing MCP Workflows

#### **⭐ MCP Tool Filtering with Redis** → `mcp-tool-filtering/`
[→ Setup & Run Instructions](mcp-tool-filtering/README.md)

MCP agents can access 170+ tools, but sending all schemas to the LLM causes high costs, slow responses, and inaccurate selection. This demo uses Redis vector search to pre-filter tools for faster MCP workflows, reducing context size by 98%, and improving tool selection accuracy. See side-by-side comparison of baseline vs. optimized approach.

**Purpose:** Demonstrate Redis vector search for intelligent tool selection in MCP workflows
**Audience:** Developers building MCP agents, teams optimizing LLM applications for cost and performance

---

### Redis MCP Server Examples

#### **Chatbot Persistent Memory** → `conversation-context/`
[→ Setup & Run Instructions](conversation-context/README.md)

This demo compares traditional Redis integration with Redis MCP for LLM applications with persistent memory. It provides working examples of both approaches. The demo showcases MCP's reduction in code complexity and persistence across multiple chat sessions.

**Purpose:** Demonstrate Redis MCP's impact on application development complexity
**Audience:** Developers building AI applications, teams evaluating Redis integration approaches

#### **Infrastructure and Data Prototyping** → `claude-desktop/`
[→ Setup & Run Instructions](claude-desktop/README.md)

Manage Redis Cloud databases through Claude Desktop chat. Create databases, seed data, and get AI optimization suggestions without learning Redis commands.

**Purpose:** Show Redis MCP's capability for database management and architecture discovery
**Audience:** Solutions architects, developers exploring Redis, teams doing rapid prototyping

#### **Semantic Search Interface** → `vector-search-mcp/`
[→ Setup & Run Instructions](vector-search-mcp/README.md)

Natural language movie search powered by Redis vector embeddings. Find movies through conversational queries like "space adventures with aliens" without writing vector search code.

**Purpose:** Demonstrate Redis MCP enabling semantic search through natural language
**Audience:** Developers building search applications, teams exploring vector databases  