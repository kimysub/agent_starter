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

"""OpenAI-compatible LLM implementation for ADK.

This module provides a custom BaseLlm implementation that works with
OpenAI-compatible API endpoints (OpenAI, vLLM, Ollama, X.AI, etc.).
"""

import os
from collections.abc import AsyncGenerator
from typing import Any

from google.adk.models import BaseLlm, LlmRequest, LlmResponse
from google.genai.types import Content, Part, FunctionCall, FunctionResponse, FinishReason
from openai import AsyncOpenAI


class OpenAICompatibleLlm(BaseLlm):
    """OpenAI-compatible LLM implementation for ADK.

    This class allows ADK agents to use OpenAI-compatible API endpoints
    without requiring google.genai SDK for model calls.

    Example:
        ```python
        from app_utils.openai_llm import OpenAICompatibleLlm

        llm = OpenAICompatibleLlm(
            model="grok-beta",
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_ENDPOINT_URL"),
        )

        agent = Agent(
            name="my_agent",
            model=llm,  # Pass custom LLM instance
            instruction="You are a helpful assistant.",
            tools=[my_tool],
        )
        ```
    """

    api_key: str = ""
    base_url: str = ""
    _client: Any = None  # AsyncOpenAI client (set as Any to avoid pydantic validation)

    def __init__(self, **data):
        """Initialize the OpenAI-compatible LLM.

        Args:
            model: Model name (e.g., "grok-beta", "llama-3.1-8b")
            api_key: API key for authentication
            base_url: Base URL for the API endpoint
        """
        super().__init__(**data)

        # Get configuration from environment if not provided
        if not self.api_key:
            self.api_key = os.getenv("LLM_API_KEY", "not-needed")
        if not self.base_url:
            self.base_url = os.getenv("LLM_ENDPOINT_URL", "http://localhost:8001/v1")

        # Initialize OpenAI client
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    @classmethod
    def supported_models(cls) -> list[str]:
        """Returns list of supported model patterns.

        Returns empty list to match all models (since OpenAI-compatible
        endpoints can serve any model).
        """
        return [".*"]  # Match all models

    async def generate_content_async(
        self,
        llm_request: LlmRequest,
        stream: bool = False,
    ) -> AsyncGenerator[LlmResponse, None]:
        """Generate content using OpenAI-compatible API.

        Args:
            llm_request: The request containing contents and configuration
            stream: Whether to stream the response

        Yields:
            LlmResponse objects containing the model's response
        """
        # Convert ADK request to OpenAI format
        messages = self._convert_contents_to_messages(llm_request.contents)
        tools = self._convert_tools(llm_request.tools_dict) if llm_request.tools_dict else None

        # Prepare OpenAI API call parameters
        kwargs = {
            "model": llm_request.model or self.model,
            "messages": messages,
            "stream": stream,
        }

        # Add tools if provided
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # Add generation config if provided
        if llm_request.config:
            if hasattr(llm_request.config, 'temperature') and llm_request.config.temperature is not None:
                kwargs["temperature"] = llm_request.config.temperature
            if hasattr(llm_request.config, 'max_output_tokens') and llm_request.config.max_output_tokens is not None:
                kwargs["max_tokens"] = llm_request.config.max_output_tokens
            if hasattr(llm_request.config, 'top_p') and llm_request.config.top_p is not None:
                kwargs["top_p"] = llm_request.config.top_p

        try:
            if stream:
                # Streaming response
                async for chunk in await self._client.chat.completions.create(**kwargs):
                    llm_response = self._convert_streaming_chunk_to_response(chunk)
                    if llm_response:
                        yield llm_response
            else:
                # Non-streaming response
                response = await self._client.chat.completions.create(**kwargs)
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
        """Convert ADK Content objects to OpenAI messages format.

        Args:
            contents: List of Content objects from ADK

        Returns:
            List of message dictionaries in OpenAI format
        """
        messages = []

        for content in contents:
            role = content.role if content.role else "user"
            # Map ADK roles to OpenAI roles
            if role == "model":
                role = "assistant"

            message = {"role": role}

            # Convert parts to content
            if content.parts:
                # For now, handle simple text parts
                # TODO: Handle multimodal parts (images, etc.)
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
                        # This is a tool response from previous turn
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
        """Convert ADK tools to OpenAI tools format.

        Args:
            tools_dict: Dictionary of tool name to BaseTool

        Returns:
            List of tool definitions in OpenAI format
        """
        tools = []

        for tool_name, tool in tools_dict.items():
            # Get tool schema
            if hasattr(tool, 'get_schema'):
                schema = tool.get_schema()
            else:
                # Fallback: create basic schema
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
        """Convert OpenAI response to ADK LlmResponse.

        Args:
            response: OpenAI chat completion response

        Returns:
            LlmResponse object
        """
        choice = response.choices[0]
        message = choice.message

        # Convert to Content with Parts
        parts = []

        # Add text content
        if message.content:
            parts.append(Part(text=message.content))

        # Add tool calls if present
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                parts.append(FunctionCall(
                    name=tool_call.function.name,
                    args=tool_call.function.arguments,
                ))

        content = Content(role="model", parts=parts) if parts else None

        # Map finish reason
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
        """Convert OpenAI streaming chunk to ADK LlmResponse.

        Args:
            chunk: OpenAI streaming chunk

        Returns:
            LlmResponse object or None if no content
        """
        if not chunk.choices:
            return None

        choice = chunk.choices[0]
        delta = choice.delta

        parts = []

        # Add text content from delta
        if hasattr(delta, 'content') and delta.content:
            parts.append(Part(text=delta.content))

        # Add tool calls from delta
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

        # Check if this is the final chunk
        is_final = choice.finish_reason is not None

        return LlmResponse(
            content=content,
            partial=not is_final,
            turn_complete=is_final,
            finish_reason=FinishReason.STOP if is_final else None,
        )
