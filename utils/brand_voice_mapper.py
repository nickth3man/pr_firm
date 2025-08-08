from typing import Dict

DEFAULT_FORBIDDENS = {
    "em_dash": True,  # Never use em dash (—)
    "rhetorical_contrast": True,  # Never use not X but Y / not just X ...
}


def brand_bible_to_voice(parsed: Dict) -> Dict:
    """Map parsed brand bible into a persona_voice structure with forbiddens."""
    persona = {
        "brand_name": parsed.get("brand_name", ""),
        "axes": {
            "formality": "medium",
            "warmth": parsed.get("tone", "neutral"),
            "vividness": "balanced",
        },
        "styles": {
            "voice": parsed.get("voice", "clear"),
        },
        "forbiddens": {**DEFAULT_FORBIDDENS},
    }
    # Merge additional forbiddens from brand bible
    for f in parsed.get("forbiddens", []) or []:
        persona["forbiddens"][f] = True
    return persona
