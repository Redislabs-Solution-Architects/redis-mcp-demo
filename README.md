# Redis MCP Demos

**Redis just got way easier.** With Model Context Protocol (MCP), you can manage Redis through conversation instead of learning commands and writing integration code.

Here's how it works: MCP connects Large Language Models directly to Redis, so AI can handle all the database operations for you. We've built two demos to show you what's possible when Redis gets an AI interface.

## Two Demo Scenarios

### **Infrastructure Prototyping** → `claude-desktop/`
This demo shows how Redis MCP enables rapid database architecture exploration through Claude Desktop. It's designed to demonstrate Redis Cloud management, data seeding, and AI-powered optimization suggestions without requiring Redis expertise. The demo highlights how developers can prototype Redis infrastructure through conversation rather than learning commands and writing scripts.

**Purpose:** Show Redis MCP's capability for database management and architecture discovery  
**Audience:** Solutions architects, developers exploring Redis, teams doing rapid prototyping  
[→ Setup & Run](claude-desktop/README.md)

### **AI-Powered Persistent Memory** → `conversation-context/`  
This demo compares traditional Redis integration with Redis MCP for LLM applications with persistent memory. It provides working examples of both approaches - a traditional implementation with many lines of Redis code versus an MCP implementation with natural language instructions. The demo proves Redis persistence works across application restarts while showing the dramatic reduction in code complexity.

**Purpose:** Demonstrate Redis MCP's impact on application development complexity  
**Audience:** Developers building AI applications, teams evaluating Redis integration approaches  
[→ Setup & Run](conversation-context/README.md)
