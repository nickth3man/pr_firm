"""
OpenRouter API Client

This module provides a client for interacting with the OpenRouter API.
"""

import requests
import json
from typing import Dict, Any, Optional

class OpenRouterError(Exception):
    """Custom exception for OpenRouter API errors"""
    pass

class OpenRouterClient:
    """
    Client for interacting with the OpenRouter API.
    """

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key
            base_url: Base URL for the API (default: OpenRouter production)
        """
        if not api_key:
            raise OpenRouterError("API key is required")

        self.api_key = api_key
        self.base_url = base_url

    def call_api(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Call the OpenRouter API with the given parameters.

        Args:
            prompt: The prompt to send to the model
            model: The model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            presence_penalty: Presence penalty parameter
            frequency_penalty: Frequency penalty parameter
            timeout: Request timeout in seconds

        Returns:
            The API response as a dictionary

        Raises:
            OpenRouterError: If there's an error calling the API
        """
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=timeout
            )

            # Check for errors
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_details = response.json()
                    if 'error' in error_details:
                        error_msg += f": {error_details['error'].get('message', 'Unknown error')}"
                except ValueError:
                    error_msg += f": {response.text}"

                raise OpenRouterError(error_msg)

            return response.json()

        except requests.exceptions.Timeout:
            raise OpenRouterError(f"Request timed out after {timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise OpenRouterError("Connection error")
        except requests.exceptions.RequestException as e:
            raise OpenRouterError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise OpenRouterError("Invalid JSON response from API")
