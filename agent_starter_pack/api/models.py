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

"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field


class ToolInfo(BaseModel):
    """Simple tool information from UI."""

    name: str = Field(..., description="Tool/function name")
    description: str = Field(..., description="What the tool does")


class GenerateProjectRequest(BaseModel):
    """Request model for generating agent project from UI."""

    agent_name: str = Field(..., description="Name of the agent/project")
    description: str = Field(..., description="Description of what the agent does")
    prompt: str = Field(..., description="System prompt/instruction for the agent")
    tools: list[ToolInfo] = Field(
        default_factory=list, description="List of tools the agent should have"
    )
    create_git_repo: bool = Field(
        default=False, description="Whether to create a Git repository"
    )
    git_repo_name: str | None = Field(
        None, description="Git repository name (if create_git_repo is True)"
    )


class GenerateProjectResponse(BaseModel):
    """Response model for generated agent project."""

    project_name: str = Field(..., description="Name of the generated project")
    download_url: str = Field(..., description="URL to download zip file")
    git_repo_url: str | None = Field(
        None, description="Git repository URL (if created)"
    )
    files_generated: int = Field(..., description="Number of files generated")
    message: str = Field(..., description="Success message")
