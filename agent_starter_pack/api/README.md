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

### Example 3: With GitHub Push (Folder-based)

**Request:**
```bash
# Set GitHub token (required for GitHub integration)
export GITHUB_TOKEN=ghp_your_token_here

curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "sales-agent",
    "description": "Sales assistant",
    "prompt": "You help with product information",
    "create_git_repo": true,
    "git_repo_name": "agents-collection"
  }'
```

**Success Response:**
```json
{
  "project_name": "sales-agent",
  "download_url": "/downloads/sales-agent.zip",
  "git_repo_url": "https://github.com/yourusername/agents-collection/tree/main/sales-agent-0042",
  "git_folder_name": "sales-agent-0042",
  "files_generated": 23,
  "message": "Project 'sales-agent' generated successfully!"
}
```

**Note:** The agent is pushed to a numbered folder (e.g., `sales-agent-0042`) in the existing `agents-collection` repository. The repository must already exist on GitHub.

## What Gets Generated

- **app/agent.py** - Customized agent with your description & prompt
- **Dockerfile** + **docker-compose.yml** - Deployment files
- **.env.example** - Configuration template
- **pyproject.toml** - Dependencies
- **README.md** - Documentation
- **Complete ADK + A2A** - Full agent framework

## GitHub Integration

The API can automatically push your generated projects to a fixed GitHub repository as numbered folders!

**Folder-Based Approach:**
- All agents are pushed to **ONE existing repository**
- Each agent gets a **unique numbered folder** (e.g., `my-agent-0042`)
- Perfect for **mono-repo pattern** and centralized agent management

**Setup:**
1. Create a GitHub repository (e.g., `agents-collection`) on GitHub.com or GitHub Enterprise
2. Create a GitHub Personal Access Token with `repo` scope
3. Set the `GITHUB_TOKEN` environment variable:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```

**Features:**
- ✅ Push to repositories on **GitHub.com**
- ✅ Push to repositories in **GitHub organizations**
- ✅ Push to repositories on **GitHub Enterprise**
- ✅ Automatic **numbered folder naming** (e.g., `agent-0001`, `agent-0042`)
- ✅ **Mono-repo pattern** - all agents in one place

**Example:**
```bash
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "my-bot",
    "description": "My chatbot",
    "prompt": "You are helpful",
    "create_git_repo": true,
    "git_repo_name": "agents-collection",
    "github_org": "my-company"
  }'
```

**Result:** Agent pushed to `https://github.com/my-company/agents-collection/tree/main/my-bot-0042`

**See full documentation:** [docs/GITHUB_INTEGRATION.md](../../docs/GITHUB_INTEGRATION.md)

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
  "create_git_repo": "boolean (default: false)",
  "git_repo_name": "string (required if create_git_repo=true) - Fixed repo name",
  "github_token": "string (optional, can use GITHUB_TOKEN env var)",
  "github_org": "string (optional)",
  "github_enterprise_url": "string (optional)"
}
```

**Response Schema:**
```json
{
  "project_name": "string",
  "download_url": "string",
  "git_repo_url": "string|null - URL to folder in repository",
  "git_folder_name": "string|null - Folder name (e.g., 'agent-0042')",
  "files_generated": "integer",
  "message": "string"
}
```

## Interactive Documentation

- Swagger UI: http://localhost:8080/docs
- Health Check: http://localhost:8080/health

## License

Apache 2.0
