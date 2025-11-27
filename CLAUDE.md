# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **Agent Starter Pack** is a Python CLI package that generates production-ready GenAI agent projects. Originally designed for Google Cloud, the project is being extended to support on-premise deployment with local infrastructure alternatives. It uses a sophisticated templating system based on Cookiecutter and Jinja2 to scaffold complete agent projects with infrastructure, CI/CD, and deployment configurations.

Key capabilities:
- Generate agent projects from templates (`uvx agent-starter-pack create`)
- Enhance existing projects with deployment infrastructure (`uvx agent-starter-pack enhance`)
- Set up CI/CD pipelines for GitHub Actions or Cloud Build (`agent-starter-pack setup-cicd`)
- **[Partially Complete]** On-premise deployment with local LLMs, storage, and vector databases
  - ✅ LLM integration validated (ADK + LiteLLM with OpenAI-compatible endpoints)
  - 🚧 Storage, vector databases, and observability in progress

## Development Commands

### Testing
```bash
# Run all tests
make test

# Run tests for templated agents
make test-templated-agents

# Test specific agent/deployment combination
_TEST_AGENT_COMBINATION="adk_base,cloud_run,--session-type,in_memory" make test-templated-agents

# Run E2E deployment tests (requires .env setup)
make test-e2e
```

### Linting
```bash
# Lint CLI and test code
make lint

# Lint generated agent templates (skip mypy for speed)
SKIP_MYPY=1 make lint-templated-agents

# Lint specific combination
SKIP_MYPY=1 _TEST_AGENT_COMBINATION="adk_base,agent_engine" make lint-templated-agents
```

### Installation & Dependencies
```bash
# Install dependencies with uv
make install

# Generate lock files for templates
make generate-lock
```

### Documentation
```bash
# Run local documentation server
make docs-dev
# Access at http://localhost:5173
```

### Testing a Template Creation
```bash
# Test creating a project from templates
uv run agent-starter-pack create myagent-$(date +%s) --output-dir target
```

## Architecture

### Multi-Layer Template System

The project uses a 4-layer template architecture where later layers override earlier ones:

1. **Base Template** (`agent_starter_pack/base_template/`) - Core structure applied to ALL projects
2. **Deployment Targets** (`agent_starter_pack/deployment_targets/`) - Environment-specific overrides
   - `cloud_run/` - Cloud Run deployment files
   - `agent_engine/` - Agent Engine deployment files
3. **Frontend Types** (`agent_starter_pack/frontends/`) - UI-specific files
   - `adk_live_react/` - React frontend for multimodal Live API agents
4. **Agent Templates** (`agent_starter_pack/agents/`) - Individual agent implementations
   - `adk_base/` - ReAct agent using Google's Agent Development Kit
   - `adk_a2a_base/` - ADK agent with Agent2Agent protocol support
   - `agentic_rag/` - RAG agent with Vertex AI Search/Vector Search
   - `langgraph_base/` - ReAct agent using LangChain's LangGraph
   - `adk_live/` - Real-time multimodal agent with audio/video/text

### Template Processing Flow

1. User runs `agent-starter-pack create <name>`
2. CLI (`agent_starter_pack/cli/commands/create.py`) orchestrates the process
3. Template processor (`agent_starter_pack/cli/utils/template.py`) applies layers:
   - Copy base template
   - Overlay deployment target files
   - Overlay frontend files (if applicable)
   - Overlay agent-specific files
4. Cookiecutter renders Jinja2 templates using variables from `cookiecutter.json`
5. File/directory names with Jinja2 conditionals are processed
6. Generated project appears in output directory

### CLI Structure

- `agent_starter_pack/cli/main.py` - Main CLI entrypoint
- `agent_starter_pack/cli/commands/` - Command implementations
  - `create.py` - Create new agent projects
  - `enhance.py` - Add deployment infrastructure to existing projects
  - `setup_cicd.py` - Configure CI/CD pipelines
  - `register_gemini_enterprise.py` - Register Gemini Enterprise
  - `list.py` - List available agent templates
- `agent_starter_pack/cli/utils/` - Utility modules
  - `template.py` - Template processing logic
  - `gcp.py` - Google Cloud Platform interactions
  - `cicd.py` - CI/CD setup utilities
  - `remote_template.py` - Remote template fetching

## On-Premise Deployment (Partially Complete)

### Overview

The project is being extended to support on-premise deployment as an alternative to Google Cloud. This allows running agents with local infrastructure while preserving the ADK (Agent Development Kit) framework.

**Key Constraint**: The ADK framework itself remains unchanged. Only the infrastructure and Google Cloud services are replaced with on-premise alternatives.

**Status**: ✅ Core LLM integration validated | 🚧 Storage, databases, and observability in progress

### Service Mapping

#### Current (Google Cloud) → Target (On-Premise)

**AI/ML Services:**
- Vertex AI / Gemini API → OpenAI-compatible LLM (vLLM, Ollama, LocalAI)
- Vertex AI Embeddings → Sentence Transformers, HuggingFace Embeddings
- Vertex AI Search → Chroma, Weaviate, Qdrant, pgvector
- Vertex AI Vector Search → Same local vector databases
- Vertex AI Ranking → Local cross-encoder models

**Storage Services:**
- Cloud Storage (GCS) → MinIO or local filesystem
- Cloud SQL → Local PostgreSQL
- BigQuery → Pandas, DuckDB, or Polars
- Artifact Registry → Local Docker registry

**Infrastructure:**
- Cloud Run → Docker Compose or Kubernetes
- Agent Engine → Docker with custom HTTP server
- Cloud Build → Jenkins, GitLab CI, or local CI/CD

**Observability:**
- Cloud Logging → File-based logging, Loki, or ELK
- Cloud Trace → Jaeger or Zipkin
- Cloud Monitoring → Prometheus + Grafana

**Security:**
- Secret Manager → Environment variables, .env files, or Vault
- Cloud IAM → Application-level auth, API keys, or mTLS

### New Deployment Target: `on_premise`

A new deployment target is being created at `agent_starter_pack/deployment_targets/on_premise/` with:
- Docker Compose configuration
- Local service initialization
- Environment variable templates
- Alternative storage and database implementations

### ADK + OpenAI-Compatible LLM Integration ✅ VALIDATED

**Key Finding**: ADK has built-in support for OpenAI-compatible endpoints via `google.adk.models.lite_llm.LiteLlm`.

**Solution**:
```python
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent

# Create LiteLlm instance with OpenAI-compatible endpoint
llm = LiteLlm(
    model=os.getenv("LLM_MODEL_NAME"),      # e.g., "xai/grok-4-1-fast"
    api_key=os.getenv("LLM_API_KEY"),
    api_base=os.getenv("LLM_ENDPOINT_URL"), # e.g., "https://api.x.ai/v1"
)

# Pass LiteLlm instance directly to Agent
agent = Agent(
    name="root_agent",
    model=llm,  # Use LiteLlm instance, not string!
    instruction="...",
    tools=[...],
)
```

**Supported Providers** (via LiteLLM):
- **Local**: vLLM, Ollama, Text Generation Inference, LocalAI
- **Cloud**: OpenAI, X.AI, Anthropic, Azure OpenAI, Cohere, etc.
- **100+ total providers** through LiteLLM's unified interface

**No Custom Wrapper Needed**: ADK's native `LiteLlm` class handles all provider compatibility internally.

**Tested Successfully**: Validated with X.AI Grok endpoint on 2025-01-26.

### Key Files for On-Premise Work

**Base Template Modifications:**
- `app_utils/gcs.py` → Renamed to `app_utils/storage.py` with pluggable backends (MinIO, local)
- `app_utils/telemetry.py` → Updated to use local exporters (Jaeger, file logging)

**New Configuration Files:**
- `docker-compose.yml` - Multi-service orchestration
- `.env.example` - Environment variable template
- `config/local.yaml` - Local deployment configuration

**CLI Updates:**
- `cli/commands/create.py` - Add `on_premise` deployment target
- `cli/commands/enhance.py` - Support on-premise enhancement
- `cli/utils/gcp.py` → May need refactoring to `cli/utils/infrastructure.py`

### Environment Variables for On-Premise

New environment variables to support:
- `LLM_ENDPOINT_URL` - OpenAI-compatible LLM endpoint
- `LLM_MODEL_NAME` - Local model name (e.g., llama-3.1, mistral)
- `EMBEDDING_ENDPOINT_URL` - Local embedding service
- `VECTOR_DB_TYPE` - Vector database type (chroma, weaviate, qdrant, pgvector)
- `VECTOR_DB_URL` - Vector database connection string
- `STORAGE_TYPE` - Storage backend (minio, local, s3)
- `STORAGE_ENDPOINT_URL` - MinIO or S3-compatible endpoint
- `DATABASE_URL` - PostgreSQL connection string
- `TRACING_ENDPOINT` - Jaeger or Zipkin endpoint

### Testing On-Premise Changes

When working on on-premise features:
1. Test with local services (Docker Compose test environment)
2. Verify ADK framework compatibility with OpenAI-compatible models
3. Test both GCP and on-premise deployment targets to ensure no regressions
4. Update tests to support both environments

### Reference Documents

- `CHECKLIST.md` - Comprehensive migration checklist (11 phases, all services)
- `QUICK_START.md` - Quick start guide for local deployment
- `docs/guide/on-premise-setup.md` - Detailed on-premise setup guide (to be created)

## Critical Jinja2 Templating Rules

The templates use Jinja2 extensively. Understanding these patterns is essential:

### Block Balancing
Every opening block MUST have a closing block:
- `{% if ... %}` requires `{% endif %}`
- `{% for ... %}` requires `{% endfor %}`
- `{% raw %}` requires `{% endraw %}`

### Variable Usage
- **Substitution**: `{{ cookiecutter.project_name }}`
- **Logic**: `{% if cookiecutter.deployment_target == 'cloud_run' %}`

### Whitespace Control
Jinja2 is whitespace-sensitive. Use hyphens to control newlines:
- `{%-` removes whitespace before the tag
- `-%}` removes whitespace after the tag

Example for conditional imports:
```jinja
from opentelemetry.sdk.trace import TracerProvider
{% if cookiecutter.session_type == "agent_engine" -%}
from vertexai import agent_engines
{% endif %}

from app.app_utils.gcs import create_bucket_if_not_exists
```

### End-of-File Newlines
Ruff requires exactly ONE newline at end of every file. For templates with conditionals at end:
```jinja
agent_engine = AgentEngineApp(project_id=project_id)
{%- endif %}
```

## Testing Template Changes

**CRITICAL**: Template changes can affect multiple agent/deployment combinations. Always test across combinations.

### Common Test Combinations
```bash
# Cloud Run with different agents
SKIP_MYPY=1 _TEST_AGENT_COMBINATION="adk_base,cloud_run,--session-type,in_memory" make lint-templated-agents
SKIP_MYPY=1 _TEST_AGENT_COMBINATION="adk_live,cloud_run,--session-type,in_memory" make lint-templated-agents

# Agent Engine with different agents
SKIP_MYPY=1 _TEST_AGENT_COMBINATION="adk_base,agent_engine" make lint-templated-agents
SKIP_MYPY=1 _TEST_AGENT_COMBINATION="langgraph_base,agent_engine" make lint-templated-agents

# With data ingestion
SKIP_MYPY=1 _TEST_AGENT_COMBINATION="agentic_rag,cloud_run,--data-ingestion" make lint-templated-agents
```

### Files Most Prone to Linting Issues
1. `agent_engine_app.py` (deployment_targets/agent_engine/) - Multiple conditional paths
2. `fast_api_app.py` (deployment_targets/cloud_run/) - Conditional imports and nested logic
3. Any file with `{% if cookiecutter.agent_name == "..." %}` - Different agents trigger different code paths

### Debugging Generated Files
When lint fails:
```bash
# Find generated project (in target/ directory)
ls target/

# Check the problematic file
cat target/project-name/path/to/file.py

# Find source template
find agent_starter_pack -name "file.py" -type f
```

## CI/CD Dual Implementation

The project maintains parallel CI/CD implementations. **Any CI/CD change must be applied to BOTH**:

- **GitHub Actions**: `.github/workflows/` - Uses `${{ vars.VAR_NAME }}`
- **Google Cloud Build**: `.cloudbuild/` - Uses `${_VAR_NAME}`

Variables and secrets must be configured for both systems in Terraform.

## Terraform Infrastructure

### Unified Service Account Pattern
- Uses single `app_sa` service account across all deployment targets
- Do NOT create target-specific service accounts
- Define roles in `app_sa_roles`

### Resource Referencing
For resources created with `for_each`:
```hcl
# Creation
resource "google_service_account" "app_sa" {
  for_each   = local.deploy_project_ids
  account_id = "${var.project_name}-app"
}

# Reference in module
service_account = google_service_account.app_sa["staging"].email
```

## Python Configuration

- **Python version**: 3.10+
- **Package manager**: `uv` (preferred) or `pip`
- **Build system**: Hatchling
- **Linting**: Ruff (formatting + linting) + mypy (type checking)
- **Testing**: pytest with parallel execution support

### Linting Configuration
- Line length: 88 characters
- Target: Python 3.11
- Includes: `agent_starter_pack/cli/**/*.py`, `tests/**/*.py`
- Excludes: Agent templates (`agent_starter_pack/agents/**/*.py`)

## Development Workflow

### Making Template Changes
1. Identify the correct layer (base, deployment target, frontend, or agent)
2. Modify template files with proper Jinja2 syntax
3. Test the specific combination you're working on
4. Test related combinations (same deployment + different agents)
5. Test alternate code paths (different deployments + session types)

### Adding New Features
1. Update base template if feature applies to all projects
2. Add deployment-specific overrides in `deployment_targets/` if needed
3. Update agent templates if feature is agent-specific
4. Update documentation in `docs/`
5. Test multiple agent/deployment combinations

### Modifying CLI Commands
1. CLI commands are in `agent_starter_pack/cli/commands/`
2. Utilities are in `agent_starter_pack/cli/utils/`
3. Run `make lint` to validate changes
4. Run `make test` to ensure tests pass

## Important Context Files

- `GEMINI.md` - Detailed coding guidelines for AI agents (contains Jinja2 patterns, linting rules, PR best practices)
- `CHECKLIST.md` - On-premise migration checklist with comprehensive service mapping
- `QUICK_START.md` - Quick start guide for local/on-premise deployment
- `llm.txt` - Project context for LLM consumption
- `CONTRIBUTING.md` - Contribution guidelines
- `README.md` - User-facing documentation

## Key Dependencies

- **click** - CLI framework
- **cookiecutter** - Template scaffolding
- **rich** - Terminal formatting
- **google-cloud-aiplatform** - Vertex AI integration
- **pyyaml** - Configuration parsing

## Common Gotchas

1. **Hardcoded URLs**: Always use relative paths for frontend connections
2. **Missing Conditionals**: Wrap agent-specific code in proper `{% if %}` blocks
3. **Whitespace in Imports**: Conditional imports require careful whitespace control to avoid linting errors
4. **Template Variable Scope**: Variables defined in `cookiecutter.json` are available as `cookiecutter.*`
5. **Cross-file Dependencies**: Changes to configuration files often require updates in multiple locations
