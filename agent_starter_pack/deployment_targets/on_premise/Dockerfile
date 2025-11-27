# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS, PROPRIETARY AND CONFIDENTIAL
#
# On-Premise Deployment Dockerfile
# Optimized for local deployment with minimal dependencies

FROM python:3.11-slim

# Install uv package manager
RUN pip install --no-cache-dir uv==0.8.13

{%- if cookiecutter.is_adk_live %}
# Install Node.js for frontend build
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
{%- endif %}

WORKDIR /code

# Copy dependency files
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# Copy application code
COPY ./{{cookiecutter.agent_directory}} ./{{cookiecutter.agent_directory}}

{%- if cookiecutter.is_adk_live %}
# Copy and build frontend
COPY ./frontend ./frontend
RUN cd frontend && npm ci && npm run build
{%- endif %}

# Install Python dependencies
RUN uv sync --frozen

# Build arguments for versioning
ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

ARG AGENT_VERSION=0.1.0
ENV AGENT_VERSION=${AGENT_VERSION}

# Create directories for logs and data
RUN mkdir -p /var/log /data/storage /data/chroma

# Expose application port (default 8000)
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "{{cookiecutter.agent_directory}}.fast_api_app:app", "--host", "0.0.0.0", "--port", "8000"]
