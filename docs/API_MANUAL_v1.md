# Agent Starter Pack API - User Manual

Complete guide for using the Agent Starter Pack API to generate AI agent code programmatically.

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [API Reference](#api-reference)
4. [Integration Examples](#integration-examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Introduction

The Agent Starter Pack API allows you to generate AI agent code programmatically without using the CLI. This is useful for:

- **Web Applications**: Build visual agent builders
- **IDE Extensions**: Create plugins for VSCode, JetBrains, etc.
- **Automation**: Generate agents in CI/CD pipelines
- **Learning Platforms**: Provide interactive agent creation
- **Custom Tools**: Integrate agent generation into your workflow

### Key Features

- 🚀 **Simple REST API** - Just POST JSON, get Python code
- 🔧 **Customizable** - Add custom tools/functions and environment variables
- 🌐 **CORS Enabled** - Works with web frontends
- 📖 **Self-Documenting** - Built-in Swagger/OpenAPI docs
- 🔓 **Public API** - No authentication required

## Quick Start

### 1. Start the API Server

```bash
# Install agent-starter-pack
pip install agent-starter-pack

# Start API server
agent-starter-pack-api

# Server starts at http://localhost:8080
```

### 2. Make Your First Request

```bash
curl -X POST http://localhost:8080/api/v1/generate/agent \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-first-agent",
    "agent_type": "adk_a2a_base"
  }'
```

### 3. View Interactive Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## API Reference

### Base URL

```
http://localhost:8080
```

### Endpoints

#### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### `GET /`

Root endpoint with API information.

**Response:**
```json
{
  "service": "Agent Starter Pack API",
  "version": "0.1.0",
  "endpoints": {
    "generate_agent": "/api/v1/generate/agent",
    "health": "/health",
    "docs": "/docs"
  }
}
```

#### `POST /api/v1/generate/agent`

Generate agent.py code with custom configuration.

**Request Body Schema:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_name` | string | No | "my-agent" | Name of the agent project |
| `agent_type` | string | No | "adk_a2a_base" | Type of agent (`adk_a2a_base`, `adk_base`) |
| `tools` | array | No | [] | Custom tools/functions (see below) |
| `env_vars` | array | No | [] | Custom environment variables (see below) |
| `agent_description` | string | No | null | Description of what the agent does |
| `agent_instruction` | string | No | null | System instruction for the agent |

**Tool Definition Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Function name (valid Python identifier) |
| `description` | string | Yes | What the tool does |
| `parameters` | string | Yes | Function parameters (e.g., "query: str") |
| `implementation` | string | Yes | Function body (indented with 4 spaces) |

**Environment Variable Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Variable name (uppercase recommended) |
| `default_value` | string | Yes | Default value if not set |
| `description` | string | No | Description of the variable |

**Response:**
```json
{
  "code": "# Copyright 2025 Google LLC\n...",
  "filename": "agent.py",
  "agent_type": "adk_a2a_base"
}
```

**Status Codes:**

- `200 OK` - Successfully generated code
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Generation failed

## Integration Examples

### Example 1: Basic Agent Generation

**Request:**
```bash
curl -X POST http://localhost:8080/api/v1/generate/agent \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "weather-agent",
    "agent_type": "adk_a2a_base",
    "agent_description": "A helpful weather information assistant",
    "agent_instruction": "Provide accurate weather information for any location."
  }'
```

**Response:**
```json
{
  "code": "# Copyright 2025 Google LLC\n# ...\n\nfrom google.adk.agents import Agent\nfrom google.adk.models.lite_llm import LiteLlm\n...",
  "filename": "agent.py",
  "agent_type": "adk_a2a_base"
}
```

### Example 2: Custom Tools

**Request:**
```json
{
  "project_name": "calculator-agent",
  "agent_type": "adk_a2a_base",
  "tools": [
    {
      "name": "add",
      "description": "Add two numbers",
      "parameters": "a: float, b: float",
      "implementation": "    return str(a + b)"
    },
    {
      "name": "multiply",
      "description": "Multiply two numbers",
      "parameters": "a: float, b: float",
      "implementation": "    return str(a * b)"
    }
  ]
}
```

### Example 3: Custom Environment Variables

**Request:**
```json
{
  "project_name": "api-agent",
  "agent_type": "adk_a2a_base",
  "env_vars": [
    {
      "name": "API_KEY",
      "default_value": "your-api-key-here",
      "description": "API key for external service"
    },
    {
      "name": "API_ENDPOINT",
      "default_value": "https://api.example.com",
      "description": "API endpoint URL"
    }
  ]
}
```

### Example 4: Python Client

```python
import requests

def generate_agent(project_name, tools=None, env_vars=None):
    """Generate agent code using the API."""
    response = requests.post(
        "http://localhost:8080/api/v1/generate/agent",
        json={
            "project_name": project_name,
            "agent_type": "adk_a2a_base",
            "tools": tools or [],
            "env_vars": env_vars or [],
        }
    )
    response.raise_for_status()
    return response.json()["code"]

# Example usage
code = generate_agent(
    project_name="stock-agent",
    tools=[
        {
            "name": "get_stock_price",
            "description": "Get current stock price",
            "parameters": "symbol: str",
            "implementation": '    return f"${symbol}: $123.45"'
        }
    ],
    env_vars=[
        {
            "name": "STOCK_API_KEY",
            "default_value": "your-key",
            "description": "Stock API key"
        }
    ]
)

# Save to file
with open("agent.py", "w") as f:
    f.write(code)

print("Agent generated successfully!")
```

### Example 5: JavaScript/TypeScript

```typescript
interface Tool {
  name: string;
  description: string;
  parameters: string;
  implementation: string;
}

interface EnvVar {
  name: string;
  default_value: string;
  description?: string;
}

async function generateAgent(
  projectName: string,
  tools?: Tool[],
  envVars?: EnvVar[]
): Promise<string> {
  const response = await fetch('http://localhost:8080/api/v1/generate/agent', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      project_name: projectName,
      agent_type: 'adk_a2a_base',
      tools: tools || [],
      env_vars: envVars || [],
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();
  return data.code;
}

// Example usage
const code = await generateAgent('my-agent', [
  {
    name: 'search',
    description: 'Search for information',
    parameters: 'query: str',
    implementation: '    return f"Results for: {query}"',
  },
]);

console.log('Generated agent code:', code);
```

### Example 6: Web Frontend (React)

```jsx
import React, { useState } from 'react';

function AgentGenerator() {
  const [projectName, setProjectName] = useState('');
  const [generatedCode, setGeneratedCode] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/v1/generate/agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_name: projectName,
          agent_type: 'adk_a2a_base',
        }),
      });

      const data = await response.json();
      setGeneratedCode(data.code);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Agent Code Generator</h1>
      <input
        type="text"
        placeholder="Project Name"
        value={projectName}
        onChange={(e) => setProjectName(e.target.value)}
      />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Agent'}
      </button>
      {generatedCode && (
        <pre>
          <code>{generatedCode}</code>
        </pre>
      )}
    </div>
  );
}

export default AgentGenerator;
```

## Best Practices

### 1. Error Handling

Always handle errors properly:

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    code = response.json()["code"]
except requests.exceptions.RequestException as e:
    print(f"API error: {e}")
```

### 2. Tool Implementation

Tool implementation must be indented with 4 spaces:

```json
{
  "name": "my_tool",
  "implementation": "    # This is correct (4 spaces)\n    return 'result'"
}
```

### 3. Environment Variable Naming

Use uppercase for environment variable names:

```json
{
  "name": "API_KEY",  // Good
  "name": "api_key"   // Works but not conventional
}
```

### 4. Validation

Validate inputs before sending to the API:

```python
def validate_tool(tool):
    """Validate tool definition."""
    required = ["name", "description", "parameters", "implementation"]
    if not all(key in tool for key in required):
        raise ValueError(f"Tool missing required fields: {required}")

    # Check if name is valid Python identifier
    if not tool["name"].isidentifier():
        raise ValueError(f"Invalid tool name: {tool['name']}")
```

### 5. Rate Limiting

If deploying publicly, consider implementing rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/generate/agent")
@limiter.limit("10/minute")  # 10 requests per minute
async def generate_agent(...):
    ...
```

## Troubleshooting

### API Server Won't Start

**Problem:** Port 8080 already in use

**Solution:** Use a different port
```bash
uvicorn agent_starter_pack.api.main:app --port 8081
```

### CORS Errors in Browser

**Problem:** CORS blocked by browser

**Solution:** API already has CORS enabled. If still blocked, check:
- Using `http://localhost:8080` not `http://127.0.0.1:8080`
- Browser security settings
- Proxy/firewall configuration

### Generated Code Has Syntax Errors

**Problem:** Tool implementation not indented correctly

**Solution:** Ensure 4-space indentation:
```json
{
  "implementation": "    return value"  // Must start with 4 spaces
}
```

### Request Timeout

**Problem:** API takes too long to respond

**Solution:**
- Check server logs for errors
- Simplify request (fewer tools)
- Increase client timeout

### Invalid Agent Type

**Problem:** `400 Bad Request: Unsupported agent type`

**Solution:** Use supported types:
- `adk_a2a_base` (recommended)
- `adk_base`

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install agent-starter-pack

EXPOSE 8080
CMD ["agent-starter-pack-api"]
```

### Environment Variables

```bash
# Optional configuration
export UVICORN_HOST=0.0.0.0
export UVICORN_PORT=8080
export UVICORN_WORKERS=4  # For production
```

### Health Monitoring

Monitor the `/health` endpoint:

```bash
curl http://localhost:8080/health
```

Expected response: `{"status": "healthy"}`

## Support

- **Documentation**: http://localhost:8080/docs
- **GitHub Issues**: https://github.com/GoogleCloudPlatform/agent-starter-pack/issues
- **API README**: `agent_starter_pack/api/README.md`

## License

Apache 2.0 - See LICENSE file for details
