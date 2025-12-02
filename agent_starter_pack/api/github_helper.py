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

"""GitHub helper for pushing agent projects to folders in a fixed repository."""

import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path


def push_agent_to_github(
    project_path: Path,
    agent_name: str,
    repo_name: str,
    github_token: str | None = None,
    github_org: str | None = None,
    github_enterprise_url: str | None = None,
    branch: str = "main",
) -> tuple[str, str]:
    """Push agent project to a numbered folder in an existing GitHub repository.

    Args:
        project_path: Path to the generated agent project
        agent_name: Name of the agent (used for folder name)
        repo_name: Name of the fixed GitHub repository to push to
        github_token: GitHub Personal Access Token
        github_org: Optional organization name
        github_enterprise_url: Optional GitHub Enterprise URL
        branch: Branch name to push to

    Returns:
        Tuple of (folder_name, github_url_with_folder)

    Raises:
        RuntimeError: If push fails
    """
    # Get token from parameter or environment
    token = github_token or os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GitHub token is required for push")

    # Determine GitHub base URL
    if github_enterprise_url:
        github_base = github_enterprise_url.rstrip("/")
    else:
        github_base = "https://github.com"

    # Construct repository URLs
    if github_org:
        repo_owner = github_org
    else:
        # Get authenticated user
        repo_owner = _get_github_username(token, github_enterprise_url)

    clone_url = f"{github_base}/{repo_owner}/{repo_name}.git"
    html_url = f"{github_base}/{repo_owner}/{repo_name}"

    # Generate unique folder name with random 4-digit suffix
    folder_name = f"{agent_name}-{random.randint(0, 9999):04d}"

    # Create temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        repo_path = temp_path / repo_name

        try:
            # Clone the existing repository
            auth_clone_url = clone_url.replace("https://", f"https://{token}@")
            subprocess.run(
                ["git", "clone", auth_clone_url, str(repo_path)],
                check=True,
                capture_output=True,
            )

            # Create folder for this agent
            agent_folder = repo_path / folder_name
            agent_folder.mkdir(exist_ok=True)

            # Copy all project files to the agent folder
            for item in project_path.iterdir():
                if item.name == ".git":
                    continue  # Skip git directory from generated project
                if item.is_dir():
                    shutil.copytree(item, agent_folder / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, agent_folder / item.name)

            # Configure git user
            subprocess.run(
                ["git", "config", "user.name", "Agent Starter Pack API"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "api@agent-starter-pack.local"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            # Add the new folder
            subprocess.run(
                ["git", "add", folder_name],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            # Commit the changes
            commit_message = f"Add agent: {folder_name}"
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            # Push to GitHub
            subprocess.run(
                ["git", "push", "origin", branch],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            # Return folder name and URL to the folder
            folder_url = f"{html_url}/tree/{branch}/{folder_name}"
            return folder_name, folder_url

        except subprocess.CalledProcessError as e:
            error_output = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"Failed to push to GitHub: {error_output}") from e


def _get_github_username(
    github_token: str, github_enterprise_url: str | None = None
) -> str:
    """Get the authenticated user's GitHub username.

    Args:
        github_token: GitHub Personal Access Token
        github_enterprise_url: Optional GitHub Enterprise URL

    Returns:
        GitHub username

    Raises:
        RuntimeError: If unable to get username
    """
    import requests

    # Determine API base URL
    if github_enterprise_url:
        api_base = f"{github_enterprise_url.rstrip('/')}/api/v3"
    else:
        api_base = "https://api.github.com"

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(f"{api_base}/user", headers=headers, timeout=30)

    if response.status_code == 200:
        return response.json()["login"]
    else:
        raise RuntimeError(
            f"Failed to get GitHub username: {response.status_code} {response.text}"
        )
