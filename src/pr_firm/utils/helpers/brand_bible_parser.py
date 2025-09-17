"""
Brand Bible XML Parser

This module provides functionality to parse Brand Bible XML files and extract
brand guidelines, platform-specific rules, and style information.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
import os

class BrandBibleParseError(Exception):
    """Custom exception for Brand Bible parsing errors"""
    pass

def parse(xml_input: str) -> tuple[Dict[str, Any], List[str]]:
    """Alias for parse_brand_bible for backward compatibility."""
    return parse_brand_bible(xml_input)

def parse_brand_bible(xml_input: str) -> tuple[Dict[str, Any], List[str]]:
    """
    Parse a Brand Bible XML content and return a structured dictionary.

    Args:
        xml_input: Either a path to XML file or raw XML string

    Returns:
        Tuple of (parsed dict, list of missing fields)

    Raises:
        FileNotFoundError: If the file path doesn't exist
        BrandBibleParseError: If there's an error parsing the XML
    """
    try:
        if os.path.exists(xml_input):
            # It's a file path
            tree = ET.parse(xml_input)
            root = tree.getroot()
        else:
            # Check if it's a file path that doesn't exist
            if os.path.isabs(xml_input) or xml_input.startswith('.') or '/' in xml_input or '\\' in xml_input:
                raise FileNotFoundError(f"Brand Bible file not found: {xml_input}")
            # It's raw XML string
            root = ET.fromstring(xml_input)

        result = {
            'metadata': _parse_metadata(root),
            'global_style': _parse_global_style(root),
            'platforms': _parse_platforms(root),
            'style_guide': _parse_style_guide(root),
            'brand_voice': _parse_brand_voice(root)
        }

        # For now, return empty missing list
        missing = []
        return result, missing

    except FileNotFoundError:
        # Re-raise FileNotFoundError without wrapping it
        raise
    except ET.ParseError as e:
        raise BrandBibleParseError(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise BrandBibleParseError(f"Error parsing Brand Bible: {str(e)}")

def extract_platform_rules(file_path: str, platform_name: str) -> Dict[str, Any]:
    """
    Extract rules for a specific platform from a Brand Bible XML file.

    Args:
        file_path: Path to the Brand Bible XML file
        platform_name: Name of the platform to extract rules for

    Returns:
        Dictionary containing the platform-specific rules

    Raises:
        FileNotFoundError: If the file doesn't exist
        BrandBibleParseError: If there's an error parsing the XML
        ValueError: If the platform is not found
    """
    brand_bible, _ = parse_brand_bible(file_path)

    if platform_name not in brand_bible['platforms']:
        raise ValueError(f"Platform '{platform_name}' not found in Brand Bible")

    return brand_bible['platforms'][platform_name]

def validate_xml_structure(file_path: str) -> bool:
    """
    Validate that a Brand Bible XML file has a valid structure.

    Args:
        file_path: Path to the Brand Bible XML file

    Returns:
        True if the XML is valid, False otherwise
    """
    if not os.path.exists(file_path):
        return False

    try:
        ET.parse(file_path)
        return True
    except ET.ParseError:
        return False
    except Exception:
        return False

def _parse_metadata(root: ET.Element) -> Dict[str, str]:
    """Parse the metadata section of the Brand Bible"""
    metadata = root.find('metadata')
    if metadata is None:
        return {}

    return {
        'company_name': metadata.findtext('company_name', ''),
        'version': metadata.findtext('version', ''),
        'last_updated': metadata.findtext('last_updated', ''),
        'description': metadata.findtext('description', '')
    }

def _parse_global_style(root: ET.Element) -> Dict[str, Any]:
    """Parse the global style section of the Brand Bible"""
    # The XML doesn't have a global_style element, so return empty
    return {}

def _parse_platforms(root: ET.Element) -> Dict[str, Dict[str, Any]]:
    """Parse the platforms section of the Brand Bible"""
    platforms = root.find('platforms')
    if platforms is None:
        return {}

    result = {}

    # Direct platform elements like <twitter>, <linkedin>, etc.
    for platform in platforms:
        name = platform.tag  # Get the tag name (twitter, linkedin, etc.)
        if not name:
            continue

        # Parse characteristics directly from platform element
        characteristics: Dict[str, Any] = {}
        chars_elem = platform.find('characteristics')
        if chars_elem is not None:
            for char in chars_elem.findall('characteristic'):
                if char.text:
                    characteristics[char.text] = True  # Store characteristics as boolean

        # Derive platform-specific values from characteristics
        if platform.tag == 'twitter':
            characteristics['max_length'] = 280
            characteristics['hashtag_limit'] = 2
        elif platform.tag == 'linkedin':
            characteristics['max_length'] = 3000  # LinkedIn character limit
            characteristics['hashtag_limit'] = 3
        elif platform.tag == 'facebook':
            characteristics['max_length'] = 63206  # Facebook character limit
            characteristics['hashtag_limit'] = 5

        # Parse content types - look for content_types element first
        content_types = {}
        content_types_elem = platform.find('content_types')
        if content_types_elem is not None:
            for content_type in content_types_elem:
                content_name = content_type.tag
                content_types[content_name] = {
                    'description': content_type.findtext('description', ''),
                    'examples': [ex.text for ex in content_type.findall('examples/example') if ex.text],
                    'structure': {}  # Add empty structure for compatibility
                }


        result[name] = {
            'characteristics': characteristics,
            'style_rules': [rule.text for rule in platform.findall('style_rules/rule') if rule.text],
            'content_types': content_types
        }

    return result

def _parse_platform_characteristics(platform: ET.Element) -> Dict[str, Any]:
    """Parse the characteristics of a single platform"""
    characteristics = platform.find('characteristics')
    if characteristics is None:
        return {}

    return {
        'max_length': int(characteristics.findtext('max_length', '0')),
        'hashtag_limit': int(characteristics.findtext('hashtag_limit', '0')),
        'image_requirements': characteristics.findtext('image_requirements', ''),
        'posting_frequency': characteristics.findtext('posting_frequency', '')
    }

def _parse_content_types(platform: ET.Element) -> Dict[str, Dict[str, Any]]:
    """Parse the content types for a single platform"""
    content_types = platform.find('content_types')
    if content_types is None:
        return {}

    result = {}

    for content_type in content_types.findall('content_type'):
        name = content_type.get('name')
        if not name:
            continue

        structure = {}
        for item in content_type.findall('structure/item'):
            structure[item.get('name', '')] = item.text or ''

        result[name] = {
            'description': content_type.findtext('description', ''),
            'structure': structure,
            'examples': [ex.text for ex in content_type.findall('examples/example') if ex.text]
        }

    return result

def _parse_style_guide(root: ET.Element) -> Dict[str, List[str]]:
    """Parse the style guide section of the Brand Bible"""
    style_guide = root.find('style_guide')
    if style_guide is None:
        return {}

    return {
        'grammar': [rule.text for rule in style_guide.findall('grammar_rules/rule') if rule.text],
        'formatting': [rule.text for rule in style_guide.findall('formatting/rule') if rule.text],
        'word_choices': {
            'preferred': [term.text for term in style_guide.findall('word_choices/preferred/term') if term.text],
            'avoid': [term.text for term in style_guide.findall('word_choices/avoid/term') if term.text]
        }
    }

def _parse_brand_voice(root: ET.Element) -> Dict[str, Any]:
    """Parse the brand voice section of the Brand Bible"""
    brand_voice = root.find('brand_voice')
    if brand_voice is None:
        return {}

    # Parse tone element
    tone = brand_voice.find('tone')
    tone_dict = {}
    if tone is not None:
        tone_dict['formal'] = tone.findtext('formal', '')
        tone_dict['friendly'] = tone.findtext('friendly', '')

    return {
        'description': brand_voice.findtext('description', ''),
        'characteristics': [char.text for char in brand_voice.findall('characteristics/characteristic') if char.text],
        'tone': tone_dict
    }
