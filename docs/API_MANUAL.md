# Agent Starter Pack API - User Manual v2.0

Complete guide for using the Agent Starter Pack API to generate complete AI agent projects from web UIs.

## Overview

The Agent Starter Pack API has been redesigned for **UI integration**. Instead of requiring users to write code, it accepts simple inputs (agent name, description, prompt, tools) and returns a complete project with downloadable zip file and optional Git repository.

### Key Changes in v2.0

- ✅ **Simpler Input**: No need to write tool implementations
- ✅ **Full Project**: Returns complete project (not just agent.py)
- ✅ **Zip Download**: Downloadable zip file of the entire project
- ✅ **Git Repository**: Optional Git repository creation
- ✅ **UI-Friendly**: Designed for web frontend integration

## Quick Start

### 1. Start the API Server

```bash
uv run agent-starter-pack-api
# Server starts at http://localhost:8080
```

### 2. Generate a Project

```bash
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "weather-agent",
    "description": "An agent that provides weather information",
    "prompt": "You are a helpful weather assistant",
    "tools": [
      {"name": "get_weather", "description": "Get weather for a location"},
      {"name": "get_forecast", "description": "Get weather forecast"}
    ]
  }'
```

### 3. Download the ZIP

```bash
curl -O http://localhost:8080/downloads/weather-agent.zip
```

## API Reference

### `POST /api/v1/generate/project`

Generate a complete agent project.

**Request:**
```json
{
  "agent_name": "my-agent",
  "description": "What the agent does",
  "prompt": "System instruction",
  "tools": [
    {"name": "tool_name", "description": "What it does"}
  ],
  "create_git_repo": false
}
```

**Response:**
```json
{
  "project_name": "my-agent",
  "download_url": "/downloads/my-agent.zip",
  "git_repo_url": null,
  "files_generated": 25,
  "message": "Project 'my-agent' generated successfully!"
}
```

## Integration Examples

See full examples in the documentation!

## License

Apache 2.0
