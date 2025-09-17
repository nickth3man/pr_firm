"""
Unit tests for brand_bible_parser.py
"""

import pytest
import os
from src.pr_firm.utils.helpers.brand_bible_parser import (
    parse_brand_bible,
    extract_platform_rules,
    validate_xml_structure,
    BrandBibleParseError
)
from src.pr_firm.utils.content.brand_voice_mapper import map_brand_voice_to_prompt

# Fixture paths
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../../data/fixtures/brand_bible_samples')

def test_parse_valid_brand_bible():
    """Test parsing a valid brand bible XML file"""
    file_path = os.path.join(FIXTURE_DIR, 'valid_brand_bible.xml')

    result, missing = parse_brand_bible(file_path)

    # Verify basic structure
    assert 'metadata' in result
    assert 'global_style' in result
    assert 'platforms' in result
    assert 'style_guide' in result
    assert 'brand_voice' in result

    # Verify metadata
    assert result['metadata']['version'] == '1.2'
    assert result['metadata']['last_updated'] == '2023-11-15'
    assert result['metadata']['company_name'] == 'TechCorp'

    # Verify global style (empty as per XML structure)
    assert result['global_style'] == {}

    # Verify platforms
    assert len(result['platforms']) == 3
    assert 'twitter' in result['platforms']
    assert 'linkedin' in result['platforms']
    assert 'facebook' in result['platforms']

    # Verify twitter platform specifics
    twitter = result['platforms']['twitter']
    assert 'concise' in twitter['characteristics']
    assert 'engaging' in twitter['characteristics']
    assert 'hashtag-friendly' in twitter['characteristics']
    assert len(twitter['style_rules']) == 4
    assert len(twitter['content_types']) == 2  # product_announcement and thought_leadership

def test_parse_minimal_brand_bible():
    """Test parsing a minimal brand bible XML file"""
    file_path = os.path.join(FIXTURE_DIR, 'minimal_brand_bible.xml')

    result, _ = parse_brand_bible(file_path)

    # Verify basic structure exists even with minimal content
    assert 'metadata' in result
    assert 'global_style' in result
    assert 'platforms' in result

    # Verify minimal content
    assert result['metadata']['version'] == '1.0'
    assert len(result['platforms']) == 1
    assert 'twitter' in result['platforms']

def test_parse_empty_brand_bible():
    """Test parsing an empty brand bible XML file"""
    file_path = os.path.join(FIXTURE_DIR, 'empty_brand_bible.xml')

    result, _ = parse_brand_bible(file_path)

    # Should return empty structure
    assert result == {
        'metadata': {},
        'global_style': {},
        'platforms': {},
        'style_guide': {},
        'brand_voice': {}
    }

def test_parse_malformed_brand_bible():
    """Test parsing a malformed brand bible XML file"""
    file_path = os.path.join(FIXTURE_DIR, 'malformed_brand_bible.xml')

    with pytest.raises(BrandBibleParseError) as excinfo:
        parse_brand_bible(file_path)

    assert "XML parsing error" in str(excinfo.value)

def test_extract_platform_rules():
    """Test extracting rules for a specific platform"""
    file_path = os.path.join(FIXTURE_DIR, 'valid_brand_bible.xml')

    # Extract twitter rules
    twitter_rules = extract_platform_rules(file_path, 'twitter')

    assert 'characteristics' in twitter_rules
    assert 'style_rules' in twitter_rules
    assert 'content_types' in twitter_rules

    # Verify specific twitter characteristics
    assert twitter_rules['characteristics']['max_length'] == 280
    assert twitter_rules['characteristics']['hashtag_limit'] == 2

    # Verify style rules
    assert len(twitter_rules['style_rules']) == 4
    assert "Use 280 characters or less" in twitter_rules['style_rules']
    assert "Include relevant hashtags" in twitter_rules['style_rules']

    # Verify content types
    assert 'product_announcement' in twitter_rules['content_types']
    assert 'thought_leadership' in twitter_rules['content_types']

def test_extract_nonexistent_platform():
    """Test extracting rules for a non-existent platform"""
    file_path = os.path.join(FIXTURE_DIR, 'valid_brand_bible.xml')

    with pytest.raises(ValueError) as excinfo:
        extract_platform_rules(file_path, 'nonexistent')

    assert "Platform 'nonexistent' not found" in str(excinfo.value)

def test_validate_xml_structure_valid():
    """Test validating a valid XML structure"""
    file_path = os.path.join(FIXTURE_DIR, 'valid_brand_bible.xml')

    is_valid = validate_xml_structure(file_path)
    assert is_valid is True

def test_validate_xml_structure_invalid():
    """Test validating an invalid XML structure"""
    file_path = os.path.join(FIXTURE_DIR, 'malformed_brand_bible.xml')

    is_valid = validate_xml_structure(file_path)
    assert is_valid is False

def test_file_not_found():
    """Test handling of non-existent file"""
    non_existent_path = os.path.join(FIXTURE_DIR, 'nonexistent.xml')

    with pytest.raises(FileNotFoundError):
        parse_brand_bible(non_existent_path)

def test_brand_voice_mapping():
    """Test mapping brand voice to prompt"""
    file_path = os.path.join(FIXTURE_DIR, 'valid_brand_bible.xml')
    result, _ = parse_brand_bible(file_path)

    prompt = map_brand_voice_to_prompt(result['brand_voice'])

    # Verify key elements are in the prompt
    assert "knowledgeable" in prompt
    assert "helpful" in prompt
    assert "slightly humorous" in prompt
    assert "Professional yet approachable" in prompt

    # Note: No avoided terms are defined in the test XML, so we can't test this

def test_platform_specific_content_types():
    """Test extracting platform-specific content types"""
    file_path = os.path.join(FIXTURE_DIR, 'valid_brand_bible.xml')

    result, _ = parse_brand_bible(file_path)

    # Test twitter content types
    twitter_content = result['platforms']['twitter']['content_types']
    assert 'product_announcement' in twitter_content
    assert 'thought_leadership' in twitter_content

    # Verify product announcement content structure
    product_announcement = twitter_content['product_announcement']
    assert 'description' in product_announcement
    assert 'examples' in product_announcement

    # Test linkedin content types
    linkedin_content = result['platforms']['linkedin']['content_types']
    assert 'company_update' in linkedin_content
    assert 'industry_insight' in linkedin_content

def test_style_guide_extraction():
    """Test extracting style guide rules"""
    file_path = os.path.join(FIXTURE_DIR, 'valid_brand_bible.xml')

    result, _ = parse_brand_bible(file_path)
    style_guide = result['style_guide']

    # Test grammar rules
    assert len(style_guide['grammar']) == 4
    assert "Avoid passive voice" in style_guide['grammar']
    assert "Use Oxford comma" in style_guide['grammar']

    # Test formatting rules
    assert len(style_guide['formatting']) == 4
    assert "One space after periods" in style_guide['formatting']
    assert "No multiple spaces between words" in style_guide['formatting']

    # Test word choices
    assert 'word_choices' in style_guide
    assert 'preferred' in style_guide['word_choices']
    assert 'avoid' in style_guide['word_choices']
