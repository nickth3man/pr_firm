import os
from typing import List, Dict, Optional

try:
    from openai import OpenAI
except ImportError:  # Fallback for environments with legacy openai package
    OpenAI = None  # type: ignore


def get_client() -> "OpenAI":
    """Return an OpenAI-compatible client configured for OpenRouter.

    Requires environment variable OPENROUTER_API_KEY.
    Optional: OPENROUTER_BASE_URL (default: https://openrouter.ai/api/v1)
    """
    if OpenAI is None:
        raise RuntimeError("openai package is required. Please add 'openai' to requirements.txt and install it.")

    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in the environment.")

    return OpenAI(base_url=base_url, api_key=api_key)


def chat(messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.7) -> str:
    """Send a chat completion to OpenRouter and return the string response.

    - messages: list of {"role": "user|system|assistant", "content": str}
    - model: override model; default uses OPENROUTER_MODEL or a sensible default
    - temperature: decoding temperature
    """
    client = get_client()
    resolved_model = model or os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    r = client.chat.completions.create(
        model=resolved_model,
        messages=messages,
        temperature=temperature,
    )
    # OpenRouter proxies OpenAI-compatible schema
    return r.choices[0].message.content  # type: ignore[attr-defined]
