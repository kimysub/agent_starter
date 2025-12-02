# Agent Starter Pack API v2.0

REST API for generating complete AI agent projects - designed for UI integration.

## Quick Start

### Installation

```bash
# Install agent-starter-pack with dependencies
pip install agent-starter-pack

# Start API server
agent-starter-pack-api
```

### Basic Usage

```bash
# Generate project
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "my-agent",
    "description": "A helpful assistant",
    "prompt": "You help users with questions"
  }'

# Download project
curl -O http://localhost:8080/downloads/my-agent.zip
```

## Success Examples

### Example 1: Simple Agent

**Request:**
```bash
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "hello-agent",
    "description": "A friendly greeting agent",
    "prompt": "You greet users warmly"
  }'
```

**Success Response:**
```json
{
  "project_name": "hello-agent",
  "download_url": "/downloads/hello-agent.zip",
  "git_repo_url": null,
  "files_generated": 23,
  "message": "Project 'hello-agent' generated successfully!"
}
```

### Example 2: With Custom Tools

**Request:**
```bash
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "support-bot",
    "description": "Customer support chatbot",
    "prompt": "You help customers with their questions",
    "tools": [
      {"name": "search_faq", "description": "Search FAQ database"},
      {"name": "create_ticket", "description": "Create support ticket"}
    ]
  }'
```

**Success Response:**
```json
{
  "project_name": "support-bot",
  "download_url": "/downloads/support-bot.zip",
  "git_repo_url": null,
  "files_generated": 25,
  "message": "Project 'support-bot' generated successfully!"
}
```

### Example 3: With Git Repository

**Request:**
```bash
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "sales-agent",
    "description": "Sales assistant",
    "prompt": "You help with product information",
    "create_git_repo": true
  }'
```

**Success Response:**
```json
{
  "project_name": "sales-agent",
  "download_url": "/downloads/sales-agent.zip",
  "git_repo_url": "file:///tmp/agent-starter-pack-api/projects/sales-agent",
  "files_generated": 23,
  "message": "Project 'sales-agent' generated successfully!"
}
```

## What Gets Generated

- **app/agent.py** - Customized agent with your description & prompt
- **Dockerfile** + **docker-compose.yml** - Deployment files
- **.env.example** - Configuration template
- **pyproject.toml** - Dependencies
- **README.md** - Documentation
- **Complete ADK + A2A** - Full agent framework

## API Reference

### POST /api/v1/generate/project

**Request Schema:**
```json
{
  "agent_name": "string (required)",
  "description": "string (required)",
  "prompt": "string (required)",
  "tools": [
    {"name": "string", "description": "string"}
  ],
  "create_git_repo": "boolean (default: false)"
}
```

**Response Schema:**
```json
{
  "project_name": "string",
  "download_url": "string",
  "git_repo_url": "string|null",
  "files_generated": "integer",
  "message": "string"
}
```

## Interactive Documentation

- Swagger UI: http://localhost:8080/docs
- Health Check: http://localhost:8080/health

## License

Apache 2.0
