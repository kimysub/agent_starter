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

"""ADK Agent with Agent2Agent (A2A) Protocol for on-premise deployment.

This agent combines:
- LiteLLM for OpenAI-compatible endpoints (vLLM, Ollama, local LLMs, etc.)
- Agent2Agent (A2A) protocol for agent collaboration

Based on patterns from: https://github.com/a2aproject/a2a-samples
"""

import datetime
import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env file
load_dotenv()

# Get LLM configuration from environment variables
llm_endpoint = os.getenv("LLM_ENDPOINT_URL", "http://localhost:8001/v1")
llm_model = os.getenv("LLM_MODEL_NAME", "openai/llama-3.1-8b")
llm_api_key = os.getenv("LLM_API_KEY", "not-needed")

# Use ADK's built-in LiteLLM support!
# LiteLlm supports 100+ providers: OpenAI, Anthropic, vLLM, Ollama, X.AI, etc.
llm = LiteLlm(
    model=llm_model,
    api_key=llm_api_key,
    api_base=llm_endpoint,
)


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


# Create ADK agent with LiteLLM and A2A protocol support
root_agent = Agent(
    name="root_agent",
    model=llm,  # Use LiteLlm instance for OpenAI-compatible endpoints
    description="An agent that can provide information about the weather and time.",
    instruction="You are a helpful AI assistant designed to provide accurate and useful information.",
    tools=[get_weather, get_current_time],
)

# Convert ADK agent to A2A application
# This enables the agent to communicate with other agents using the Agent2Agent protocol
# Works with any OpenAI-compatible LLM endpoint (vLLM, Ollama, LocalAI, etc.)
a2a_app = to_a2a(root_agent, port=int(os.getenv("PORT", "8001")))
