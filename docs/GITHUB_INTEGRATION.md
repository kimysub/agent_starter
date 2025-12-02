# GitHub Integration Guide

How to push generated agent projects to folders in a GitHub repository.

## Overview

The API uses a **folder-based approach** for GitHub integration:
- All agents are pushed to **ONE fixed repository**
- Each agent gets a **unique numbered folder** (e.g., `my-agent-0042`)
- Perfect for **mono-repo pattern** and centralized management

**Benefits:**
- ✅ All agents in one place
- ✅ Easy version control and history
- ✅ Shared CI/CD pipeline
- ✅ Better for organizations
- ✅ No need to create multiple repositories

## Setup

### 1. Create Fixed Repository on GitHub

First, create a repository that will hold all your agents:

**On GitHub.com:**
1. Go to https://github.com/new
2. Repository name: `agents-collection` (or your preferred name)
3. Choose public or private
4. Initialize with README (optional)
5. Click "Create repository"

**On GitHub Enterprise:**
1. Go to `https://your-github-enterprise.com` and create a new repository
2. Follow the same steps as above

### 2. Create GitHub Personal Access Token

**For GitHub.com:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: `agent-starter-pack-api`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click "Generate token"
6. **Save the token** - you won't see it again!

**For GitHub Enterprise:**
1. Go to `https://your-github-enterprise.com/settings/tokens`
2. Follow the same steps as above

### 3. Configure API with Token

**Option A: Environment Variable (Recommended)**
```bash
export GITHUB_TOKEN=ghp_your_token_here
agent-starter-pack-api
```

**Option B: Pass in Request**
```bash
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "my-agent",
    "description": "My agent",
    "prompt": "You are helpful",
    "create_git_repo": true,
    "git_repo_name": "agents-collection",
    "github_token": "ghp_your_token_here"
  }'
```

## Usage Examples

### Example 1: Push to Personal Repository on GitHub.com

```bash
# Set token (do this once)
export GITHUB_TOKEN=ghp_your_token_here

# Generate and push agent
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "customer-support-bot",
    "description": "A customer support chatbot",
    "prompt": "You help customers with questions",
    "create_git_repo": true,
    "git_repo_name": "agents-collection"
  }'
```

**Success Response:**
```json
{
  "project_name": "customer-support-bot",
  "download_url": "/downloads/customer-support-bot.zip",
  "git_repo_url": "https://github.com/yourusername/agents-collection/tree/main/customer-support-bot-0042",
  "git_folder_name": "customer-support-bot-0042",
  "files_generated": 23,
  "message": "Project 'customer-support-bot' generated successfully!"
}
```

**Result:** Agent pushed to folder `customer-support-bot-0042` in your `agents-collection` repository

### Example 2: Push to Organization Repository

```bash
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "sales-bot",
    "description": "Sales assistant",
    "prompt": "You help with sales",
    "create_git_repo": true,
    "git_repo_name": "company-agents",
    "github_org": "my-company"
  }'
```

**Result:** Agent pushed to `https://github.com/my-company/company-agents/tree/main/sales-bot-0001`

### Example 3: Push to GitHub Enterprise

```bash
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "internal-agent",
    "description": "Internal company agent",
    "prompt": "You help employees",
    "create_git_repo": true,
    "git_repo_name": "enterprise-agents",
    "github_enterprise_url": "https://github.mycompany.com",
    "github_org": "engineering"
  }'
```

**Result:** Agent pushed to `https://github.mycompany.com/engineering/enterprise-agents/tree/main/internal-agent-0123`

### Example 4: Multiple Agents in Same Repository

```bash
# Push first agent
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "agent-one",
    "description": "First agent",
    "prompt": "You are agent one",
    "create_git_repo": true,
    "git_repo_name": "all-agents"
  }'

# Push second agent to same repository
curl -X POST http://localhost:8080/api/v1/generate/project \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "agent-two",
    "description": "Second agent",
    "prompt": "You are agent two",
    "create_git_repo": true,
    "git_repo_name": "all-agents"
  }'
```

**Result:**
- `https://github.com/user/all-agents/tree/main/agent-one-0001`
- `https://github.com/user/all-agents/tree/main/agent-two-0002`

Both agents in the same repository, different folders!

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_name` | string | Yes | Name of the agent (used for folder name) |
| `description` | string | Yes | Agent description |
| `prompt` | string | Yes | System prompt |
| `create_git_repo` | boolean | No | Set to `true` to push to GitHub |
| `git_repo_name` | string | Yes* | Fixed repository name to push to |
| `github_token` | string | No** | GitHub PAT (or use `GITHUB_TOKEN` env var) |
| `github_org` | string | No | Organization name (defaults to user account) |
| `github_enterprise_url` | string | No | GitHub Enterprise URL (defaults to github.com) |

\*Required if `create_git_repo` is `true`
\*\*Required if `GITHUB_TOKEN` environment variable is not set

## How It Works

When you set `create_git_repo: true`, the API:

1. ✅ Generates the complete agent project locally
2. ✅ Clones the existing GitHub repository
3. ✅ Creates a unique folder name (e.g., `agent-name-0042`)
4. ✅ Copies all project files into that folder
5. ✅ Commits the changes with message: `"Add agent: agent-name-0042"`
6. ✅ Pushes to GitHub
7. ✅ Returns folder URL

**Folder Naming:**
- Format: `{agent_name}-{random_4_digits}`
- Example: `my-agent-0042`, `chatbot-1234`, `assistant-0001`
- Random suffix ensures uniqueness

## Repository Structure

After pushing multiple agents, your repository will look like:

```
agents-collection/
├── README.md
├── agent-one-0001/
│   ├── app/
│   │   └── agent.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   └── README.md
├── agent-two-0002/
│   ├── app/
│   │   └── agent.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   └── README.md
└── agent-three-0003/
    ├── app/
    │   └── agent.py
    ├── Dockerfile
    ├── docker-compose.yml
    ├── pyproject.toml
    └── README.md
```

Each folder is a complete, independent agent project!

## Troubleshooting

### Error: "GitHub token is required"

**Solution:** Set the `GITHUB_TOKEN` environment variable or pass `github_token` in the request.

### Error: "Failed to push to GitHub: repository not found"

**Causes:**
- The repository doesn't exist
- Repository name is incorrect
- Organization doesn't exist
- Token doesn't have access to the repository

**Solution:**
1. Verify the repository exists on GitHub
2. Check repository name spelling
3. Ensure token has access to the repository

### Error: "Failed to push to GitHub: permission denied"

**Causes:**
- Token doesn't have `repo` scope
- Token expired
- Organization requires SSO authorization

**Solution:** Create a new token with correct scopes and SSO authorization if needed.

### Error: "git_repo_name is required when create_git_repo is true"

**Solution:** Include `git_repo_name` parameter in your request when `create_git_repo` is `true`.

### Error: "Failed to push to GitHub: repository is empty"

**Cause:** The repository was just created and has no commits yet.

**Solution:** Initialize the repository with at least one commit (e.g., add a README file).

## Security Best Practices

### ✅ DO:
- Use environment variables for tokens
- Use private repositories for sensitive agents
- Rotate tokens regularly
- Use organization tokens for org repos
- Enable SSO if required by your organization
- Limit token scope to `repo` only

### ❌ DON'T:
- Commit tokens to code
- Share tokens in chat/email
- Use tokens with more permissions than needed
- Store tokens in browser localStorage (for web UIs)
- Use personal tokens for production (use org tokens)

## Integration Examples

### Python Client

```python
import os
import requests

def create_and_push_agent(agent_name, description, prompt, repo_name):
    response = requests.post(
        "http://localhost:8080/api/v1/generate/project",
        json={
            "agent_name": agent_name,
            "description": description,
            "prompt": prompt,
            "create_git_repo": True,
            "git_repo_name": repo_name,
            # Token from environment (secure!)
            "github_token": os.getenv("GITHUB_TOKEN"),
        }
    )
    response.raise_for_status()
    return response.json()

result = create_and_push_agent(
    "support-bot",
    "Customer support chatbot",
    "You help customers",
    "agents-collection"
)

print(f"✅ Agent pushed to: {result['git_repo_url']}")
print(f"📁 Folder name: {result['git_folder_name']}")
print(f"📦 Download: http://localhost:8080{result['download_url']}")
```

### JavaScript/React

```javascript
async function createAndPushAgent(agentName, description, prompt, repoName) {
  const response = await fetch('http://localhost:8080/api/v1/generate/project', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent_name: agentName,
      description,
      prompt,
      create_git_repo: true,
      git_repo_name: repoName,
      // Get token from secure backend, NOT from frontend!
      github_token: await getTokenFromBackend(),
    }),
  });

  return await response.json();
}

// Usage
const result = await createAndPushAgent(
  'my-agent',
  'My helpful agent',
  'You assist users',
  'agents-collection'
);

console.log(`✅ Agent pushed to: ${result.git_repo_url}`);
console.log(`📁 Folder: ${result.git_folder_name}`);
```

## Mono-Repo Benefits

Using a single repository for all agents provides:

1. **Centralized Management**
   - All agents in one place
   - Easy to browse and search
   - Unified version control

2. **Shared Infrastructure**
   - One CI/CD pipeline for all agents
   - Shared deployment scripts
   - Common configuration

3. **Better Collaboration**
   - Team can see all agents
   - Easy code review across agents
   - Shared documentation

4. **Cost Efficiency**
   - No need to manage multiple repositories
   - Simpler access control
   - Less overhead

## GitHub Enterprise Specific Notes

### Custom SSL Certificates

If your GitHub Enterprise uses custom SSL certificates:

```bash
# Add certificate to system trust store first
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
agent-starter-pack-api
```

### Self-Signed Certificates (NOT RECOMMENDED for production)

```python
# Only for testing!
import requests
requests.packages.urllib3.disable_warnings()
```

## License

Apache 2.0
