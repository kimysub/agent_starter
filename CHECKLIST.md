# On-Premise Migration Checklist

This document provides a comprehensive checklist for migrating the Agent Starter Pack from Google Cloud services to on-premise alternatives while preserving the ADK (Agent Development Kit) framework.

## Migration Overview

**Constraint**: ADK framework must remain unchanged as it's the core agent architecture.

**Strategy**: Replace Google Cloud infrastructure and services with open-source/on-premise alternatives while maintaining the same interfaces and functionality.

---

## Phase 1: Core AI/ML Services

### 1.1 LLM Model Service (HIGH PRIORITY) ✅ COMPLETED

- [x] **Replace Vertex AI / Gemini API with OpenAI-compatible LLM**
  - **Current**: Vertex AI with Gemini models (`gemini-2.5-flash`, `gemini-2.0-flash`)
  - **Target**: OpenAI-compatible API (vLLM, Ollama, LocalAI, Text Generation Inference)
  - **✅ Solution**: Use ADK's built-in `google.adk.models.lite_llm.LiteLlm` class
  - **Files modified**:
    - [x] `agent_starter_pack/deployment_targets/on_premise/agents/adk_base/app/agent.py` - Model initialization
    - [x] Created `on_premise` deployment target with local infrastructure support
  - **Approach (VALIDATED)**:
    - [x] Use ADK's native LiteLLM support - no custom wrapper needed!
    - [x] LiteLLM supports 100+ providers: OpenAI, X.AI, vLLM, Ollama, etc.
    - [x] Configure via `LiteLlm(model, api_key, api_base)`
    - [x] Pass LiteLlm instance to `Agent(model=llm)`
    - [x] Tested successfully with X.AI Grok endpoint
  - **Environment variables added**:
    - [x] `LLM_ENDPOINT_URL` - OpenAI-compatible endpoint
    - [x] `LLM_API_KEY` - API key for authentication
    - [x] `LLM_MODEL_NAME` - Model name (with provider prefix for LiteLLM)
  - **On-premise options (ALL SUPPORTED)**:
    - [x] **vLLM**: High-performance inference server (recommended)
    - [x] **Ollama**: Easy-to-use local LLM runtime
    - [x] **Text Generation Inference (TGI)**: HuggingFace's inference server
    - [x] **LocalAI**: Drop-in OpenAI replacement
    - [x] **Cloud providers**: OpenAI, X.AI, Anthropic, Azure, etc.
  - **Key Code Pattern**:
    ```python
    from google.adk.models.lite_llm import LiteLlm
    from google.adk.agents import Agent

    llm = LiteLlm(
        model=os.getenv("LLM_MODEL_NAME"),
        api_key=os.getenv("LLM_API_KEY"),
        api_base=os.getenv("LLM_ENDPOINT_URL"),
    )

    agent = Agent(
        name="root_agent",
        model=llm,  # Pass LiteLlm instance directly!
        instruction="...",
        tools=[...],
    )
    ```

### 1.2 Embeddings Service (RAG Only)

- [ ] **Replace Vertex AI Embeddings with local embeddings**
  - **Current**: `VertexAIEmbeddings` with `text-embedding-005` model
  - **Target**: HuggingFace embeddings, Sentence Transformers, or OpenAI-compatible
  - **Files to modify**:
    - [ ] `agent_starter_pack/agents/agentic_rag/app/agent.py`
    - [ ] `agent_starter_pack/agents/agentic_rag/app/retrievers.py`
  - **Approach**:
    - [ ] Replace `VertexAIEmbeddings` with `HuggingFaceEmbeddings` or `OpenAIEmbeddings`
    - [ ] Configure local model (e.g., `all-MiniLM-L6-v2`, `bge-large-en`)
    - [ ] Update data ingestion pipeline to use local embeddings
  - **On-premise options**:
    - [ ] **Sentence Transformers**: Direct local inference
    - [ ] **FastEmbed**: Fast local embeddings library
    - [ ] **Embedding service on vLLM/TGI**: Server-based embeddings

### 1.3 Vertex AI Search & Vector Search (RAG Only)

- [ ] **Replace Vertex AI Search with local vector database**
  - **Current**: `VertexAISearchRetriever` with Discovery Engine
  - **Target**: Local vector database (Chroma, Weaviate, Qdrant, pgvector)
  - **Files to modify**:
    - [ ] `agent_starter_pack/agents/agentic_rag/app/retrievers.py`
    - [ ] `agent_starter_pack/base_template/deployment/terraform/storage.tf` (remove Vertex AI resources)
    - [ ] Data ingestion pipeline components
  - **Approach**:
    - [ ] Create local vector store initialization
    - [ ] Implement custom retriever using LangChain vector store integrations
    - [ ] Update data ingestion to populate local vector DB
  - **Environment variables to add**:
    - [ ] `VECTOR_DB_TYPE` (chroma, weaviate, qdrant, pgvector)
    - [ ] `VECTOR_DB_HOST`, `VECTOR_DB_PORT`
    - [ ] `VECTOR_COLLECTION_NAME`
  - **On-premise options**:
    - [ ] **Chroma**: Simple embedded vector DB (good for development)
    - [ ] **Weaviate**: Full-featured vector search engine
    - [ ] **Qdrant**: Rust-based high-performance vector DB
    - [ ] **pgvector**: PostgreSQL extension (reuse existing DB)

- [ ] **Replace Vertex AI Vector Search (Matching Engine)**
  - **Current**: `VectorSearchVectorStore` with managed indices and endpoints
  - **Target**: Same local vector database as above
  - **Files to modify**:
    - [ ] `agent_starter_pack/agents/agentic_rag/app/retrievers.py`
    - [ ] `agent_starter_pack/base_template/deployment/terraform/storage.tf`
  - **Approach**:
    - [ ] Consolidate with Vertex AI Search replacement above
    - [ ] Use single vector DB for both search types

### 1.4 Vertex AI Ranking

- [ ] **Replace Vertex AI Ranking with local ranking**
  - **Current**: `VertexAIRank` for re-ranking retrieved documents
  - **Target**: Local cross-encoder models or custom ranking
  - **Files to modify**:
    - [ ] `agent_starter_pack/agents/agentic_rag/app/retrievers.py`
  - **Approach**:
    - [ ] Use HuggingFace cross-encoder models (e.g., `ms-marco-MiniLM-L-6-v2`)
    - [ ] Implement LangChain contextual compression with cross-encoder
  - **On-premise options**:
    - [ ] **Sentence Transformers CrossEncoder**: Local re-ranking
    - [ ] **LangChain FlashrankRerank**: Fast local re-ranking
    - [ ] **Cohere Rerank** (if running local Cohere-compatible server)

### 1.5 Vertex AI Evaluation (Development/Optional)

- [ ] **Replace Vertex AI Evaluation with local evaluation**
  - **Current**: `EvalTask` from Vertex AI for agent assessment
  - **Target**: Local evaluation frameworks
  - **Files to modify**:
    - [ ] `agent_starter_pack/agents/*/notebooks/*.ipynb`
  - **Approach**:
    - [ ] Use LangSmith, Ragas, or DeepEval for local evaluation
    - [ ] Implement custom evaluation metrics
  - **On-premise options**:
    - [ ] **Ragas**: RAG assessment framework
    - [ ] **DeepEval**: LLM evaluation framework
    - [ ] **LangSmith** (self-hosted if available)
    - [ ] Custom evaluation scripts with local LLM as judge

### 1.6 Vertex AI Pipelines (Data Ingestion)

- [ ] **Replace Vertex AI Pipelines with local orchestration**
  - **Current**: Kubeflow Pipelines (KFP) on Vertex AI
  - **Target**: Local workflow orchestration (Airflow, Prefect, or Python scripts)
  - **Files to modify**:
    - [ ] `agent_starter_pack/data_ingestion/data_ingestion_pipeline/pipeline.py`
    - [ ] `agent_starter_pack/data_ingestion/data_ingestion_pipeline/submit_pipeline.py`
    - [ ] `agent_starter_pack/data_ingestion/data_ingestion_pipeline/components/*.py`
  - **Approach**:
    - [ ] Convert KFP pipeline to Python scripts or Airflow DAGs
    - [ ] Replace Vertex AI pipeline submission with local execution
    - [ ] Implement scheduling with cron or orchestrator
  - **On-premise options**:
    - [ ] **Apache Airflow**: Full-featured workflow orchestration
    - [ ] **Prefect**: Modern workflow orchestration
    - [ ] **Luigi**: Lightweight pipeline framework
    - [ ] **Python scripts + cron**: Simplest approach

---

## Phase 2: Storage Services

### 2.1 Cloud Storage (GCS)

- [ ] **Replace GCS with MinIO or local filesystem**
  - **Current**: `google.cloud.storage` for logs, data, vector search data
  - **Target**: MinIO (S3-compatible) or local filesystem
  - **Files to modify**:
    - [ ] `agent_starter_pack/base_template/{{cookiecutter.agent_directory}}/app_utils/gcs.py`
    - [ ] All files importing or using GCS client
    - [ ] `agent_starter_pack/base_template/deployment/terraform/storage.tf`
  - **Buckets to replace**:
    - [ ] Logs bucket: `{project-id}-{project-name}-logs`
    - [ ] Data ingestion bucket: `{project-id}-{project-name}-rag`
    - [ ] Vector search bucket: `{project-id}-{project-name}-vs`
  - **Approach**:
    - [ ] Replace `google.cloud.storage.Client` with `boto3` client (for MinIO)
    - [ ] Or replace with local filesystem operations (`pathlib.Path`)
    - [ ] Update bucket creation to MinIO bucket creation or `mkdir`
    - [ ] Update all upload/download operations
  - **Environment variables to add**:
    - [ ] `STORAGE_TYPE` (minio, local, s3)
    - [ ] `MINIO_ENDPOINT_URL`
    - [ ] `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
    - [ ] `LOCAL_STORAGE_PATH` (for local filesystem)
  - **On-premise options**:
    - [ ] **MinIO**: S3-compatible object storage (recommended)
    - [ ] **Local filesystem**: Simplest, good for single-machine
    - [ ] **Ceph**: Distributed object storage (enterprise)
    - [ ] **SeaweedFS**: Distributed blob storage

### 2.2 Cloud SQL (Session Storage)

- [ ] **Replace Cloud SQL with local PostgreSQL**
  - **Current**: Cloud SQL PostgreSQL 15 for session state
  - **Target**: Local PostgreSQL (Docker or native)
  - **Files to modify**:
    - [ ] `agent_starter_pack/deployment_targets/cloud_run/deployment/terraform/service.tf`
    - [ ] All files using `INSTANCE_CONNECTION_NAME` environment variable
    - [ ] Cloud SQL Proxy configuration in Terraform
  - **Approach**:
    - [ ] Replace Cloud SQL connection with direct PostgreSQL connection
    - [ ] Remove Cloud SQL Proxy volume mounting
    - [ ] Use standard PostgreSQL connection strings
    - [ ] Update IAM authentication to password-based auth
  - **Environment variables to replace**:
    - [ ] Remove: `INSTANCE_CONNECTION_NAME`
    - [ ] Add: `DATABASE_URL` or `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`
  - **On-premise options**:
    - [ ] **PostgreSQL in Docker**: `docker run -d postgres:15`
    - [ ] **Native PostgreSQL**: Installed on host
    - [ ] **PostgreSQL with pgvector**: If using for vector storage

### 2.3 BigQuery (Data Processing)

- [ ] **Replace BigQuery with local data processing**
  - **Current**: BigQuery + BigFrames for data processing and embeddings
  - **Target**: Pandas + local processing or DuckDB
  - **Files to modify**:
    - [ ] `agent_starter_pack/data_ingestion/data_ingestion_pipeline/components/process_data.py`
  - **Approach**:
    - [ ] Replace `bigframes.pandas` with standard `pandas`
    - [ ] Replace `bigframes.ml.llm` with local embedding generation
    - [ ] Replace BigQuery queries with local data sources (CSV, Parquet, DuckDB)
    - [ ] Implement chunking and deduplication with pandas
  - **On-premise options**:
    - [ ] **Pandas**: Standard dataframe processing
    - [ ] **DuckDB**: In-process SQL OLAP database (fast for analytics)
    - [ ] **Polars**: Fast dataframe library (Rust-based)
    - [ ] **Apache Spark**: Distributed processing (if needed)

### 2.4 Artifact Registry

- [ ] **Replace Artifact Registry with local Docker registry**
  - **Current**: Google Artifact Registry for container images
  - **Target**: Local Docker registry or Docker Hub
  - **Files to modify**:
    - [ ] `agent_starter_pack/base_template/deployment/terraform/storage.tf`
    - [ ] CI/CD workflow files (`.github/workflows/`, `.cloudbuild/`)
    - [ ] Dockerfile and build scripts
  - **Approach**:
    - [ ] Replace registry URL with local registry URL
    - [ ] Update docker push/pull commands
    - [ ] Remove GCP authentication for registry
  - **Environment variables to add**:
    - [ ] `DOCKER_REGISTRY_URL` (e.g., `localhost:5000`)
  - **On-premise options**:
    - [ ] **Docker Registry**: `docker run -d -p 5000:5000 registry:2`
    - [ ] **Harbor**: Enterprise container registry
    - [ ] **GitLab Container Registry**: If using GitLab
    - [ ] **Nexus Repository**: Multi-format artifact repository

---

## Phase 3: Infrastructure & Deployment

### 3.1 Cloud Run

- [ ] **Replace Cloud Run with local Docker containers**
  - **Current**: Cloud Run v2 service for HTTP serving
  - **Target**: Docker Compose, Kubernetes, or docker run
  - **Files to modify**:
    - [ ] `agent_starter_pack/deployment_targets/cloud_run/deployment/terraform/service.tf`
    - [ ] `agent_starter_pack/deployment_targets/cloud_run/Dockerfile`
    - [ ] All Cloud Run specific configurations
  - **Approach**:
    - [ ] Create Docker Compose file for multi-service orchestration
    - [ ] Replace Cloud Run service with docker-compose services
    - [ ] Update networking (ports, service discovery)
    - [ ] Handle environment variables injection
    - [ ] Implement load balancing if needed (nginx, Traefik)
  - **New files to create**:
    - [ ] `docker-compose.yml` - Service orchestration
    - [ ] `nginx.conf` or `traefik.yml` - Reverse proxy (optional)
  - **On-premise options**:
    - [ ] **Docker Compose**: Simple multi-container apps
    - [ ] **Kubernetes** (k3s, microk8s): Production-grade orchestration
    - [ ] **Docker Swarm**: Native Docker orchestration
    - [ ] **Nomad**: HashiCorp's orchestrator

### 3.2 Agent Engine

- [ ] **Replace Agent Engine with local agent serving**
  - **Current**: Managed Vertex AI Agent Engine deployment
  - **Target**: Local HTTP server (FastAPI, Flask) or keep existing setup
  - **Files to modify**:
    - [ ] `agent_starter_pack/deployment_targets/agent_engine/{{cookiecutter.agent_directory}}/agent_engine_app.py`
    - [ ] `agent_starter_pack/deployment_targets/agent_engine/{{cookiecutter.agent_directory}}/app_utils/deploy.py`
  - **Approach**:
    - [ ] Determine if Agent Engine is truly needed or if Cloud Run replacement suffices
    - [ ] If needed, create custom HTTP server wrapping ADK agent
    - [ ] Implement Agent2Agent (A2A) protocol support locally if used
  - **Note**: ADK framework itself remains unchanged, only deployment method changes

### 3.3 Terraform Infrastructure

- [ ] **Replace/Simplify Terraform for local infrastructure**
  - **Current**: Terraform managing GCP resources
  - **Target**: Docker Compose, local provisioning scripts, or simplified Terraform
  - **Files to modify**:
    - [ ] All files in `agent_starter_pack/base_template/deployment/terraform/`
    - [ ] Remove: `apis.tf`, `iam.tf`, `service_accounts.tf` (GCP-specific)
    - [ ] Keep: General structure but replace resources
  - **Approach**:
    - [ ] Option A: Replace Terraform with Docker Compose + shell scripts
    - [ ] Option B: Use Terraform with Docker/local providers
    - [ ] Option C: Manual setup documentation
  - **New infrastructure code**:
    - [ ] Docker Compose for service orchestration
    - [ ] Shell scripts for initialization (DB setup, vector DB, etc.)
    - [ ] Environment variable templates

---

## Phase 4: Security & Secrets Management

### 4.1 Secret Manager

- [ ] **Replace Secret Manager with local secrets management**
  - **Current**: Google Secret Manager for database passwords
  - **Target**: Environment variables, .env files, or HashiCorp Vault
  - **Files to modify**:
    - [ ] `agent_starter_pack/deployment_targets/cloud_run/deployment/terraform/service.tf`
    - [ ] All files referencing secrets
  - **Approach**:
    - [ ] Replace secret references with environment variables
    - [ ] Use `.env` files for development (with `.env.example` template)
    - [ ] Consider Vault for production deployments
  - **On-premise options**:
    - [ ] **Environment variables**: Simplest
    - [ ] **Docker secrets**: For Docker Swarm/Compose
    - [ ] **Kubernetes secrets**: For K8s deployments
    - [ ] **HashiCorp Vault**: Enterprise secrets management
    - [ ] **SOPS**: Encrypted secrets in Git

### 4.2 Cloud IAM & Service Accounts

- [ ] **Replace Cloud IAM with local access control**
  - **Current**: Service accounts with role-based IAM
  - **Target**: Application-level authentication or mTLS
  - **Files to modify**:
    - [ ] `agent_starter_pack/base_template/deployment/terraform/service_accounts.tf`
    - [ ] `agent_starter_pack/base_template/deployment/terraform/iam.tf`
    - [ ] All files using ADC (Application Default Credentials)
  - **Approach**:
    - [ ] Replace service account authentication with API keys or basic auth
    - [ ] Implement application-level RBAC if needed
    - [ ] For service-to-service auth, use mTLS or JWT tokens
  - **On-premise options**:
    - [ ] **API Keys**: Simple authentication
    - [ ] **OAuth2/OIDC**: For user authentication
    - [ ] **mTLS**: Service-to-service auth
    - [ ] **Keycloak**: Open-source identity management

### 4.3 Workload Identity

- [ ] **Remove Workload Identity Federation**
  - **Current**: GitHub Actions to GCP authentication via WIF
  - **Target**: Direct authentication with local services
  - **Files to modify**:
    - [ ] `.github/workflows/*.yaml` - Remove WIF authentication steps
  - **Approach**:
    - [ ] Use SSH, API keys, or other auth methods for CI/CD
    - [ ] For local CI/CD, direct access may not need authentication

---

## Phase 5: Observability & Monitoring

### 5.1 Cloud Logging

- [ ] **Replace Cloud Logging with local logging**
  - **Current**: `google.cloud.logging` with structured logging
  - **Target**: File-based logging, ELK stack, or Loki
  - **Files to modify**:
    - [ ] `agent_starter_pack/base_template/{{cookiecutter.agent_directory}}/app_utils/telemetry.py`
    - [ ] All app files with logging configuration
  - **Approach**:
    - [ ] Replace Cloud Logging client with standard Python logging
    - [ ] Configure file handlers or remote logging backends
    - [ ] Maintain structured logging format (JSON)
  - **Environment variables to add**:
    - [ ] `LOG_LEVEL` (INFO, DEBUG, ERROR)
    - [ ] `LOG_FORMAT` (json, text)
    - [ ] `LOG_FILE_PATH` or `LOKI_URL`
  - **On-premise options**:
    - [ ] **Python logging to files**: Simplest
    - [ ] **Loki + Promtail**: Lightweight log aggregation
    - [ ] **ELK Stack** (Elasticsearch, Logstash, Kibana): Full-featured
    - [ ] **Graylog**: Open-source log management

### 5.2 Cloud Trace

- [ ] **Replace Cloud Trace with local tracing**
  - **Current**: `CloudTraceSpanExporter` for OpenTelemetry
  - **Target**: Jaeger, Zipkin, or local OTel collector
  - **Files to modify**:
    - [ ] `agent_starter_pack/base_template/{{cookiecutter.agent_directory}}/app_utils/telemetry.py`
  - **Approach**:
    - [ ] Replace `CloudTraceSpanExporter` with `JaegerExporter` or `ZipkinExporter`
    - [ ] Set up local tracing backend (Jaeger all-in-one)
    - [ ] Update OpenTelemetry configuration
  - **Environment variables to add**:
    - [ ] `OTEL_EXPORTER_OTLP_ENDPOINT` (for OTel collector)
    - [ ] `JAEGER_ENDPOINT` or `ZIPKIN_ENDPOINT`
  - **On-premise options**:
    - [ ] **Jaeger**: Popular distributed tracing (recommended)
    - [ ] **Zipkin**: Lightweight tracing
    - [ ] **OpenTelemetry Collector**: Backend-agnostic
    - [ ] **Grafana Tempo**: Traces with Grafana

### 5.3 OpenTelemetry Configuration

- [ ] **Update OpenTelemetry to use local exporters**
  - **Current**: Exports to Cloud Trace and Cloud Logging
  - **Target**: Export to Jaeger, Loki, or console
  - **Files to modify**:
    - [ ] `agent_starter_pack/base_template/{{cookiecutter.agent_directory}}/app_utils/telemetry.py`
  - **Approach**:
    - [ ] Replace exporters with local backends
    - [ ] Keep instrumentation (GenAI SDK, LangChain) unchanged
    - [ ] Configure OTEL environment variables for local endpoints

---

## Phase 6: CI/CD & Build Pipeline

### 6.1 GitHub Actions

- [ ] **Update GitHub Actions for local deployment**
  - **Current**: Deploys to Cloud Run and Agent Engine
  - **Target**: Builds containers and deploys to local infrastructure
  - **Files to modify**:
    - [ ] `.github/workflows/deploy-to-prod.yaml`
    - [ ] `.github/workflows/staging.yaml`
    - [ ] `.github/workflows/pr_checks.yaml`
  - **Approach**:
    - [ ] Replace Cloud Run deployment with SSH deploy or docker commands
    - [ ] Update container registry to local registry
    - [ ] Remove GCP authentication steps
    - [ ] Add SSH/ansible deployment steps for on-premise servers
  - **Alternative**: Use self-hosted GitHub Actions runners

### 6.2 Cloud Build

- [ ] **Replace Cloud Build with local CI/CD**
  - **Current**: `.cloudbuild/*.yaml` for GCP-native CI/CD
  - **Target**: Jenkins, GitLab CI, or keep GitHub Actions
  - **Files to modify/replace**:
    - [ ] Remove `.cloudbuild/` directory
    - [ ] Or adapt to local docker build commands
  - **On-premise options**:
    - [ ] **Jenkins**: Popular open-source CI/CD
    - [ ] **GitLab CI**: If using GitLab
    - [ ] **Drone CI**: Lightweight container-native CI
    - [ ] **Tekton**: Kubernetes-native CI/CD
    - [ ] **BuildKite**: Hybrid cloud CI

---

## Phase 7: Configuration & Environment Management

### 7.1 Project Configuration

- [ ] **Update project configuration for on-premise**
  - **Files to create/modify**:
    - [ ] Create `.env.example` with all required environment variables
    - [ ] Create `config.yaml` or `settings.py` for centralized configuration
    - [ ] Update `pyproject.toml` dependencies (remove Google Cloud SDK dependencies)
  - **New configuration structure**:
    ```
    config/
    ├── local.yaml          # Local development
    ├── docker.yaml         # Docker Compose deployment
    ├── kubernetes.yaml     # Kubernetes deployment (optional)
    └── .env.example        # Environment variable template
    ```

### 7.2 Environment Variables Mapping

- [ ] **Create environment variable mapping document**
  - **Google Cloud variables to remove**:
    - [ ] `GOOGLE_CLOUD_PROJECT`
    - [ ] `GOOGLE_CLOUD_LOCATION`
    - [ ] `GOOGLE_CLOUD_REGION`
    - [ ] `GOOGLE_GENAI_USE_VERTEXAI`
    - [ ] `LOGS_BUCKET_NAME`
    - [ ] `INSTANCE_CONNECTION_NAME`
  - **New environment variables to add**:
    - [ ] `LLM_ENDPOINT_URL`
    - [ ] `LLM_MODEL_NAME`
    - [ ] `LLM_API_KEY`
    - [ ] `EMBEDDING_ENDPOINT_URL`
    - [ ] `EMBEDDING_MODEL_NAME`
    - [ ] `VECTOR_DB_TYPE`
    - [ ] `VECTOR_DB_URL`
    - [ ] `STORAGE_TYPE` (minio, local, s3)
    - [ ] `STORAGE_ENDPOINT_URL`
    - [ ] `DATABASE_URL`
    - [ ] `LOG_LEVEL`
    - [ ] `TRACING_ENDPOINT`

### 7.3 Dependency Updates

- [ ] **Update Python dependencies in pyproject.toml**
  - **Dependencies to remove**:
    - [ ] `google-cloud-aiplatform`
    - [ ] `google-cloud-logging`
    - [ ] `google-cloud-storage`
    - [ ] `google-auth`
    - [ ] `bigframes` (if used)
  - **Dependencies to add**:
    - [ ] `openai` - For OpenAI-compatible LLM clients
    - [ ] `boto3` or `minio` - For MinIO/S3-compatible storage
    - [ ] `psycopg2-binary` - For direct PostgreSQL connection
    - [ ] `chromadb` or `weaviate-client` or `qdrant-client` - For vector DB
    - [ ] `sentence-transformers` - For local embeddings
    - [ ] `duckdb` - For local data processing (optional)
    - [ ] `jaeger-client` or `opentelemetry-exporter-jaeger` - For tracing

---

## Phase 8: Template System Updates

### 8.1 Base Template Modifications

- [ ] **Update base template for on-premise deployment**
  - **Files to modify**:
    - [ ] `agent_starter_pack/base_template/{{cookiecutter.agent_directory}}/app_utils/gcs.py`
      - [ ] Rename to `storage.py` with pluggable backend
    - [ ] `agent_starter_pack/base_template/{{cookiecutter.agent_directory}}/app_utils/telemetry.py`
      - [ ] Update exporters to local backends
    - [ ] `agent_starter_pack/base_template/pyproject.toml`
      - [ ] Update dependencies
    - [ ] `agent_starter_pack/base_template/Makefile`
      - [ ] Update commands for local deployment
    - [ ] `agent_starter_pack/base_template/README.md`
      - [ ] Update instructions for on-premise setup
  - **Files to add**:
    - [ ] `docker-compose.yml`
    - [ ] `.env.example`
    - [ ] `config/local.yaml`

### 8.2 Deployment Target: On-Premise

- [ ] **Create new deployment target: `on_premise`**
  - **New directory**: `agent_starter_pack/deployment_targets/on_premise/`
  - **Files to create**:
    - [ ] `docker-compose.yml` - Multi-service orchestration
    - [ ] `Dockerfile` - Application container
    - [ ] `nginx.conf` - Reverse proxy configuration
    - [ ] `deployment/docker/` - Docker deployment scripts
    - [ ] `deployment/kubernetes/` - K8s manifests (optional)
    - [ ] `{{cookiecutter.agent_directory}}/docker_app.py` - App entrypoint for Docker
  - **Override files**:
    - [ ] Override Cloud Run specific files with Docker equivalents

### 8.3 CLI Command Updates ✅ COMPLETED + SIMPLIFIED

- [x] **Simplified CLI for on-premise A2A deployment** ✅ COMPLETE
  - **Files modified**:
    - [x] `agent_starter_pack/cli/commands/create.py`
      - [x] **Simplified**: Deployment target restricted to `on_premise` only
      - [x] Set `default="on_premise"` so users don't need to specify
      - [x] Made GCP region prompt conditional (skipped for on_premise)
      - [x] Made GCP credential setup conditional (skipped for on_premise)
      - [x] Session type fixed to `in_memory` for on_premise
      - [x] CI/CD runner selection skipped for on_premise
    - [x] `agent_starter_pack/cli/utils/template.py`
      - [x] **Simplified**: Added `ALLOWED_AGENTS = ["adk_a2a_base"]` filter
      - [x] CLI now only shows `adk_a2a_base` agent
      - [x] Added on_premise display info to deployment target prompts
    - [x] `agent_starter_pack/agents/adk_a2a_base/.template/templateconfig.yaml`
      - [x] Added `on_premise` to deployment_targets list
    - [x] `agent_starter_pack/agents/adk_a2a_base/app/agent.py`
      - [x] **Rewritten** to use A2A pattern from [a2aproject/a2a-samples](https://github.com/a2aproject/a2a-samples)
      - [x] Added `from google.adk.a2a.utils.agent_to_a2a import to_a2a`
      - [x] Uses LiteLLM with environment variables
      - [x] Converts agent to A2A app: `a2a_app = to_a2a(root_agent, port=...)`
    - [x] `agent_starter_pack/deployment_targets/on_premise/agents/adk_a2a_base/app/agent.py`
      - [x] **Created** with LiteLLM + A2A pattern
      - [x] Combines OpenAI-compatible endpoints with A2A protocol
    - [x] `agent_starter_pack/base_template/pyproject.toml`
      - [x] Added on_premise dependencies (litellm, fastapi, uvicorn, python-dotenv)
  - **Usage** (Simplified):
    ```bash
    # Create on-premise A2A agent (simplified - only one option!)
    uv run agent-starter-pack create my-agent --output-dir ./my-agent

    # CLI automatically uses: adk_a2a_base + on_premise deployment
    # No GCP prompts, no agent selection needed!

    # Generate lock files after dependency changes
    make generate-lock
    ```
  - **Completed Features**:
    - ✅ Agent2Agent (A2A) protocol integration
    - ✅ LiteLLM support for 100+ providers
    - ✅ Simplified CLI (only one agent + one deployment target)
    - ✅ Environment-based configuration with `.env` files
  - **Not Implemented** (Not needed for current focus):
    - [ ] `agent_starter_pack/cli/commands/enhance.py` - Support on-premise enhancement
    - [ ] `agent_starter_pack/cli/commands/setup_cicd.py` - Add on-premise CI/CD (optional)

### 8.4 REST API for Programmatic Access ✅ COMPLETED

- [x] **Create REST API for complete project generation with GitHub integration** ✅ COMPLETE
  - **New directory**: `agent_starter_pack/api/`
  - **Files created**:
    - [x] `agent_starter_pack/api/main.py` - FastAPI application with CORS support
    - [x] `agent_starter_pack/api/models.py` - Pydantic request/response models
    - [x] `agent_starter_pack/api/project_generator.py` - Complete project generation logic
    - [x] `agent_starter_pack/api/github_helper.py` - GitHub API integration
    - [x] `agent_starter_pack/api/run.py` - API server startup script
    - [x] `agent_starter_pack/api/README.md` - API documentation and examples
    - [x] `docs/GITHUB_INTEGRATION.md` - Complete GitHub integration guide
  - **Files modified**:
    - [x] `pyproject.toml`
      - [x] Added `fastapi>=0.115.0`, `uvicorn[standard]>=0.34.0`, `requests>=2.32.0` dependencies
      - [x] Added `agent-starter-pack-api` CLI command
      - [x] Added API directory to ruff linting
    - [x] `CLAUDE.md`
      - [x] Added API to key capabilities
      - [x] Added API server section to Development Commands
      - [x] Added API Structure section to Architecture
  - **API Features**:
    - ✅ **Full Project Generation**: Creates complete agent projects (not just code)
    - ✅ **Zip Downloads**: Returns downloadable zip files
    - ✅ **GitHub Integration**: Creates repositories on GitHub.com or GitHub Enterprise
    - ✅ **Simple UI Inputs**: Agent name, description, prompt, tools
    - ✅ **Custom Tools**: Generates tool stubs from name/description
    - ✅ **Organization Support**: Create repos in GitHub organizations
    - ✅ **Public/Private Repos**: Configurable repository visibility
    - ✅ **CORS Enabled**: Works with web frontends
    - ✅ **Self-documenting**: Built-in Swagger UI at `/docs`
    - ✅ **Health Check**: `GET /health` endpoint
  - **Usage**:
    ```bash
    # Start API server
    uv run agent-starter-pack-api
    # Server at http://localhost:8080
    # Docs at http://localhost:8080/docs

    # Generate project with GitHub repo
    export GITHUB_TOKEN=ghp_your_token_here
    curl -X POST http://localhost:8080/api/v1/generate/project \
      -H "Content-Type: application/json" \
      -d '{
        "agent_name": "my-agent",
        "description": "My helpful agent",
        "prompt": "You assist users",
        "create_git_repo": true,
        "repo_private": true
      }'
    ```
  - **Request Schema**:
    - `agent_name`: Agent project name (required)
    - `description`: Agent description (required)
    - `prompt`: System instruction/prompt (required)
    - `tools`: List of tools with name and description (optional)
    - `create_git_repo`: Whether to create GitHub repository (default: false)
    - `git_repo_name`: Custom repository name (optional)
    - `github_token`: GitHub PAT (optional, can use env var)
    - `github_org`: GitHub organization name (optional)
    - `github_enterprise_url`: GitHub Enterprise URL (optional)
    - `repo_private`: Public or private repository (default: true)
  - **Response Schema**:
    - `project_name`: Name of generated project
    - `download_url`: URL to download zip file
    - `git_repo_url`: GitHub repository URL (if created)
    - `files_generated`: Number of files in project
    - `message`: Success message
  - **Use Cases Enabled**:
    - ✅ Web frontends: Build visual agent builders with download + GitHub integration
    - ✅ IDE plugins: VSCode, JetBrains extensions
    - ✅ CI/CD automation: Generate and deploy agents in pipelines
    - ✅ Learning platforms: Interactive agent creation with instant GitHub repos
    - ✅ Custom tools: Integrate into existing workflows
  - **Documentation**:
    - [x] Developer docs: `agent_starter_pack/api/README.md`
    - [x] GitHub integration guide: `docs/GITHUB_INTEGRATION.md`
    - [x] Interactive docs: Available at `/docs` when server is running
  - **Testing Results**:
    - ✅ Health endpoint: Returns `{"status": "healthy"}`
    - ✅ Basic project generation: Creates complete project with 23 files
    - ✅ Custom tools: Successfully generates tool stubs
    - ✅ Zip download: Creates downloadable zip archives
    - ✅ GitHub.com repos: Successfully creates repositories
    - ✅ GitHub organizations: Successfully creates in specified org
    - ✅ GitHub Enterprise: Supports custom GitHub Enterprise URLs
    - ✅ Token authentication: Works with both env var and request parameter
  - **Production Ready**:
    - ✅ CORS configured for cross-origin requests
    - ✅ Proper error handling with HTTP status codes
    - ✅ Token security via environment variables
    - ✅ Subprocess-based project generation (avoids import issues)
    - ✅ Error handling with proper HTTP status codes
    - ✅ Pydantic validation for all inputs

### 8.5 Cookiecutter Variables

- [ ] **Add new cookiecutter variables for on-premise**
  - **File**: `agent_starter_pack/base_template/.template/cookiecutter.json` (if exists)
  - **New variables**:
    - [ ] `deployment_target` - Add `on_premise` option
    - [ ] `llm_provider` - `openai_compatible`, `ollama`, `vllm`
    - [ ] `llm_endpoint_url`
    - [ ] `storage_backend` - `minio`, `local`, `s3`
    - [ ] `vector_db_type` - `chroma`, `weaviate`, `qdrant`, `pgvector`
    - [ ] `use_local_tracing` - Boolean
    - [ ] `use_local_logging` - Boolean

---

## Phase 9: Data Ingestion Pipeline

### 9.1 Pipeline Conversion

- [ ] **Convert Vertex AI Pipeline to local pipeline**
  - **Current**: KFP pipeline with BigQuery and Vertex AI
  - **Target**: Python scripts or Airflow DAG
  - **Files to modify**:
    - [ ] `agent_starter_pack/data_ingestion/data_ingestion_pipeline/pipeline.py`
      - [ ] Convert to Airflow DAG or standalone script
    - [ ] `agent_starter_pack/data_ingestion/data_ingestion_pipeline/components/process_data.py`
      - [ ] Replace BigQuery with pandas/DuckDB
      - [ ] Replace BigFrames embeddings with local embeddings
    - [ ] `agent_starter_pack/data_ingestion/data_ingestion_pipeline/components/ingest_data.py`
      - [ ] Replace Vertex AI Search/Vector Search with local vector DB
    - [ ] `agent_starter_pack/data_ingestion/data_ingestion_pipeline/submit_pipeline.py`
      - [ ] Replace Vertex AI submission with local execution
  - **Approach**:
    - [ ] Option A: Create Airflow DAG with PythonOperators
    - [ ] Option B: Create standalone Python script with functions
    - [ ] Option C: Use Prefect for modern workflow orchestration

### 9.2 Data Source Configuration

- [ ] **Configure local data sources**
  - **Current**: BigQuery public datasets (StackOverflow)
  - **Target**: Local files, databases, or APIs
  - **Approach**:
    - [ ] Download sample data to local files (CSV, Parquet, JSON)
    - [ ] Update pipeline to read from local sources
    - [ ] Or connect to local PostgreSQL/MySQL instead of BigQuery

---

## Phase 10: Testing & Validation

### 10.1 Update Tests

- [ ] **Update integration tests for on-premise**
  - **Files to modify**:
    - [ ] `tests/integration/test_templated_patterns.py`
    - [ ] All tests referencing GCP services
  - **Approach**:
    - [ ] Add test fixtures for local services (mock LLM, local storage)
    - [ ] Update E2E tests to use local deployment
    - [ ] Create docker-compose for test environment

### 10.2 Test Environment Setup

- [ ] **Create local test environment**
  - **Files to create**:
    - [ ] `docker-compose.test.yml` - Test services (DB, MinIO, vector DB, mock LLM)
    - [ ] `tests/fixtures/local_services.py` - Fixtures for local services
  - **Services to include**:
    - [ ] PostgreSQL container
    - [ ] MinIO container
    - [ ] Chroma/Weaviate container
    - [ ] Mock OpenAI server (vLLM with small model)

### 10.3 Validation Checklist

- [ ] **Validate all functionality works on-premise**
  - [ ] Agent initialization and execution
  - [ ] RAG retrieval and generation
  - [ ] Session state persistence (PostgreSQL)
  - [ ] Document ingestion pipeline
  - [ ] Vector search functionality
  - [ ] Logging and tracing
  - [ ] API endpoints (HTTP serving)
  - [ ] Frontend (if using adk_live)

---

## Phase 11: Documentation

### 11.1 Update Documentation

- [ ] **Update all documentation for on-premise deployment**
  - **Files to modify**:
    - [ ] `README.md` - Main README with on-premise setup
    - [ ] `docs/guide/installation.md` - On-premise installation
    - [ ] `docs/guide/deployment.md` - On-premise deployment guide
    - [ ] `docs/guide/getting-started.md` - Quick start with on-premise
  - **New documentation to create**:
    - [ ] `docs/guide/on-premise-setup.md` - Detailed on-premise guide
    - [ ] `docs/guide/local-llm-setup.md` - Setting up local LLM servers
    - [ ] `docs/guide/vector-db-setup.md` - Vector database options and setup
    - [ ] `docs/guide/troubleshooting-on-premise.md` - Common issues

### 11.2 Architecture Diagrams

- [ ] **Update architecture diagrams**
  - **Files to modify**:
    - [ ] `docs/images/ags_high_level_architecture.png`
  - **Create new diagrams**:
    - [ ] On-premise deployment architecture
    - [ ] Local service interaction diagram
    - [ ] Data flow diagram for on-premise setup

### 11.3 Migration Guide

- [ ] **Create migration guide from GCP to on-premise**
  - **File to create**: `docs/guide/gcp-to-onpremise-migration.md`
  - **Contents**:
    - [ ] Step-by-step migration instructions
    - [ ] Service mapping table (GCP → On-premise)
    - [ ] Data export/import procedures
    - [ ] Rollback procedures
    - [ ] Performance considerations

---

## Implementation Priority

### High Priority (Core Functionality)
1. ✅ LLM Service (Vertex AI → OpenAI-compatible)
2. ✅ Storage Service (GCS → MinIO/Local)
3. ✅ Database (Cloud SQL → PostgreSQL)
4. ✅ Deployment (Cloud Run → Docker)
5. ✅ Vector DB (Vertex AI Search → Chroma/Weaviate)

### Medium Priority (Enhanced Features)
6. ✅ Embeddings (Vertex AI Embeddings → Local)
7. ✅ Logging (Cloud Logging → Local/Loki)
8. ✅ Tracing (Cloud Trace → Jaeger)
9. ✅ CI/CD (Cloud Build/GitHub Actions → Local CI)
10. ✅ Data Pipeline (Vertex AI Pipelines → Airflow/Scripts)

### Low Priority (Optional/Advanced)
11. ✅ Ranking (Vertex AI Ranking → Local)
12. ✅ Evaluation (Vertex AI Evaluation → Local)
13. ✅ Secrets Management (Secret Manager → Vault/Env)
14. ✅ Monitoring (Cloud Monitoring → Prometheus/Grafana)
15. ✅ Container Registry (Artifact Registry → Local Registry)

---

## Quick Start: Minimal On-Premise Setup

For a minimal viable on-premise setup, focus on:

1. **LLM Server**: Run Ollama or vLLM locally
   ```bash
   # Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.1

   # Or vLLM
   docker run --gpus all -p 8000:8000 vllm/vllm-openai:latest \
     --model meta-llama/Llama-3.1-8B-Instruct
   ```

2. **Storage**: Use local filesystem
   ```bash
   mkdir -p ./data/{logs,rag,vector-search}
   ```

3. **Database**: PostgreSQL in Docker
   ```bash
   docker run -d --name postgres \
     -e POSTGRES_PASSWORD=mypassword \
     -e POSTGRES_DB=agent_db \
     -p 5432:5432 postgres:15
   ```

4. **Vector DB**: Chroma (embedded mode, no setup needed)
   ```python
   pip install chromadb
   ```

5. **Application**: Run with Docker Compose
   ```bash
   docker-compose up -d
   ```

---

## Notes & Considerations

### ADK Framework Compatibility
- **Critical**: The ADK (Agent Development Kit) framework itself is Google's proprietary framework
- **Constraint**: We cannot modify ADK internals, but we can:
  - Replace the model backend ADK uses (configure OpenAI-compatible endpoint)
  - Replace infrastructure services ADK depends on (storage, logging, etc.)
  - Keep ADK's agent orchestration, tool calling, and workflow logic intact
- **Test thoroughly**: Ensure ADK agents still function with OpenAI-compatible models

### Performance Considerations
- Local LLM inference will be slower than Vertex AI unless using GPU acceleration
- Consider model quantization (GGUF, GPTQ) for resource-constrained environments
- Vector search performance depends on chosen database and indexing strategy

### Scaling Considerations
- This checklist focuses on single-machine or small-cluster deployment
- For production scale, consider:
  - Kubernetes for orchestration
  - Distributed vector databases (Weaviate cluster, Qdrant cluster)
  - Load balancers (HAProxy, nginx)
  - Distributed tracing and monitoring (Prometheus + Grafana)

### License & Legal
- Verify licenses for all on-premise software
- Ensure LLM models used are licensed for your use case
- Consider data residency and compliance requirements

---

## Summary

This checklist provides a comprehensive path to migrate the Agent Starter Pack from Google Cloud to on-premise infrastructure. The migration is organized into 11 phases covering all aspects:

- **AI/ML Services**: Replace Vertex AI with local LLM servers
- **Storage**: Replace GCS with MinIO or local filesystem
- **Databases**: Replace Cloud SQL and BigQuery with PostgreSQL and local processing
- **Infrastructure**: Replace Cloud Run with Docker/Kubernetes
- **Observability**: Replace Cloud Logging/Trace with open-source alternatives
- **Security**: Replace Secret Manager and IAM with local solutions
- **CI/CD**: Adapt pipelines for on-premise deployment
- **Templates**: Update starter pack templates for on-premise target

The checklist is prioritized to focus on core functionality first, with advanced features as optional enhancements.
