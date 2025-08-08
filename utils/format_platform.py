from typing import Dict, Optional


def build_guidelines(platform: str, persona_voice: Dict, intent: str, platform_nuance: Optional[Dict] = None, reddit: Optional[Dict] = None) -> Dict:
    """Return a unified Guidelines dict for the given platform.

    Keys: limits, structure, style, hashtags, links, markdown, cta, notes
    Reddit may include subreddit_name/title and pasted rules/description notes.
    """
    platform = platform.lower()
    platform_nuance = platform_nuance or {}

    base_style = {
        "forbiddens": persona_voice.get("forbiddens", {}),
        "voice": persona_voice.get("styles", {}).get("voice", "clear"),
        "axes": persona_voice.get("axes", {}),
        "intent": intent,
    }

    if platform == "email":
        limits = {"subject": 70, "body": 500}
        structure = ["salutation", "opening", "value", "cta", "signature"]
        hashtags = []
        links = {"allowed": True, "placement": "body_or_signature"}
        markdown = False
    elif platform in ("twitter", "x"):
        limits = {"chars": 280}
        structure = ["hook", "value", "cta"]
        hashtags = {"count": 2, "placement": "end"}
        links = {"allowed": True, "placement": "end"}
        markdown = False
    elif platform == "instagram":
        limits = {"chars": 2200}
        structure = ["hook", "value", "cta"]
        hashtags = {"count": 5, "placement": "end"}
        links = {"allowed": False, "placement": None}
        markdown = False
    elif platform == "linkedin":
        limits = {"chars": 3000}
        structure = ["hook", "value", "cta"]
        hashtags = {"count": 3, "placement": "end"}
        links = {"allowed": True, "placement": "end"}
        markdown = False
    elif platform == "blog":
        limits = {"words": 1200}
        structure = ["title", "intro", "sections", "conclusion", "cta"]
        hashtags = []
        links = {"allowed": True, "placement": "throughout"}
        markdown = True
    elif platform == "reddit":
        limits = {"chars": 40000}
        structure = ["title", "body"]
        hashtags = []
        links = {"allowed": True, "placement": "body"}
        markdown = True
    else:
        # Fallback generic
        limits = {"chars": 1000}
        structure = ["hook", "value", "cta"]
        hashtags = []
        links = {"allowed": True, "placement": "end"}
        markdown = False

    guidelines = {
        "limits": limits,
        "structure": structure,
        "style": base_style,
        "hashtags": hashtags,
        "links": links,
        "markdown": markdown,
        "cta": platform_nuance.get("cta", ""),
        "notes": platform_nuance.get("notes", ""),
    }

    if platform == "reddit" and reddit:
        guidelines["reddit_info"] = {
            "subreddit": reddit.get("name"),
            "rules": reddit.get("rules"),
            "description": reddit.get("description"),
        }

    return guidelines
