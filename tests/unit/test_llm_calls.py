"""
Unit tests for call_llm.py and openrouter_client.py
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from src.pr_firm.utils.llm.call_llm import (
    call_llm,
    LLMCallError,
    LLMTimeoutError,
    LLMRateLimitError
)
from src.pr_firm.utils.llm.openrouter_client import (
    OpenRouterClient,
    OpenRouterError
)

# Fixture paths
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../../data/fixtures/llm_responses')

def test_call_llm_success():
    """Test successful LLM call"""
    # Mock the OpenRouterClient to return a successful response
    mock_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Test response content"
                }
            }
        ]
    }

    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.return_value = mock_response

        # Test the call
        prompt = "Test prompt"
        result = call_llm(prompt, model="test-model", max_tokens=100)

        # Verify the result
        assert result == "Test response content"

        # Verify the client was called correctly
        mock_client.assert_called_once()
        mock_client.return_value.call_api.assert_called_once()
        called_args, called_kwargs = mock_client.return_value.call_api.call_args
        assert called_kwargs['model'] == "test-model"
        assert called_kwargs['max_tokens'] == 100
        assert prompt in called_kwargs['prompt']  # Formatted prompt contains original prompt

def test_call_llm_error():
    """Test LLM call with error response"""
    # Mock the OpenRouterClient to raise an exception
    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.side_effect = OpenRouterError("Test error")

        # Test the call
        with pytest.raises(LLMCallError) as excinfo:
            call_llm("Test prompt")

        assert "Test error" in str(excinfo.value)

def test_call_llm_timeout():
    """Test LLM call with timeout"""
    # Mock the OpenRouterClient to raise a timeout exception
    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.side_effect = TimeoutError("Request timed out")

        # Test the call
        with pytest.raises(LLMTimeoutError) as excinfo:
            call_llm("Test prompt", timeout=1)

        assert "Request timed out" in str(excinfo.value)

def test_call_llm_rate_limit():
    """Test LLM call with rate limit error"""
    # Load the error response fixture
    error_file = os.path.join(FIXTURE_DIR, 'error_response.json')
    with open(error_file, 'r') as f:
        error_response = json.load(f)

    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.return_value = error_response

        # Test the call
        with pytest.raises(LLMRateLimitError) as excinfo:
            call_llm("Test prompt")

        assert "Rate limit exceeded" in str(excinfo.value)

def test_call_llm_empty_response():
    """Test LLM call with empty response"""
    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.return_value = {"choices": []}

        # Test the call
        with pytest.raises(LLMCallError) as excinfo:
            call_llm("Test prompt")

        assert "Empty LLM response" in str(excinfo.value)

def test_call_llm_missing_content():
    """Test LLM call with missing content in response"""
    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.return_value = {
            "choices": [{"message": {}}]
        }

        # Test the call
        with pytest.raises(LLMCallError) as excinfo:
            call_llm("Test prompt")

        assert "Missing content" in str(excinfo.value)

def test_openrouter_client_initialization():
    """Test OpenRouterClient initialization"""
    # Test with API key
    client1 = OpenRouterClient(api_key="test-key")
    assert client1.api_key == "test-key"
    assert client1.base_url == "https://openrouter.ai/api/v1"

    # Test with custom base URL
    client2 = OpenRouterClient(api_key="test-key", base_url="https://custom.url")
    assert client2.base_url == "https://custom.url"

def test_openrouter_client_call_api_success():
    """Test successful API call"""
    # Load a successful response fixture
    response_file = os.path.join(FIXTURE_DIR, 'sample_response_1.json')
    with open(response_file, 'r') as f:
        mock_response = json.load(f)

    with patch('src.pr_firm.utils.llm.openrouter_client.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        # Create client and make call
        client = OpenRouterClient(api_key="test-key")
        response = client.call_api(
            prompt="Test prompt",
            model="test-model",
            max_tokens=100
        )

        # Verify response
        assert response == mock_response

        # Verify request was made correctly
        mock_post.assert_called_once()
        called_args, called_kwargs = mock_post.call_args
        assert called_kwargs['headers']['Authorization'] == "Bearer test-key"
        assert json.loads(called_kwargs['json']['prompt']) == "Test prompt"
        assert called_kwargs['json']['model'] == "test-model"
        assert called_kwargs['json']['max_tokens'] == 100

def test_openrouter_client_call_api_error():
    """Test API call with error response"""
    with patch('src.pr_firm.utils.llm.openrouter_client.requests.post') as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "error": {"message": "Test error message"}
        }

        # Create client and make call
        client = OpenRouterClient(api_key="test-key")

        with pytest.raises(OpenRouterError) as excinfo:
            client.call_api(prompt="Test prompt", model="test-model")

        assert "Test error message" in str(excinfo.value)
        assert "400" in str(excinfo.value)

def test_openrouter_client_call_api_timeout():
    """Test API call with timeout"""
    with patch('src.pr_firm.utils.llm.openrouter_client.requests.post') as mock_post:
        mock_post.side_effect = TimeoutError("Request timed out")

        # Create client and make call
        client = OpenRouterClient(api_key="test-key")

        with pytest.raises(OpenRouterError) as excinfo:
            client.call_api(prompt="Test prompt", model="test-model", timeout=1)

        assert "Request timed out" in str(excinfo.value)

def test_openrouter_client_call_api_connection_error():
    """Test API call with connection error"""
    with patch('src.pr_firm.utils.llm.openrouter_client.requests.post') as mock_post:
        mock_post.side_effect = ConnectionError("Connection failed")

        # Create client and make call
        client = OpenRouterClient(api_key="test-key")

        with pytest.raises(OpenRouterError) as excinfo:
            client.call_api(prompt="Test prompt", model="test-model")

        assert "Connection failed" in str(excinfo.value)

def test_openrouter_client_call_api_missing_api_key():
    """Test API call with missing API key"""
    # Create client without API key
    client = OpenRouterClient(api_key="")

    with pytest.raises(OpenRouterError) as excinfo:
        client.call_api(prompt="Test prompt", model="test-model")

    assert "API key is required" in str(excinfo.value)

def test_openrouter_client_call_api_with_extra_params():
    """Test API call with extra parameters"""
    # Load a successful response fixture
    response_file = os.path.join(FIXTURE_DIR, 'sample_response_2.json')
    with open(response_file, 'r') as f:
        mock_response = json.load(f)

    with patch('src.pr_firm.utils.llm.openrouter_client.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        # Create client and make call with extra params
        client = OpenRouterClient(api_key="test-key")
        response = client.call_api(
            prompt="Test prompt",
            model="test-model",
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            presence_penalty=0.1
        )

        # Verify response
        assert response == mock_response

        # Verify extra params were included
        called_args, called_kwargs = mock_post.call_args
        json_data = called_kwargs['json']
        assert json_data['temperature'] == 0.7
        assert json_data['top_p'] == 0.9
        assert json_data['presence_penalty'] == 0.1

def test_call_llm_with_brand_voice():
    """Test LLM call with brand voice mapping"""
    # Load a successful response fixture
    response_file = os.path.join(FIXTURE_DIR, 'sample_response_1.json')
    with open(response_file, 'r') as f:
        mock_response = json.load(f)

    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.return_value = mock_response

        # Test the call with brand voice
        prompt = "Test prompt"
        brand_voice = {
            "description": "Test brand voice",
            "characteristics": ["professional", "friendly"]
        }

        # Mock the brand voice mapper
        with patch('src.pr_firm.utils.llm.call_llm.map_brand_voice_to_prompt') as mock_mapper:
            mock_mapper.return_value = "Mapped brand voice prompt"

            result = call_llm(
                messages=prompt,
                model="test-model",
                max_tokens=100,
                brand_voice=brand_voice
            )

            # Verify the result
            assert result == "Test response content"

            # Verify the brand voice was mapped and included
            mock_mapper.assert_called_once_with(brand_voice)
            mock_client.return_value.call_api.assert_called_once()
            called_args, called_kwargs = mock_client.return_value.call_api.call_args
            assert "Mapped brand voice prompt" in called_args[0]
            assert prompt in called_args[0]

def test_call_llm_with_platform_rules():
    """Test LLM call with platform rules"""
    # Load a successful response fixture
    response_file = os.path.join(FIXTURE_DIR, 'sample_response_2.json')
    with open(response_file, 'r') as f:
        mock_response = json.load(f)

    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.return_value = mock_response

        # Test the call with platform rules
        prompt = "Test prompt"
        platform_rules = {
            "style_rules": ["rule1", "rule2"],
            "content_types": {"type1": {"description": "desc1"}}
        }

        # Mock the brand voice mapper for platform rules
        with patch('src.pr_firm.utils.llm.call_llm.create_brand_voice_prompt') as mock_mapper:
            mock_mapper.return_value = "Mapped platform rules prompt"

            result = call_llm(
                messages=prompt,
                model="test-model",
                max_tokens=100,
                platform_rules=platform_rules
            )

            # Verify the result
            assert result == "Here's a LinkedIn post draft following your brand guidelines:"

            # Verify the platform rules were mapped and included
            mock_mapper.assert_called_once()
            called_args, called_kwargs = mock_mapper.call_args
            assert called_args[1] == platform_rules
            mock_client.return_value.call_api.assert_called_once()
            called_args, called_kwargs = mock_client.return_value.call_api.call_args
            assert "Mapped platform rules prompt" in called_args[0]
            assert prompt in called_args[0]

def test_call_llm_with_both_brand_voice_and_platform_rules():
    """Test LLM call with both brand voice and platform rules"""
    # Load a successful response fixture
    response_file = os.path.join(FIXTURE_DIR, 'sample_response_1.json')
    with open(response_file, 'r') as f:
        mock_response = json.load(f)

    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.return_value = mock_response

        # Test the call with both brand voice and platform rules
        prompt = "Test prompt"
        brand_voice = {"description": "Test brand voice"}
        platform_rules = {"style_rules": ["rule1"]}

        # Mock both mappers
        with patch('src.pr_firm.utils.llm.call_llm.map_brand_voice_to_prompt') as mock_voice_mapper:
            with patch('src.pr_firm.utils.llm.call_llm.create_brand_voice_prompt') as mock_rules_mapper:
                mock_voice_mapper.return_value = "Mapped brand voice"
                mock_rules_mapper.return_value = "Mapped platform rules"

                result = call_llm(
                    messages=prompt,
                    model="test-model",
                    max_tokens=100,
                    brand_voice=brand_voice,
                    platform_rules=platform_rules
                )

                # Verify the result
                assert result == "Test response content"

                # Verify both mappers were called
                mock_voice_mapper.assert_called_once_with(brand_voice)
                mock_rules_mapper.assert_called_once()

                # Verify the client was called with combined prompt
                mock_client.return_value.call_api.assert_called_once()
                called_args, called_kwargs = mock_client.return_value.call_api.call_args
                assert "Mapped brand voice" in called_args[0]
                assert "Mapped platform rules" in called_args[0]
                assert prompt in called_args[0]
