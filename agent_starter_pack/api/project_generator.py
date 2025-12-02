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

"""Full project generation logic for API."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

from .models import GenerateProjectRequest, ToolInfo


def generate_tool_stub(tool: ToolInfo) -> str:
    """Generate a simple tool function stub.

    Args:
        tool: Tool information with name and description

    Returns:
        Generated Python function code
    """
    return f'''
def {tool.name}(query: str) -> str:
    """{tool.description}

    Args:
        query: Input query for the tool

    Returns:
        Tool result as a string
    """
    # TODO: Implement {tool.name}
    return f"Result from {tool.name}: {{query}}"
'''


def generate_project(
    request: GenerateProjectRequest, output_dir: Path
) -> tuple[Path, int]:
    """Generate a complete agent project using CLI.

    Args:
        request: Project generation request from UI
        output_dir: Directory to create the project in

    Returns:
        Tuple of (project_path, number_of_files_generated)
    """
    project_path = output_dir / request.agent_name

    # Call CLI command via subprocess
    cmd = [
        sys.executable,
        "-m",
        "agent_starter_pack.cli.main",
        "create",
        request.agent_name,
        "--output-dir",
        str(output_dir),
        "--agent",
        "adk_a2a_base",
        "--deployment-target",
        "on_premise",
        "--auto-approve",
        "--skip-checks",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to create project: {result.stderr or result.stdout}"
        )

    # Customize agent.py with user's description, prompt, and tools
    agent_py_path = project_path / "app" / "agent.py"
    if agent_py_path.exists():
        customize_agent_file(agent_py_path, request)

    # Count generated files
    file_count = sum(1 for _ in project_path.rglob("*") if _.is_file())

    return project_path, file_count


def customize_agent_file(agent_py_path: Path, request: GenerateProjectRequest) -> None:
    """Customize the generated agent.py with user's specifications.

    Args:
        agent_py_path: Path to agent.py file
        request: User's project request
    """
    # Read existing agent.py
    content = agent_py_path.read_text(encoding="utf-8")

    # Replace description
    old_desc = 'description="An agent that can provide information about the weather and time."'
    new_desc = f'description="{request.description}"'
    content = content.replace(old_desc, new_desc)

    # Replace instruction/prompt
    old_instruction = 'instruction="You are a helpful AI assistant designed to provide accurate and useful information."'
    new_instruction = f'instruction="{request.prompt}"'
    content = content.replace(old_instruction, new_instruction)

    # If tools are provided, add them
    if request.tools:
        # Generate tool functions
        tool_functions = []
        tool_names = []
        for tool in request.tools:
            tool_functions.append(generate_tool_stub(tool))
            tool_names.append(tool.name)

        # Find where to insert tools (before agent creation)
        agent_creation_marker = "# Create ADK agent"
        if agent_creation_marker in content:
            parts = content.split(agent_creation_marker)

            # Find the llm creation section
            llm_end_pattern = r"llm = LiteLlm\([^)]+\)\n"
            llm_match = re.search(llm_end_pattern, parts[0], re.DOTALL)
            if llm_match:
                llm_section_end = llm_match.end()
                # Keep everything up to and including llm creation
                parts[0] = parts[0][:llm_section_end]

                # Insert new tools
                parts[0] += "\n" + "\n".join(tool_functions) + "\n\n"

                # Update tools list in Agent creation
                tools_list_str = ", ".join(tool_names)
                parts[1] = re.sub(
                    r"tools=\[get_weather, get_current_time\]",
                    f"tools=[{tools_list_str}]",
                    parts[1],
                )

                content = agent_creation_marker.join(parts)

    # Write back
    agent_py_path.write_text(content, encoding="utf-8")


def create_zip_archive(project_path: Path, zip_path: Path) -> None:
    """Create a zip archive of the project.

    Args:
        project_path: Path to the project directory
        zip_path: Path where zip file should be created (without .zip extension)
    """
    shutil.make_archive(str(zip_path), "zip", project_path.parent, project_path.name)


def create_git_repository(
    project_path: Path, repo_name: str | None = None
) -> str | None:
    """Create a Git repository and optionally push to GitHub.

    Args:
        project_path: Path to the project directory
        repo_name: Optional custom repository name

    Returns:
        Git repository URL if created, None otherwise
    """
    try:
        # Initialize git repo
        subprocess.run(
            ["git", "init"], cwd=project_path, check=True, capture_output=True
        )

        # Configure git (use generic name/email)
        subprocess.run(
            ["git", "config", "user.name", "Agent Starter Pack API"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "api@agent-starter-pack.local"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )

        # Add all files
        subprocess.run(
            ["git", "add", "."], cwd=project_path, check=True, capture_output=True
        )

        # Create initial commit
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "Initial commit - Generated by Agent Starter Pack API",
            ],
            cwd=project_path,
            check=True,
            capture_output=True,
        )

        # Return local git path for now
        # In production, you would push to GitHub/GitLab here
        return f"file://{project_path.absolute()}"

    except subprocess.CalledProcessError as e:
        # Git creation failed, but this is optional
        print(f"Git repository creation failed: {e}")
        return None
