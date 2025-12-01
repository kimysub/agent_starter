# Agent Starter Pack API

REST API for generating AI agent templates programmatically.

## Overview

The Agent Starter Pack API provides programmatic access to agent template generation. This allows other platforms, web frontends, IDEs, and automation tools to generate agent code without using the CLI.

## Features

- **Simple API**: Just return agent.py code
- **Configurable**: Custom tools/functions and environment variables
- **Public API**: No authentication required
- **CORS enabled**: Works with web frontends

## Quick Start

### Installation

The API is included with agent-starter-pack. Install dependencies:

```bash
uv sync
```

### Running the API Server

```bash
# Using the CLI command
uv run agent-starter-pack-api

# Or using uvicorn directly
uvicorn agent_starter_pack.api.main:app --host 0.0.0.0 --port 8080
```

The API will be available at `http://localhost:8080`

### API Documentation

Once running, visit:
- Interactive docs: `http://localhost:8080/docs`
- Alternative docs: `http://localhost:8080/redoc`

## API Endpoints

### `POST /api/v1/generate/agent`

Generate agent.py code with custom configuration.

**Request Body:**

```json
{
  "project_name": "my-agent",
  "agent_type": "adk_a2a_base",
  "tools": [
    {
      "name": "get_stock_price",
      "description": "Get current stock price for a symbol",
      "parameters": "symbol: str",
      "implementation": "    return f\"${symbol}: $123.45\""
    }
  ],
  "env_vars": [
    {
      "name": "API_KEY",
      "default_value": "your-api-key",
      "description": "API key for external service"
    }
  ],
  "agent_description": "A helpful stock trading assistant",
  "agent_instruction": "You help users check stock prices and make informed decisions."
}
```

**Response:**

```json
{
  "code": "# Copyright 2025 Google LLC\n...",
  "filename": "agent.py",
  "agent_type": "adk_a2a_base"
}
```

### `GET /health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## Examples

### Using curl

```bash
curl -X POST http://localhost:8080/api/v1/generate/agent \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "weather-agent",
    "agent_type": "adk_a2a_base",
    "agent_description": "A weather information assistant",
    "agent_instruction": "Provide accurate weather information for any location."
  }'
```

### Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:8080/api/v1/generate/agent",
    json={
        "project_name": "my-agent",
        "agent_type": "adk_a2a_base",
        "tools": [
            {
                "name": "calculate",
                "description": "Perform a calculation",
                "parameters": "expression: str",
                "implementation": "    return str(eval(expression))"
            }
        ]
    }
)

code = response.json()["code"]
print(code)
```

### Using JavaScript fetch

```javascript
const response = await fetch('http://localhost:8080/api/v1/generate/agent', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    project_name: 'my-agent',
    agent_type: 'adk_a2a_base',
    tools: [
      {
        name: 'translate',
        description: 'Translate text to another language',
        parameters: 'text: str, target_lang: str',
        implementation: '    return f"Translated: {text}"'
      }
    ]
  })
});

const data = await response.json();
console.log(data.code);
```

## Configuration

### Supported Agent Types

- `adk_a2a_base` - ADK agent with Agent2Agent protocol (recommended)
- `adk_base` - Basic ADK agent

### Tool Definition

Each tool requires:
- `name`: Function name (must be valid Python identifier)
- `description`: What the tool does (used in docstring)
- `parameters`: Function parameters (e.g., "query: str, limit: int = 10")
- `implementation`: Function body (must be indented with 4 spaces)

### Environment Variable Definition

Each environment variable requires:
- `name`: Variable name (uppercase recommended)
- `default_value`: Default value if not set
- `description`: (optional) Description of the variable

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8080
CMD ["uv", "run", "agent-starter-pack-api"]
```

### Docker Compose

```yaml
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - UVICORN_HOST=0.0.0.0
      - UVICORN_PORT=8080
```

## Development

### Running with Auto-Reload

```bash
uvicorn agent_starter_pack.api.main:app --reload --port 8080
```

### Testing

```bash
# Test the API
curl http://localhost:8080/health

# Generate agent code
curl -X POST http://localhost:8080/api/v1/generate/agent \
  -H "Content-Type: application/json" \
  -d '{"project_name": "test-agent"}' | jq -r '.code'
```

## Use Cases

1. **Web Frontend**: Build a visual agent builder that calls the API
2. **IDE Integration**: Create VSCode/JetBrains plugins that generate agents
3. **Automation**: Generate agents in CI/CD pipelines
4. **Templates**: Quickly generate agent code for specific use cases
5. **Education**: Provide interactive agent creation for learning platforms

## License

Apache 2.0 - See LICENSE file for details
