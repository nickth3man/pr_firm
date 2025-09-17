"""
LLM Call Utilities

This module provides functionality to call LLM APIs and handle responses.
"""

import os
from typing import Dict, Any, List, Optional, Union
from .openrouter_client import OpenRouterClient, OpenRouterError
from ..content.brand_voice_mapper import map_brand_voice_to_prompt, create_brand_voice_prompt

class LLMCallError(Exception):
    """Base exception for LLM call errors"""
    pass

class LLMTimeoutError(LLMCallError):
    """Exception for LLM call timeouts"""
    pass

class LLMRateLimitError(LLMCallError):
    """Exception for LLM rate limit errors"""
    pass

def call_llm(
    messages: Union[str, List[Dict[str, str]]],
    model: str = "openrouter/mistralai/mistral-7b-instruct",
    max_tokens: int = 4096,
    temperature: float = 0.7,
    top_p: float = 1.0,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    timeout: int = 30,
    brand_voice: Optional[Dict[str, Any]] = None,
    platform_rules: Optional[Dict[str, Any]] = None
) -> str:
    """
    Call an LLM API with the given prompt and parameters.

    Args:
        messages: The prompt message(s) to send to the LLM
        model: The model to use
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature
        top_p: Nucleus sampling parameter
        presence_penalty: Presence penalty parameter
        frequency_penalty: Frequency penalty parameter
        timeout: Request timeout in seconds
        brand_voice: Optional brand voice characteristics to include in the prompt
        platform_rules: Optional platform-specific rules to include in the prompt

    Returns:
        The LLM's response text

    Raises:
        LLMCallError: If there's an error calling the LLM
        LLMTimeoutError: If the request times out
        LLMRateLimitError: If rate limits are exceeded
    """
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise LLMCallError("OPENROUTER_API_KEY environment variable not set")

    # Convert string message to list format if needed
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    # Create client
    client = OpenRouterClient(api_key=api_key)

    # Prepare the prompt with brand voice and platform rules if provided
    prompt = _prepare_prompt(messages, brand_voice, platform_rules)

    try:
        # Call the API
        response = client.call_api(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            timeout=timeout
        )

        # Process the response
        return _process_response(response)

    except TimeoutError as e:
        raise LLMTimeoutError(f"LLM call timed out: {str(e)}")
    except OpenRouterError as e:
        if "rate limit" in str(e).lower():
            raise LLMRateLimitError(f"LLM rate limit exceeded: {str(e)}")
        raise LLMCallError(f"LLM call failed: {str(e)}")

def _prepare_prompt(
    messages: List[Dict[str, str]],
    brand_voice: Optional[Dict[str, Any]] = None,
    platform_rules: Optional[Dict[str, Any]] = None
) -> str:
    """
    Prepare the prompt by combining messages with brand voice and platform rules.

    Args:
        messages: The original messages
        brand_voice: Optional brand voice characteristics
        platform_rules: Optional platform-specific rules

    Returns:
        The prepared prompt string
    """
    # Start with the original messages
    prompt_parts = []

    # Add system message with brand voice if provided
    if brand_voice:
        voice_prompt = map_brand_voice_to_prompt(brand_voice)
        prompt_parts.append({
            "role": "system",
            "content": f"Brand Voice Guidelines:\n{voice_prompt}"
        })

    # Add platform rules if provided
    if platform_rules:
        if brand_voice:
            # Combine brand voice and platform rules
            combined_prompt = create_brand_voice_prompt(brand_voice, platform_rules)
            prompt_parts.append({
                "role": "system",
                "content": f"Brand Voice and Platform Rules:\n{combined_prompt}"
            })
        else:
            # Just add platform rules
            rules_prompt = "\n".join([
                f"Platform: {platform_rules.get('platform_name', 'unknown')}",
                "Style Rules:",
                *platform_rules.get('style_rules', []),
                "Content Types:",
                *[f"- {content_type}: {details.get('description', '')}"
                  for content_type, details in platform_rules.get('content_types', {}).items()]
            ])
            prompt_parts.append({
                "role": "system",
                "content": f"Platform Rules:\n{rules_prompt}"
            })

    # Add the original messages
    prompt_parts.extend(messages)

    # Convert to string format expected by the client
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in prompt_parts])

def _process_response(response: Dict[str, Any]) -> str:
    """
    Process the LLM response and extract the content.

    Args:
        response: The raw response from the LLM API

    Returns:
        The extracted content text

    Raises:
        LLMCallError: If the response is invalid or empty
    """
    if not response or 'choices' not in response:
        raise LLMCallError("Invalid LLM response format")

    choices = response['choices']
    if not choices:
        raise LLMCallError("Empty LLM response")

    first_choice = choices[0]
    if 'message' not in first_choice or 'content' not in first_choice['message']:
        raise LLMCallError("Missing content in LLM response")

    return first_choice['message']['content']
