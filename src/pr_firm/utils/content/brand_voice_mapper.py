"""
Brand Voice Mapper

This module provides functionality to map brand voice characteristics to
LLM prompt instructions for consistent content generation.
"""

from typing import Dict, Any, List

def brand_bible_to_voice(parsed_brand_bible: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert parsed brand bible to brand voice persona format.

    Args:
        parsed_brand_bible: Parsed brand bible dictionary

    Returns:
        Brand voice persona dictionary
    """
    brand_voice = parsed_brand_bible.get('brand_voice', {})

    # Transform to persona format expected by the nodes
    persona = {
        'description': brand_voice.get('description', ''),
        'characteristics': brand_voice.get('characteristics', []),
        'avoid': brand_voice.get('avoid', []),
        'tone_examples': brand_voice.get('tone_examples', {}),
        'styles': {'voice': 'clear'},  # default
        'axes': {'formality': 'medium', 'vividness': 'balanced'},  # defaults
        'forbiddens': {'em_dash': True, 'rhetorical_contrast': True}  # brand bans
    }

    return persona

def map_brand_voice_to_prompt(brand_voice: Dict[str, Any]) -> str:
    """
    Convert brand voice characteristics into an LLM prompt instruction.

    Args:
        brand_voice: Dictionary containing brand voice characteristics

    Returns:
        String containing the prompt instruction
    """
    if not brand_voice:
        return ""

    # Start with the basic description
    prompt_parts = [f"Brand Voice Description: {brand_voice.get('description', '')}"]

    # Add characteristics
    characteristics = brand_voice.get('characteristics', [])
    if characteristics:
        prompt_parts.append("Characteristics:")
        for char in characteristics:
            prompt_parts.append(f"- {char}")

    # Add tone examples
    tone_examples = brand_voice.get('tone_examples', {})
    if tone_examples:
        prompt_parts.append("Tone Examples:")
        for tone_type, example in tone_examples.items():
            if example:
                prompt_parts.append(f"{tone_type.capitalize()}: {example}")

    # Add things to avoid
    avoid = brand_voice.get('avoid', [])
    if avoid:
        prompt_parts.append("Avoid:")
        for item in avoid:
            prompt_parts.append(f"- {item}")

    # Combine all parts into a single prompt
    return "\n".join(prompt_parts)

def create_brand_voice_prompt(brand_voice: Dict[str, Any], platform_rules: Dict[str, Any]) -> str:
    """
    Create a comprehensive prompt combining brand voice and platform-specific rules.

    Args:
        brand_voice: Dictionary containing brand voice characteristics
        platform_rules: Dictionary containing platform-specific rules

    Returns:
        String containing the complete prompt
    """
    voice_prompt = map_brand_voice_to_prompt(brand_voice)

    # Add platform-specific rules
    platform_prompt = []

    # Add style rules
    style_rules = platform_rules.get('style_rules', [])
    if style_rules:
        platform_prompt.append("Platform Style Rules:")
        for rule in style_rules:
            platform_prompt.append(f"- {rule}")

    # Add content type information
    content_types = platform_rules.get('content_types', {})
    if content_types:
        platform_prompt.append("Content Types:")
        for content_type, details in content_types.items():
            platform_prompt.append(f"{content_type.capitalize()}:")
            platform_prompt.append(f"  Description: {details.get('description', '')}")

            structure = details.get('structure', {})
            if structure:
                platform_prompt.append("  Structure:")
                for item_name, item_desc in structure.items():
                    platform_prompt.append(f"    {item_name}: {item_desc}")

            examples = details.get('examples', [])
            if examples:
                platform_prompt.append("  Examples:")
                for example in examples:
                    platform_prompt.append(f"    - {example}")

    # Combine voice and platform prompts
    combined_prompt = []

    if voice_prompt:
        combined_prompt.append(voice_prompt)

    if platform_prompt:
        combined_prompt.append("\n".join(platform_prompt))

    return "\n\n".join(combined_prompt)
