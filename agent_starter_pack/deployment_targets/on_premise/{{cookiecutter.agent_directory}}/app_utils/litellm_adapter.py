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

"""LiteLLM adapter for ADK.

This module provides a BaseLlm implementation using LiteLLM, which supports
100+ LLM providers with a unified interface.
"""

import os
from collections.abc import AsyncGenerator
from typing import Any

from google.adk.models import BaseLlm, LlmRequest, LlmResponse
from google.genai.types import Content, Part, FunctionCall, FunctionResponse, FinishReason
import litellm


class LiteLLMAdapter(BaseLlm):
    """LiteLLM adapter for ADK.

    Uses LiteLLM to support any LLM provider (OpenAI, Anthropic, vLLM, Ollama, etc.)
    without needing google.genai SDK.

    Supported providers:
    - OpenAI (openai/gpt-4, openai/gpt-3.5-turbo)
    - Anthropic (anthropic/claude-3-5-sonnet-20241022)
    - X.AI (xai/grok-beta)
    - vLLM (openai/model-name with api_base)
    - Ollama (ollama/llama3.1)
    - And 100+ more!

    Example:
        ```python
        from app_utils.litellm_adapter import LiteLLMAdapter

        # For OpenAI
        llm = LiteLLMAdapter(model="openai/gpt-4o-mini")

        # For X.AI Grok
        llm = LiteLLMAdapter(
            model="xai/grok-beta",
            api_key=os.getenv("XAI_API_KEY"),
        )

        # For local vLLM
        llm = LiteLLMAdapter(
            model="openai/llama-3.1-8b",  # Use openai/ prefix for OpenAI-compatible
            api_base="http://localhost:8001/v1",
        )

        # For Ollama
        llm = LiteLLMAdapter(model="ollama/llama3.1")

        agent = Agent(
            name="my_agent",
            model=llm,  # Pass LiteLLM adapter
            instruction="You are a helpful assistant.",
            tools=[my_tool],
        )
        ```

    Environment variables (optional):
    - LLM_API_KEY: API key for the provider
    - LLM_ENDPOINT_URL: Custom API endpoint (for vLLM, etc.)
    - LLM_MODEL_NAME: Model name with provider prefix
    """

    api_key: str = ""
    api_base: str = ""

    def __init__(self, **data):
        """Initialize the LiteLLM adapter.

        Args:
            model: Model name with provider prefix (e.g., "openai/gpt-4", "xai/grok-beta")
            api_key: API key for authentication (optional, can use env vars)
            api_base: Custom API base URL (for vLLM, self-hosted, etc.)
        """
        super().__init__(**data)

        # Get configuration from environment if not provided
        if not self.api_key:
            self.api_key = os.getenv("LLM_API_KEY", "")
        if not self.api_base:
            self.api_base = os.getenv("LLM_ENDPOINT_URL", "")

        # Configure LiteLLM
        if self.api_key:
            litellm.api_key = self.api_key
        if self.api_base:
            litellm.api_base = self.api_base

        # Set verbose mode from environment
        litellm.set_verbose = os.getenv("LITELLM_VERBOSE", "false").lower() == "true"

    @classmethod
    def supported_models(cls) -> list[str]:
        """Returns list of supported model patterns.

        LiteLLM supports 100+ providers, so we match all models.
        """
        return [".*"]

    async def generate_content_async(
        self,
        llm_request: LlmRequest,
        stream: bool = False,
    ) -> AsyncGenerator[LlmResponse, None]:
        """Generate content using LiteLLM.

        Args:
            llm_request: The request containing contents and configuration
            stream: Whether to stream the response

        Yields:
            LlmResponse objects containing the model's response
        """
        # Convert ADK request to LiteLLM format (OpenAI-compatible)
        messages = self._convert_contents_to_messages(llm_request.contents)

        # Prepare LiteLLM parameters
        kwargs = {
            "model": llm_request.model or self.model,
            "messages": messages,
            "stream": stream,
        }

        # Add API key if specified
        if self.api_key:
            kwargs["api_key"] = self.api_key

        # Add custom API base if specified
        if self.api_base:
            kwargs["api_base"] = self.api_base

        # Add generation config if provided
        if llm_request.config:
            if hasattr(llm_request.config, 'temperature') and llm_request.config.temperature is not None:
                kwargs["temperature"] = llm_request.config.temperature
            if hasattr(llm_request.config, 'max_output_tokens') and llm_request.config.max_output_tokens is not None:
                kwargs["max_tokens"] = llm_request.config.max_output_tokens
            if hasattr(llm_request.config, 'top_p') and llm_request.config.top_p is not None:
                kwargs["top_p"] = llm_request.config.top_p

        # Add tools if provided
        if llm_request.tools_dict:
            tools = self._convert_tools(llm_request.tools_dict)
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

        try:
            if stream:
                # Streaming response
                response = await litellm.acompletion(**kwargs)
                async for chunk in response:
                    llm_response = self._convert_streaming_chunk_to_response(chunk)
                    if llm_response:
                        yield llm_response
            else:
                # Non-streaming response
                response = await litellm.acompletion(**kwargs)
                yield self._convert_response_to_llm_response(response)

        except Exception as e:
            # Return error response
            yield LlmResponse(
                content=None,
                error_code="api_error",
                error_message=str(e),
                partial=False,
            )

    def _convert_contents_to_messages(self, contents: list[Content]) -> list[dict]:
        """Convert ADK Content objects to OpenAI messages format."""
        messages = []

        for content in contents:
            role = content.role if content.role else "user"
            if role == "model":
                role = "assistant"

            message = {"role": role}
            text_parts = []
            tool_calls = []

            for part in content.parts:
                if isinstance(part, str):
                    text_parts.append(part)
                elif hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
                elif isinstance(part, FunctionCall):
                    tool_calls.append({
                        "id": f"call_{part.name}",
                        "type": "function",
                        "function": {
                            "name": part.name,
                            "arguments": str(part.args) if part.args else "{}",
                        }
                    })
                elif isinstance(part, FunctionResponse):
                    messages.append({
                        "role": "tool",
                        "tool_call_id": f"call_{part.name}",
                        "content": str(part.response),
                    })
                    continue

            if text_parts:
                message["content"] = " ".join(text_parts)
            if tool_calls:
                message["tool_calls"] = tool_calls
                if not text_parts:
                    message["content"] = None

            if "content" in message or "tool_calls" in message:
                messages.append(message)

        return messages

    def _convert_tools(self, tools_dict: dict) -> list[dict]:
        """Convert ADK tools to OpenAI tools format."""
        tools = []

        for tool_name, tool in tools_dict.items():
            if hasattr(tool, 'get_schema'):
                schema = tool.get_schema()
            else:
                schema = {
                    "name": tool_name,
                    "description": getattr(tool, 'description', ''),
                    "parameters": {"type": "object", "properties": {}},
                }

            tools.append({
                "type": "function",
                "function": {
                    "name": schema.get("name", tool_name),
                    "description": schema.get("description", ""),
                    "parameters": schema.get("parameters", {"type": "object", "properties": {}}),
                }
            })

        return tools

    def _convert_response_to_llm_response(self, response: Any) -> LlmResponse:
        """Convert LiteLLM response to ADK LlmResponse."""
        choice = response.choices[0]
        message = choice.message

        parts = []

        if hasattr(message, 'content') and message.content:
            parts.append(Part(text=message.content))

        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                parts.append(FunctionCall(
                    name=tool_call.function.name,
                    args=tool_call.function.arguments,
                ))

        content = Content(role="model", parts=parts) if parts else None

        finish_reason_map = {
            "stop": FinishReason.STOP,
            "length": FinishReason.MAX_TOKENS,
            "tool_calls": FinishReason.STOP,
            "content_filter": FinishReason.SAFETY,
        }
        finish_reason = finish_reason_map.get(choice.finish_reason, FinishReason.STOP)

        return LlmResponse(
            content=content,
            finish_reason=finish_reason,
            partial=False,
            turn_complete=True,
        )

    def _convert_streaming_chunk_to_response(self, chunk: Any) -> LlmResponse | None:
        """Convert LiteLLM streaming chunk to ADK LlmResponse."""
        if not chunk.choices:
            return None

        choice = chunk.choices[0]
        delta = choice.delta

        parts = []

        if hasattr(delta, 'content') and delta.content:
            parts.append(Part(text=delta.content))

        if hasattr(delta, 'tool_calls') and delta.tool_calls:
            for tool_call in delta.tool_calls:
                if tool_call.function:
                    parts.append(FunctionCall(
                        name=tool_call.function.name,
                        args=tool_call.function.arguments,
                    ))

        if not parts:
            return None

        content = Content(role="model", parts=parts)
        is_final = choice.finish_reason is not None

        return LlmResponse(
            content=content,
            partial=not is_final,
            turn_complete=is_final,
            finish_reason=FinishReason.STOP if is_final else None,
        )
