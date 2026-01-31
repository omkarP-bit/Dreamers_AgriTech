"""
Groq ChatCompletionClient Wrapper for AutoGen 0.7.5

Key fixes:
1. Proper CreateResult return type (not just string)
2. Correct message format handling
3. Compatible with RoundRobinGroupChat
"""

from typing import Any, AsyncIterator, Dict, List, Optional, Sequence, Union
from autogen_core.models import (
    ChatCompletionClient,
    LLMMessage,
    CreateResult,
    RequestUsage,
)
from autogen_core.models._types import FunctionExecutionResult
from groq import Groq


class GroqChatCompletionClient(ChatCompletionClient):
    """
    ChatCompletionClient implementation for Groq
    Compatible with AutoGen 0.7.5 RoundRobinGroupChat
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize Groq client wrapper
        
        Args:
            api_key: Groq API key
            model: Model name
            temperature: Temperature for generation
            max_tokens: Max tokens in response
        """
        self.client = Groq(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._actual_usage: Optional[RequestUsage] = None
        self._total_usage: Optional[RequestUsage] = None
    
    @property
    def model_info(self) -> Dict[str, Any]:
        """Return model information"""
        return {
            "family": "groq",
            "model": self._model,
            "vision": False,
            "function_calling": True,  # Groq supports function calling
        }
    
    @property
    def actual_usage(self) -> Optional[RequestUsage]:
        """Return actual token usage from last call"""
        return self._actual_usage
    
    @property
    def total_usage(self) -> Optional[RequestUsage]:
        """Return total accumulated token usage"""
        return self._total_usage
    
    @property
    def remaining_tokens(self) -> Optional[int]:
        """Return remaining tokens (not applicable for Groq)"""
        return None
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Return client capabilities"""
        return {
            "vision": False,
            "function_calling": True,
            "streaming": True,
        }
    
    async def close(self) -> None:
        """Close the client connection"""
        pass
    
    def _convert_messages(self, messages: Sequence[LLMMessage]) -> List[Dict[str, str]]:
        """
        Convert AutoGen messages to Groq format
        
        Args:
            messages: AutoGen LLMMessage objects
            
        Returns:
            List of Groq-formatted messages
        """
        groq_messages = []
        
        for msg in messages:
            if isinstance(msg, dict):
                # Already a dict
                groq_messages.append({
                    "role": msg.get("role", "user"),
                    "content": str(msg.get("content", ""))
                })
            else:
                # LLMMessage object
                role = getattr(msg, "role", "user")
                content = getattr(msg, "content", "")
                
                # Handle different content types
                if isinstance(content, str):
                    content_str = content
                elif isinstance(content, list):
                    # Multiple content parts (text, images, etc.)
                    content_str = " ".join(
                        str(part.get("text", "")) if isinstance(part, dict) else str(part)
                        for part in content
                    )
                else:
                    content_str = str(content)
                
                groq_messages.append({
                    "role": role,
                    "content": content_str
                })
        
        return groq_messages
    
    async def create(
        self,
        messages: Sequence[LLMMessage],
        *,
        tools: Sequence[Any] = [],
        json_output: Optional[bool] = None,
        extra_create_args: Dict[str, Any] = {},
        cancellation_token: Optional[Any] = None,
    ) -> CreateResult:
        """
        Create a completion using Groq
        
        CRITICAL: Must return CreateResult, not just a string
        
        Args:
            messages: List of messages
            tools: List of available tools
            json_output: Whether to output JSON
            extra_create_args: Additional parameters
            cancellation_token: Cancellation token
            
        Returns:
            CreateResult with content and usage
        """
        try:
            # Convert messages
            groq_messages = self._convert_messages(messages)
            
            # Prepare API call parameters
            api_params = {
                "model": self._model,
                "messages": groq_messages,
                "temperature": extra_create_args.get("temperature", self._temperature),
                "max_tokens": extra_create_args.get("max_tokens", self._max_tokens),
            }
            
            # Add JSON mode if requested
            if json_output:
                api_params["response_format"] = {"type": "json_object"}
            
            # Call Groq API
            response = self.client.chat.completions.create(**api_params)
            
            # Extract response content
            content = response.choices[0].message.content or ""
            
            # Store usage information
            if hasattr(response, 'usage') and response.usage:
                self._actual_usage = RequestUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                )
                
                # Update total usage
                if self._total_usage is None:
                    self._total_usage = self._actual_usage
                else:
                    self._total_usage = RequestUsage(
                        prompt_tokens=self._total_usage.prompt_tokens + self._actual_usage.prompt_tokens,
                        completion_tokens=self._total_usage.completion_tokens + self._actual_usage.completion_tokens,
                    )
            
            # Return CreateResult (CRITICAL - not just a string!)
            return CreateResult(
                content=content,
                usage=self._actual_usage,
                finish_reason=response.choices[0].finish_reason or "stop",
                cached=False,
            )
            
        except Exception as e:
            print(f"❌ Error calling Groq: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def create_stream(
        self,
        messages: Sequence[LLMMessage],
        *,
        tools: Sequence[Any] = [],
        json_output: Optional[bool] = None,
        extra_create_args: Dict[str, Any] = {},
        cancellation_token: Optional[Any] = None,
    ) -> AsyncIterator[Union[str, CreateResult]]:
        """
        Create a streaming completion using Groq
        
        Args:
            messages: List of messages
            tools: List of available tools
            json_output: Whether to output JSON
            extra_create_args: Additional parameters
            cancellation_token: Cancellation token
            
        Yields:
            Response chunks or final CreateResult
        """
        try:
            # Convert messages
            groq_messages = self._convert_messages(messages)
            
            # Prepare API call parameters
            api_params = {
                "model": self._model,
                "messages": groq_messages,
                "temperature": extra_create_args.get("temperature", self._temperature),
                "max_tokens": extra_create_args.get("max_tokens", self._max_tokens),
                "stream": True,
            }
            
            # Add JSON mode if requested
            if json_output:
                api_params["response_format"] = {"type": "json_object"}
            
            # Call Groq API with streaming
            response = self.client.chat.completions.create(**api_params)
            
            # Accumulate chunks for final result
            accumulated_content = ""
            
            # Yield chunks as they arrive
            for chunk in response:
                if chunk.choices[0].delta.content:
                    chunk_content = chunk.choices[0].delta.content
                    accumulated_content += chunk_content
                    yield chunk_content
            
            # Yield final CreateResult
            yield CreateResult(
                content=accumulated_content,
                usage=self._actual_usage,
                finish_reason="stop",
                cached=False,
            )
                    
        except Exception as e:
            print(f"❌ Error calling Groq (streaming): {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def count_tokens(
        self,
        messages: Sequence[LLMMessage],
        *,
        tools: Sequence[Any] = [],
    ) -> int:
        """
        Count tokens in messages (approximate)
        
        Args:
            messages: List of messages
            tools: List of tools
            
        Returns:
            Approximate token count
        """
        # Simple approximation: ~4 characters per token
        total_chars = 0
        
        for msg in messages:
            if isinstance(msg, dict):
                total_chars += len(str(msg.get("content", "")))
            else:
                content = getattr(msg, "content", "")
                total_chars += len(str(content))
        
        return max(1, total_chars // 4)


# Quick test
if __name__ == "__main__":
    import asyncio
    import os
    
    async def test():
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not set")
            return
        
        print("=== Testing Groq Wrapper ===\n")
        
        client = GroqChatCompletionClient(
            api_key=api_key,
            model="llama-3.3-70b-versatile"
        )
        
        # Test message
        messages = [
            {"role": "user", "content": "What is 2+2? Reply in one sentence."}
        ]
        
        print("Sending test message...")
        result = await client.create(messages)
        
        print(f"✓ Response: {result.content}")
        print(f"✓ Usage: {result.usage}")
        print(f"✓ Finish reason: {result.finish_reason}")
        
        await client.close()
    
    asyncio.run(test())