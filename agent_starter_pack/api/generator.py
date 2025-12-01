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

"""Agent code generation logic."""

from pathlib import Path

from .models import GenerateAgentRequest, ToolDefinition


def generate_tool_function(tool: ToolDefinition) -> str:
    """Generate Python function code from a tool definition.

    Args:
        tool: Tool definition containing name, description, parameters, and implementation

    Returns:
        Generated Python function code as a string
    """
    return f'''
def {tool.name}({tool.parameters}) -> str:
    """{tool.description}"""
{tool.implementation}
'''


def generate_agent_code(request: GenerateAgentRequest) -> str:
    """Generate agent.py code based on request parameters.

    Args:
        request: Generate agent request containing configuration

    Returns:
        Generated agent.py code as a string
    """
    # Header and imports
    code_parts = [
        '# Copyright 2025 Google LLC',
        '#',
        '# Licensed under the Apache License, Version 2.0 (the "License");',
        '# you may not use this file except in compliance with the License.',
        '# You may obtain a copy of the License at',
        '#',
        '#     http://www.apache.org/licenses/LICENSE-2.0',
        '#',
        '# Unless required by applicable law or agreed to in writing, software',
        '# distributed under the License is distributed on an "AS IS" BASIS,',
        '# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.',
        '# See the License for the specific language governing permissions and',
        '# limitations under the License.',
        '',
        f'"""Generated agent for {request.project_name}."""',
        '',
        'import os',
    ]

    # Add datetime import if needed for default tools
    if not request.tools:
        code_parts.extend(
            [
                'import datetime',
                'from zoneinfo import ZoneInfo',
            ]
        )

    code_parts.append('')

    # Agent type specific imports
    if request.agent_type == "adk_a2a_base":
        code_parts.extend(
            [
                'from google.adk.agents import Agent',
                'from google.adk.models.lite_llm import LiteLlm',
                'from google.adk.a2a.utils.agent_to_a2a import to_a2a',
                '',
                'from dotenv import load_dotenv',
                'load_dotenv()',
                '',
            ]
        )
    elif request.agent_type == "adk_base":
        code_parts.extend(
            [
                'from google.adk.agents import Agent',
                'from google.adk.models.lite_llm import LiteLlm',
                '',
                'from dotenv import load_dotenv',
                'load_dotenv()',
                '',
            ]
        )

    # Environment variables section
    code_parts.extend(
        [
            '# Get LLM configuration from environment variables',
            'llm_endpoint = os.getenv("LLM_ENDPOINT_URL", "http://localhost:8001/v1")',
            'llm_model = os.getenv("LLM_MODEL_NAME", "openai/llama-3.1-8b")',
            'llm_api_key = os.getenv("LLM_API_KEY", "not-needed")',
        ]
    )

    # Add custom environment variables
    for env_var in request.env_vars:
        default_val = env_var.default_value
        # Quote string defaults
        if not default_val.isdigit() and default_val not in ["True", "False"]:
            default_val = f'"{default_val}"'

        comment = f"  # {env_var.description}" if env_var.description else ""
        code_parts.append(
            f'{env_var.name.lower()} = os.getenv("{env_var.name}", {default_val}){comment}'
        )

    code_parts.extend(
        [
            '',
            '# Use ADK\'s built-in LiteLLM support!',
            '# LiteLlm supports 100+ providers: OpenAI, Anthropic, vLLM, Ollama, X.AI, etc.',
            'llm = LiteLlm(',
            '    model=llm_model,',
            '    api_key=llm_api_key,',
            '    api_base=llm_endpoint,',
            ')',
            '',
        ]
    )

    # Generate custom tools or use default tools
    if request.tools:
        for tool in request.tools:
            code_parts.append(generate_tool_function(tool))
    else:
        # Default tools (weather and time)
        code_parts.extend(
            [
                'def get_weather(query: str) -> str:',
                '    """Simulates a web search. Use it get information on weather.',
                '',
                '    Args:',
                '        query: A string containing the location to get weather information for.',
                '',
                '    Returns:',
                '        A string with the simulated weather information for the queried location.',
                '    """',
                '    if "sf" in query.lower() or "san francisco" in query.lower():',
                '        return "It\'s 60 degrees and foggy."',
                '    return "It\'s 90 degrees and sunny."',
                '',
                '',
                'def get_current_time(query: str) -> str:',
                '    """Simulates getting the current time for a city.',
                '',
                '    Args:',
                '        city: The name of the city to get the current time for.',
                '',
                '    Returns:',
                '        A string with the current time information.',
                '    """',
                '    if "sf" in query.lower() or "san francisco" in query.lower():',
                '        tz_identifier = "America/Los_Angeles"',
                '    else:',
                '        return f"Sorry, I don\'t have timezone information for query: {query}."',
                '',
                '    tz = ZoneInfo(tz_identifier)',
                '    now = datetime.datetime.now(tz)',
                '    return f"The current time for query {query} is {now.strftime(\'%Y-%m-%d %H:%M:%S %Z%z\')}"',
                '',
            ]
        )

    # Agent creation
    tool_names = (
        [tool.name for tool in request.tools]
        if request.tools
        else ["get_weather", "get_current_time"]
    )
    tools_list = ", ".join(tool_names)

    description = (
        request.agent_description
        or "An agent that can provide information about the weather and time."
    )
    instruction = (
        request.agent_instruction
        or "You are a helpful AI assistant designed to provide accurate and useful information."
    )

    code_parts.extend(
        [
            '# Create ADK agent with A2A protocol support'
            if request.agent_type == "adk_a2a_base"
            else '# Create ADK agent',
            'root_agent = Agent(',
            '    name="root_agent",',
            '    model=llm,',
            f'    description="{description}",',
            f'    instruction="{instruction}",',
            f'    tools=[{tools_list}],',
            ')',
            '',
        ]
    )

    # A2A conversion for adk_a2a_base
    if request.agent_type == "adk_a2a_base":
        code_parts.extend(
            [
                '# Convert ADK agent to A2A application',
                '# This enables the agent to communicate with other agents using the Agent2Agent protocol',
                'a2a_app = to_a2a(root_agent, port=int(os.getenv("PORT", "8001")))',
                'app = a2a_app',
                '',
            ]
        )
    else:
        code_parts.extend(['app = root_agent', ''])

    return '\n'.join(code_parts)
