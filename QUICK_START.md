# Quick Start: On-Premise Deployment

This guide will help you get started with running the Agent Starter Pack on-premise using local infrastructure instead of Google Cloud services.

## Prerequisites

- **Docker & Docker Compose** (v2.0+)
- **Python 3.10+** with `uv` or `pip`
- **Git**
- **8GB RAM minimum** (16GB recommended for LLM inference)
- **GPU optional** (NVIDIA GPU with CUDA for faster LLM inference)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Agent Application                    │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │   FastAPI  │  │   ADK Agent  │  │  Agent Engine    │    │
│  │  (HTTP)    │→ │  Framework   │→ │  (optional)      │    │
│  └────────────┘  └──────────────┘  └──────────────────┘    │
└───────────┬─────────────────────────────────────────────────┘
            │
            ↓
┌───────────────────────────────────────────────────────────────┐
│                    Local Infrastructure                        │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────┐   │
│  │   LLM Server │ │   Vector DB  │ │   PostgreSQL        │   │
│  │ (OpenAI API  │ │  (Chroma/    │ │  (Session State)    │   │
│  │  Compatible) │ │   Weaviate)  │ │                     │   │
│  └──────────────┘ └──────────────┘ └─────────────────────┘   │
│                                                                │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────┐   │
│  │    MinIO     │ │    Jaeger    │ │   File Logging      │   │
│  │  (Storage)   │ │  (Tracing)   │ │  (Observability)    │   │
│  └──────────────┘ └──────────────┘ └─────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

---

## Quick Start Options

### Option A: Minimal Setup (Fastest - 5 minutes)
Perfect for development and testing. Uses embedded/simple services.

### Option B: Full Stack (Production-Like - 15 minutes)
Complete setup with all services for production simulation.

---

## Option A: Minimal Setup

This setup uses the simplest possible configuration with minimal dependencies.

### Step 1: Set Up OpenAI-Compatible LLM Endpoint

You have several options for OpenAI-compatible LLM endpoints:

**Option 1: Use a Cloud Provider (Easiest)**
```bash
# Use OpenAI, Azure OpenAI, or any OpenAI-compatible service
# Just get your API key and endpoint URL
# Example providers:
# - OpenAI: https://api.openai.com/v1
# - Azure OpenAI: https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT
# - Together AI: https://api.together.xyz/v1
# - Anyscale: https://api.endpoints.anyscale.com/v1
```

**Option 2: Local LLM with vLLM (Recommended for on-premise)**
```bash
# Install vLLM (requires Python 3.10+)
pip install vllm

# Start vLLM server with a model
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 \
  --port 8001 \
  --api-key "your-secret-key-here"

# Or run with Docker
docker run -d \
  --gpus all \
  -p 8001:8000 \
  -e VLLM_API_KEY="your-secret-key-here" \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3.1-8B-Instruct
```

**Option 3: Local LLM with Ollama**
```bash
# Install Ollama (simplest for testing)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
# Note: Ollama endpoint is http://localhost:11434/v1
# Ollama doesn't require an API key by default
```

**Option 4: Text Generation Inference (TGI)**
```bash
# Run Hugging Face TGI
docker run -d \
  --gpus all \
  -p 8001:80 \
  -e MODEL_ID="meta-llama/Llama-3.1-8B-Instruct" \
  ghcr.io/huggingface/text-generation-inference:latest
```

**Verify Your LLM Endpoint:**
```bash
# Test with curl (replace with your endpoint and API key)
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-here" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

### Step 2: Set Up PostgreSQL (Optional - for session state)

```bash
# Run PostgreSQL in Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=agent_db \
  -e POSTGRES_USER=agent_user \
  -p 5432:5432 \
  postgres:15-alpine

# Verify connection
docker exec -it postgres psql -U agent_user -d agent_db -c "SELECT version();"
```

### Step 3: Create Agent Project

```bash
# Clone the repository
git clone https://github.com/GoogleCloudPlatform/agent-starter-pack.git
cd agent-starter-pack

# Install dependencies
make install

# Create a new agent project with on-premise configuration
# Note: This will be updated when on_premise deployment target is implemented
uv run agent-starter-pack create my-local-agent --output-dir ./my-agent

cd my-agent
```

### Step 4: Configure Environment Variables

Create a `.env` file in your agent project:

```bash
cat > .env << 'EOF'
# LLM Configuration
# Option 1: Cloud provider (OpenAI, Azure, Together AI, etc.)
LLM_ENDPOINT_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
LLM_API_KEY=sk-your-api-key-here

# Option 2: Local vLLM or TGI
# LLM_ENDPOINT_URL=http://localhost:8001/v1
# LLM_MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
# LLM_API_KEY=your-secret-key-here

# Option 3: Ollama (no auth required)
# LLM_ENDPOINT_URL=http://localhost:11434/v1
# LLM_MODEL_NAME=llama3.1:8b
# LLM_API_KEY=not-needed

# Database Configuration
DATABASE_URL=postgresql://agent_user:mypassword@localhost:5432/agent_db

# Storage Configuration (Local filesystem)
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./data/storage

# Vector Database (Chroma - embedded mode)
VECTOR_DB_TYPE=chroma
VECTOR_DB_PATH=./data/chroma

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=./logs/agent.log

# Tracing (disabled for minimal setup)
ENABLE_TRACING=false

# Application Settings
APP_HOST=localhost
APP_PORT=8000
EOF
```

### Step 5: Update Agent Code for OpenAI-Compatible LLM (ADK + LiteLLM)

**✅ VALIDATED APPROACH**: Use ADK's built-in LiteLLM support for seamless OpenAI-compatible endpoint integration.

Edit your agent file (e.g., `app/agent.py`) to use ADK with LiteLLM:

```python
import os
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent
from google.adk.apps.app import App

# Create LiteLlm instance with OpenAI-compatible endpoint
# Works with 100+ providers: OpenAI, X.AI, vLLM, Ollama, Azure, etc.
llm = LiteLlm(
    model=os.getenv("LLM_MODEL_NAME"),      # e.g., "xai/grok-4-1-fast" or "llama3.1:8b"
    api_key=os.getenv("LLM_API_KEY"),       # API key (use "not-needed" for Ollama)
    api_base=os.getenv("LLM_ENDPOINT_URL"), # e.g., "http://localhost:8001/v1"
)

# Define your agent tools
def example_tool(query: str) -> str:
    """Example tool for the agent."""
    return f"Tool result for: {query}"

# Create ADK agent with LiteLlm instance
root_agent = Agent(
    name="root_agent",
    model=llm,  # Pass LiteLlm instance directly!
    instruction="You are a helpful AI assistant designed to provide accurate and useful information.",
    tools=[example_tool],
)

# Create the app
app = App(root_agent=root_agent, name="app")
```

**Key Points:**
- **No custom wrapper needed** - ADK has native LiteLLM support
- **100+ providers supported** through LiteLLM's unified interface
- **Same code** works with OpenAI, X.AI, vLLM, Ollama, Azure OpenAI, etc.
- Just change `LLM_ENDPOINT_URL`, `LLM_MODEL_NAME`, and `LLM_API_KEY` in `.env`
- **Tested and validated** with X.AI Grok endpoint

**Model Name Format:**
- **LiteLLM uses provider prefixes**: `xai/grok-4-1-fast`, `openai/gpt-4o-mini`, `ollama/llama3.1:8b`
- Check [LiteLLM docs](https://docs.litellm.ai/docs/providers) for provider-specific formats

### Step 6: Install Required Dependencies

```bash
# Add ADK, LiteLLM, and local dependencies
uv add google-adk google-generativeai litellm

# Add local storage and vector DB
uv add chromadb

# If using vector search/RAG
uv add sentence-transformers langchain-chroma
```

### Step 7: Run Your Agent

```bash
# Create required directories
mkdir -p ./data/storage ./data/chroma ./logs

# Run the agent locally
uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 8: Test Your Agent

```bash
# Test the agent endpoint
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello! Can you help me?"}]
  }'

# Or with explicit model specification
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello! Can you help me?"}],
    "model": "gpt-4o-mini"
  }'
```

---

## Option B: Full Stack Setup

This provides a complete production-like environment with all services.

### Step 1: Create Docker Compose Configuration

Create `docker-compose.yml` in your project root:

```yaml
version: '3.8'

services:
  # LLM Server (vLLM for production performance)
  vllm:
    image: vllm/vllm-openai:latest
    ports:
      - "8001:8000"
    environment:
      - HF_TOKEN=${HF_TOKEN}  # HuggingFace token for model download
      - VLLM_API_KEY=${VLLM_API_KEY:-secret-token-change-me}  # API key for authentication
    command: >
      --model meta-llama/Llama-3.1-8B-Instruct
      --dtype auto
      --max-model-len 8192
      --api-key ${VLLM_API_KEY:-secret-token-change-me}
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    # For CPU-only deployment, comment out deploy section and add:
    # environment:
    #   - VLLM_CPU_ONLY=1

  # PostgreSQL for session state
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=agent_db
      - POSTGRES_USER=agent_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-changeme}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent_user -d agent_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Weaviate for vector search
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8002:8080"
      - "50051:50051"
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
      - DEFAULT_VECTORIZER_MODULE=none
      - ENABLE_MODULES=text2vec-openai,text2vec-huggingface
      - CLUSTER_HOSTNAME=node1
    volumes:
      - weaviate_data:/var/lib/weaviate
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/.well-known/ready"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MinIO for object storage
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER:-minioadmin}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-minioadmin}
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Jaeger for distributed tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "6831:6831/udp"  # Jaeger agent (UDP)
      - "16686:16686"    # Jaeger UI
      - "14268:14268"    # Jaeger collector
      - "14250:14250"    # gRPC
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  # Grafana Loki for log aggregation
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - loki_data:/loki

  # Promtail for log collection
  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./logs:/var/log/agent
      - ./promtail-config.yaml:/etc/promtail/config.yaml
    command: -config.file=/etc/promtail/config.yaml
    depends_on:
      - loki

  # Grafana for observability dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - loki
      - jaeger

volumes:
  postgres_data:
  weaviate_data:
  minio_data:
  loki_data:
  grafana_data:
```

### Step 2: Create Promtail Configuration

Create `promtail-config.yaml`:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: agent_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: agent
          __path__: /var/log/agent/*.log
```

### Step 3: Create Environment Configuration

Create `.env` file:

```bash
# LLM Configuration
# For local vLLM (from docker-compose)
LLM_ENDPOINT_URL=http://localhost:8001/v1
LLM_MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
LLM_API_KEY=secret-token-change-me  # Must match VLLM_API_KEY in docker-compose

# Alternative: Use cloud provider
# LLM_ENDPOINT_URL=https://api.openai.com/v1
# LLM_MODEL_NAME=gpt-4o-mini
# LLM_API_KEY=sk-your-openai-api-key

# Embedding Configuration (can use same vLLM or separate service)
EMBEDDING_ENDPOINT_URL=http://localhost:8001/v1
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# Database Configuration
DATABASE_URL=postgresql://agent_user:changeme@localhost:5432/agent_db
POSTGRES_PASSWORD=changeme

# Storage Configuration (MinIO)
STORAGE_TYPE=minio
STORAGE_ENDPOINT_URL=http://localhost:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Vector Database Configuration
VECTOR_DB_TYPE=weaviate
VECTOR_DB_URL=http://localhost:8002

# Tracing Configuration
ENABLE_TRACING=true
TRACING_BACKEND=jaeger
JAEGER_ENDPOINT=http://localhost:14268/api/traces
OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=./logs/agent.log
LOKI_URL=http://localhost:3100

# Grafana Configuration
GRAFANA_PASSWORD=admin

# HuggingFace Token (for downloading models from HuggingFace)
HF_TOKEN=your_huggingface_token_here

# vLLM API Key (for securing the vLLM endpoint)
VLLM_API_KEY=secret-token-change-me  # Change this to a secure random string

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
```

### Step 4: Start All Services

```bash
# Create required directories
mkdir -p ./logs ./data/storage

# Start all infrastructure services
docker-compose up -d

# Wait for services to be healthy (may take 2-3 minutes)
docker-compose ps

# Check logs if any service fails
docker-compose logs -f
```

### Step 5: Initialize MinIO Buckets

```bash
# Install MinIO client
brew install minio/stable/mc  # macOS
# Or download from https://min.io/docs/minio/linux/reference/minio-mc.html

# Configure MinIO client
mc alias set local http://localhost:9000 minioadmin minioadmin

# Create required buckets
mc mb local/agent-logs
mc mb local/agent-data
mc mb local/vector-search
```

### Step 6: Update Agent Dependencies

Add required packages to `pyproject.toml`:

```toml
[project]
dependencies = [
    "google-adk>=0.1.0",  # ADK framework
    "google-generativeai>=0.8.0",  # Required by ADK
    "litellm>=1.0.0",  # For LiteLLM support
    "boto3>=1.28.0",  # For MinIO S3 compatibility
    "weaviate-client>=4.0.0",
    "sentence-transformers>=2.2.0",
    "psycopg2-binary>=2.9.0",
    "opentelemetry-exporter-jaeger>=1.20.0",
    "python-json-logger>=2.0.0",
]
```

Install dependencies:

```bash
uv sync
```

### Step 7: Update Agent Code

Create a configuration manager (`app/config.py`):

```python
import os
from typing import Literal

class Config:
    """Application configuration from environment variables"""

    # LLM Configuration
    LLM_ENDPOINT_URL: str = os.getenv("LLM_ENDPOINT_URL", "http://localhost:8001/v1")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "llama3.1:8b")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "token-abc123")

    # Storage Configuration
    STORAGE_TYPE: Literal["minio", "local", "s3"] = os.getenv("STORAGE_TYPE", "local")
    STORAGE_ENDPOINT_URL: str = os.getenv("STORAGE_ENDPOINT_URL", "http://localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "./data/storage")

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://agent_user:changeme@localhost:5432/agent_db")

    # Vector DB Configuration
    VECTOR_DB_TYPE: Literal["chroma", "weaviate", "qdrant"] = os.getenv("VECTOR_DB_TYPE", "chroma")
    VECTOR_DB_URL: str = os.getenv("VECTOR_DB_URL", "http://localhost:8002")

    # Observability
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "false").lower() == "true"
    JAEGER_ENDPOINT: str = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "./logs/agent.log")

config = Config()
```

Update agent initialization (`app/agent.py`):

```python
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent
from google.adk.apps.app import App
from app.config import config

# Initialize LiteLlm with configuration
# Works with vLLM, Ollama, cloud providers, etc.
llm = LiteLlm(
    model=config.LLM_MODEL_NAME,
    api_key=config.LLM_API_KEY,
    api_base=config.LLM_ENDPOINT_URL,
)

# Define agent tools
def example_tool(query: str) -> str:
    """Example tool."""
    return f"Result: {query}"

# Create ADK agent with LiteLlm
root_agent = Agent(
    name="root_agent",
    model=llm,  # Use LiteLlm instance
    instruction="You are a helpful AI assistant.",
    tools=[example_tool],
)

# Create the app
app = App(root_agent=root_agent, name="app")
```

### Step 8: Run Your Agent Application

```bash
# Source environment variables
export $(cat .env | xargs)

# Run the application
uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 9: Access Observability Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger UI**: http://localhost:16686
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

---

## Testing Your Setup

### Test 1: LLM Endpoint

```bash
# Test vLLM endpoint with API key
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-change-me" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "Say hello!"}],
    "max_tokens": 50
  }'

# For cloud providers (e.g., OpenAI)
# curl -X POST https://api.openai.com/v1/chat/completions \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer sk-your-api-key" \
#   -d '{
#     "model": "gpt-4o-mini",
#     "messages": [{"role": "user", "content": "Say hello!"}],
#     "max_tokens": 50
#   }'
```

### Test 2: Agent Endpoint

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What can you help me with?"}]
  }'
```

### Test 3: Vector Search (if using RAG)

```python
# Python test script
from weaviate import Client

client = Client("http://localhost:8002")
print(client.is_ready())  # Should return True
```

### Test 4: Storage (MinIO)

```bash
# Upload a test file
echo "Test content" > test.txt
mc cp test.txt local/agent-data/test.txt

# Verify upload
mc ls local/agent-data/
```

---

## Performance Optimization

### For LLM Inference

**GPU Acceleration:**
```bash
# Ensure NVIDIA drivers and Docker GPU support are installed
nvidia-smi

# vLLM will automatically use GPU if available
```

**Model Quantization (CPU):**
```bash
# Use quantized models for faster CPU inference
ollama pull llama3.1:8b-q4_K_M  # 4-bit quantization
```

**Batch Processing:**
```python
# Configure vLLM for batch processing
# In docker-compose.yml, add to vllm command:
# --max-num-batched-tokens 8192
# --max-num-seqs 256
```

### For Vector Search

**Weaviate Performance:**
```yaml
# In docker-compose.yml, add to weaviate environment:
- LIMIT_RESOURCES=false
- GOMEMLIMIT=4GiB
```

**Chroma Optimization:**
```python
# Use persistent directory mode with SSD
import chromadb
client = chromadb.PersistentClient(path="./data/chroma")
```

---

## Troubleshooting

### Issue: LLM Server Out of Memory

**Solution:**
```bash
# Option 1: Use a smaller model
# For vLLM:
vllm serve meta-llama/Llama-3.2-3B-Instruct  # Only 2GB

# For Ollama:
ollama pull llama3.2:3b

# Option 2: Use quantized model (Ollama)
ollama pull llama3.1:8b-q4_K_M

# Option 3: Reduce max model length (vLLM)
# In docker-compose.yml:
# --max-model-len 4096

# Option 4: Switch to cloud provider
# Update .env to use OpenAI, Azure, or other cloud provider
```

### Issue: Slow LLM Response Times

**Solution:**
```bash
# Option 1: Enable GPU acceleration (for local deployment)
nvidia-smi  # Check NVIDIA drivers

# Option 2: Use smaller context window
# Set max_tokens in requests to lower values

# Option 3: Use cloud provider for faster inference
# Update LLM_ENDPOINT_URL to use OpenAI, Azure OpenAI, or Together AI

# Option 4: Optimize vLLM settings
# vLLM is faster than Ollama for production workloads
# Add to vLLM command:
# --max-num-batched-tokens 8192
# --enable-prefix-caching
```

### Issue: API Authentication Failed

**Solution:**
```bash
# Verify LLM_API_KEY matches between .env and vLLM server
# For vLLM in docker-compose.yml:
echo $VLLM_API_KEY  # Should match LLM_API_KEY in .env

# For cloud providers, verify API key is valid
# OpenAI: starts with sk-
# Azure: check Azure portal for key

# Test authentication directly:
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "your-model", "messages": [{"role": "user", "content": "test"}]}'
```

### Issue: Vector DB Connection Failed

**Solution:**
```bash
# Check if Weaviate is running
docker-compose ps weaviate

# Check health
curl http://localhost:8002/v1/.well-known/ready

# View logs
docker-compose logs weaviate
```

### Issue: PostgreSQL Connection Refused

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection
docker exec -it postgres psql -U agent_user -d agent_db

# Check DATABASE_URL format
# Should be: postgresql://username:password@host:port/database
```

### Issue: MinIO Access Denied

**Solution:**
```bash
# Verify credentials
mc alias set local http://localhost:9000 minioadmin minioadmin

# Check bucket exists
mc ls local/

# Verify bucket policy
mc admin policy list local
```

---

## Next Steps

1. **Customize Your Agent**: Modify `app/agent.py` with your specific agent logic
2. **Add Tools**: Implement custom tools for your agent to use
3. **Set Up RAG**: Configure document ingestion and vector search
4. **Enable Monitoring**: Configure Grafana dashboards for your metrics
5. **Production Hardening**:
   - Use secrets management (Vault)
   - Set up proper authentication
   - Configure SSL/TLS
   - Implement rate limiting
   - Set up backups

---

## Production Deployment

For production deployment, consider:

### Kubernetes Deployment

```bash
# Convert Docker Compose to Kubernetes manifests
kompose convert -f docker-compose.yml

# Or use Helm charts for each service
helm install postgres bitnami/postgresql
helm install weaviate weaviate/weaviate
```

### High Availability

- Deploy LLM server with multiple replicas behind a load balancer
- Use PostgreSQL with replication (primary-replica setup)
- Deploy Weaviate cluster for distributed vector search
- Use MinIO in distributed mode

### Security

- Implement mTLS for service-to-service communication
- Use HashiCorp Vault for secrets management
- Set up network policies and firewalls
- Enable audit logging

### Monitoring

- Deploy Prometheus for metrics collection
- Set up alerts for service health
- Configure log retention policies
- Implement distributed tracing across all services

---

## Resource Requirements

### Minimal Setup
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 50GB
- **GPU**: Optional

### Full Stack Setup
- **CPU**: 8+ cores
- **RAM**: 16GB+ (32GB recommended)
- **Disk**: 200GB+ (SSD recommended)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for better LLM performance)

---

## Support & Documentation

- **Full Migration Guide**: See `CHECKLIST.md`
- **Architecture Details**: See `CLAUDE.md`
- **Issue Tracker**: [GitHub Issues](https://github.com/GoogleCloudPlatform/agent-starter-pack/issues)
- **Community**: [Discussions](https://github.com/GoogleCloudPlatform/agent-starter-pack/discussions)

---

## License

This project is licensed under the Apache License 2.0. See LICENSE file for details.
