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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Agent Starter Pack API Server.

This API server provides programmatic access to agent project generation.
It allows web UIs and other platforms to generate complete agent projects
with Git repository and zip file downloads.

Usage:
    uvicorn agent_starter_pack.api.main:app --host 0.0.0.0 --port 8080
"""

import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import GenerateProjectRequest, GenerateProjectResponse
from .project_generator import create_git_repository, create_zip_archive, generate_project

app = FastAPI(
    title="Agent Starter Pack API",
    description="API for generating AI agent projects programmatically",
    version="0.2.0",
)

# Enable CORS for web frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Public API - allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temporary directory for generated projects
TEMP_DIR = Path(tempfile.gettempdir()) / "agent-starter-pack-api"
TEMP_DIR.mkdir(exist_ok=True)

# Mount static files for serving zip downloads
DOWNLOADS_DIR = TEMP_DIR / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)
app.mount("/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Agent Starter Pack API",
        "version": "0.2.0",
        "endpoints": {
            "generate_project": "/api/v1/generate/project",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/generate/project", response_model=GenerateProjectResponse)
async def generate_agent_project(
    request: GenerateProjectRequest,
) -> GenerateProjectResponse:
    """Generate a complete agent project from UI inputs.

    This endpoint generates a full agent project with:
    - Complete project structure
    - Customized agent.py with user's description, prompt, and tools
    - Downloadable zip file
    - Optional Git repository

    Args:
        request: Project generation request from UI

    Returns:
        Project information with download URL and optional Git repo URL

    Example request:
        ```json
        {
            "agent_name": "weather-agent",
            "description": "An agent that provides weather information",
            "prompt": "You are a helpful weather assistant",
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get weather for a location"
                },
                {
                    "name": "get_forecast",
                    "description": "Get weather forecast"
                }
            ],
            "create_git_repo": true,
            "git_repo_name": "my-weather-agent"
        }
        ```
    """
    try:
        # Validate agent name
        if not request.agent_name.replace("-", "").replace("_", "").isalnum():
            raise HTTPException(
                status_code=400,
                detail="Agent name must contain only alphanumeric characters, hyphens, and underscores",
            )

        # Create output directory
        output_dir = TEMP_DIR / "projects"
        output_dir.mkdir(exist_ok=True)

        # Generate project
        project_path, file_count = generate_project(request, output_dir)

        # Create zip file
        zip_name = f"{request.agent_name}"
        zip_path = DOWNLOADS_DIR / zip_name
        create_zip_archive(project_path, zip_path)

        # Create download URL
        download_url = f"/downloads/{zip_name}.zip"

        # Optionally create Git repository
        git_repo_url = None
        if request.create_git_repo:
            repo_name = request.git_repo_name or request.agent_name
            git_repo_url = create_git_repository(project_path, repo_name)

        return GenerateProjectResponse(
            project_name=request.agent_name,
            download_url=download_url,
            git_repo_url=git_repo_url,
            files_generated=file_count,
            message=f"Project '{request.agent_name}' generated successfully!",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Project generation failed: {e!s}"
        )


@app.get("/api/v1/download/{filename}")
async def download_project(filename: str):
    """Download a generated project zip file.

    Args:
        filename: Name of the zip file to download

    Returns:
        Zip file download
    """
    file_path = DOWNLOADS_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="application/zip",
        filename=filename,
    )
