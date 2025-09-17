"""
Integration tests for the brand content generation pipeline
"""

import pytest
import os
from unittest.mock import patch
from src.pr_firm.utils.helpers.brand_bible_parser import parse_brand_bible
from src.pr_firm.utils.helpers.check_style_violations import check_style_violations
from src.pr_firm.utils.llm.call_llm import call_llm
from src.pr_firm.utils.content.brand_voice_mapper import map_brand_voice_to_prompt

# Fixture paths
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../../data/fixtures')

def test_brand_pipeline_integration():
    """Test the complete brand content generation pipeline"""
    # 1. Parse brand bible
    brand_bible_path = os.path.join(FIXTURE_DIR, 'brand_bible_samples/valid_brand_bible.xml')
    brand_bible, _ = parse_brand_bible(brand_bible_path)

    # Verify brand bible was parsed correctly
    assert 'metadata' in brand_bible
    assert 'platforms' in brand_bible
    assert 'twitter' in brand_bible['platforms']

    # 2. Extract platform rules
    twitter_rules = brand_bible['platforms']['twitter']

    # Verify platform rules
    assert 'characteristics' in twitter_rules
    assert 'style_rules' in twitter_rules
    assert 'content_types' in twitter_rules

    # 3. Map brand voice to prompt
    brand_voice = brand_bible['brand_voice']
    voice_prompt = map_brand_voice_to_prompt(brand_voice)

    # Verify brand voice mapping
    assert "Brand Voice Description:" in voice_prompt
    assert "Characteristics:" in voice_prompt
    assert "knowledgeable, helpful, slightly humorous" in voice_prompt

    # 4. Mock LLM call to avoid actual API calls
    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        # Mock successful response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Generated content following brand guidelines"
                    }
                }
            ]
        }
        mock_client.return_value.call_api.return_value = mock_response

        # Call LLM with brand voice and platform rules
        prompt = "Create a Twitter post about our new product"
        result = call_llm(
            messages=prompt,
            model="test-model",
            brand_voice=brand_voice,
            platform_rules=twitter_rules
        )

        # Verify LLM was called with correct parameters
        mock_client.assert_called_once()
        mock_client.return_value.call_api.assert_called_once()

        # Verify result
        assert result == "Generated content following brand guidelines"

def test_style_violation_detection():
    """Test style violation detection in generated content"""
    # 1. Load sample text with violations
    violations_file = os.path.join(FIXTURE_DIR, 'style_violations/invalid_text.txt')
    with open(violations_file, 'r') as f:
        text = f.read()

    # 2. Check for style violations
    violations = check_style_violations(text)

    # Verify violations were found
    assert len(violations) > 0

    # Check for specific violation types
    violation_types = [v.violation_type for v in violations]
    assert 'passive_voice' in violation_types
    assert 'long_sentence' in violation_types
    assert 'double_space' in violation_types

    # Verify violation details
    for violation in violations:
        assert violation.violation_type
        assert violation.message
        assert violation.line_number > 0
        assert violation.context

def test_brand_consistency_across_platforms():
    """Test that brand voice is consistently applied across platforms"""
    # 1. Parse brand bible
    brand_bible_path = os.path.join(FIXTURE_DIR, 'brand_bible_samples/valid_brand_bible.xml')
    brand_bible, _ = parse_brand_bible(brand_bible_path)

    # 2. Get brand voice
    brand_voice = brand_bible['brand_voice']

    # 3. Test mapping for different platforms
    platforms = ['twitter', 'linkedin', 'facebook']
    voice_prompts = {}

    for platform in platforms:
        if platform in brand_bible['platforms']:
            platform_rules = brand_bible['platforms'][platform]
            voice_prompts[platform] = map_brand_voice_to_prompt(brand_voice)

    # Verify all platforms get the same brand voice mapping
    first_prompt = next(iter(voice_prompts.values()))
    for platform, prompt in voice_prompts.items():
        assert prompt == first_prompt, f"Brand voice inconsistent for {platform}"

def test_error_handling_in_pipeline():
    """Test error handling in the pipeline"""
    # 1. Test parsing invalid XML
    invalid_xml_path = os.path.join(FIXTURE_DIR, 'brand_bible_samples/malformed_brand_bible.xml')

    with pytest.raises(Exception) as excinfo:
        parse_brand_bible(invalid_xml_path)

    assert "XML parsing error" in str(excinfo.value)

    # 2. Test LLM call with error
    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        mock_client.return_value.call_api.side_effect = Exception("API error")

        with pytest.raises(Exception) as excinfo:
            call_llm("Test prompt")

        assert "API error" in str(excinfo.value)

def test_platform_specific_content_generation():
    """Test generation of platform-specific content"""
    # 1. Parse brand bible
    brand_bible_path = os.path.join(FIXTURE_DIR, 'brand_bible_samples/valid_brand_bible.xml')
    brand_bible, _ = parse_brand_bible(brand_bible_path)

    # 2. Get platform rules
    twitter_rules = brand_bible['platforms']['twitter']
    linkedin_rules = brand_bible['platforms']['linkedin']

    # 3. Mock LLM calls
    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        # Mock different responses for different platforms
        mock_client.return_value.call_api.side_effect = [
            {"choices": [{"message": {"content": "Twitter content with hashtags"}}]},
            {"choices": [{"message": {"content": "LinkedIn thought leadership post"}}]}
        ]

        # Generate content for Twitter
        twitter_prompt = "Create a Twitter post about our product"
        twitter_content = call_llm(
            messages=twitter_prompt,
            model="test-model",
            platform_rules=twitter_rules
        )

        # Generate content for LinkedIn
        linkedin_prompt = "Create a LinkedIn post about our product"
        linkedin_content = call_llm(
            messages=linkedin_prompt,
            model="test-model",
            platform_rules=linkedin_rules
        )

        # Verify different content was generated
        assert twitter_content != linkedin_content
        assert "Twitter content" in twitter_content
        assert "LinkedIn thought leadership" in linkedin_content

        # Verify LLM was called with platform-specific rules
        assert mock_client.return_value.call_api.call_count == 2

def test_style_violation_correction():
    """Test style violation detection and correction"""
    # 1. Load text with violations
    violations_file = os.path.join(FIXTURE_DIR, 'style_violations/invalid_text.txt')
    with open(violations_file, 'r') as f:
        original_text = f.read()

    # 2. Detect violations
    violations = check_style_violations(original_text)
    assert len(violations) > 0

    # 3. Mock LLM to correct violations
    with patch('src.pr_firm.utils.llm.call_llm.OpenRouterClient') as mock_client:
        # Mock corrected response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Corrected text without style violations."
                    }
                }
            ]
        }
        mock_client.return_value.call_api.return_value = mock_response

        # Create prompt to fix violations
        violation_messages = "\n".join([
            f"- {v.violation_type}: {v.message} (Line {v.line_number})"
            for v in violations
        ])

        correction_prompt = f"""
        Original text: {original_text}

        Style violations detected:
        {violation_messages}

        Please rewrite the text to fix all style violations while maintaining the original meaning.
        """

        # Call LLM to correct violations
        corrected_text = call_llm(
            messages=correction_prompt,
            model="test-model"
        )

        # Verify correction
        assert corrected_text == "Corrected text without style violations."

        # Verify LLM was called with violation information
        mock_client.return_value.call_api.assert_called_once()
        called_args, _ = mock_client.return_value.call_api.call_args
        assert "Style violations detected:" in called_args[0]