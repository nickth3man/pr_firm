from typing import Dict, Optional, Any


def build_guidelines(platform: str, persona_voice: Dict, intent: str, platform_nuance: Optional[Dict] = None, reddit: Optional[Dict] = None) -> Dict:
    """Return a unified Guidelines dict for the given platform.

    Keys: limits, structure, style, hashtags, links, markdown, cta, notes
    Reddit may include subreddit_name/title and pasted rules/description notes.
    """
    platform = platform.lower()
    platform_nuance = platform_nuance or {}

    base_style: Dict[str, Any] = {
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
        limits = {"chars": 2200, "reveal_cutoff": 125}
        structure = ["hook", "value", "cta"]
        hashtags = {"count": 5, "placement": "end"}
        links = {"allowed": False, "placement": None}
        markdown = False
    elif platform == "linkedin":
        limits = {"chars": 3000, "reveal_cutoff": 210}
        structure = ["hook", "value", "cta"]
        hashtags = {"count": 3, "placement": "end"}
        links = {"allowed": True, "placement": "end"}
        markdown = False
    elif platform == "blog":
        limits = {"words": 1200, "approx_chars": 1200 * 5}
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

    # Default per-section budgets: prefer explicit section_budgets, otherwise estimate from chars
    section_budgets = platform_nuance.get("section_budgets") if isinstance(platform_nuance.get("section_budgets"), dict) else None

    guidelines: Dict[str, Any] = {
        "limits": limits,
        "structure": structure,
        "style": base_style,
        "hashtags": hashtags,
        "links": links,
        "markdown": markdown,
        "cta": platform_nuance.get("cta", ""),
        "notes": platform_nuance.get("notes", []) if isinstance(platform_nuance.get("notes"), list) else ([platform_nuance.get("notes")] if platform_nuance.get("notes") else []),
        "section_budgets": section_budgets or {},
    }

    # Apply platform nuance overrides
    if isinstance(hashtags, dict) and isinstance(platform_nuance.get("hashtag_count_range"), (list, tuple)):
        rng = platform_nuance["hashtag_count_range"]
        if len(rng) == 2:
            # Use the upper bound as target count
            guidelines["hashtags"]["count"] = rng[1]
    if platform == "reddit" and isinstance(platform_nuance.get("tl_dr_required"), bool):
        if platform_nuance["tl_dr_required"] and not any("TL;DR" in n for n in guidelines["notes"]):
            guidelines["notes"].append("TL;DR recommended at end.")
    if platform == "instagram" and platform_nuance.get("line_breaks"):
        guidelines.setdefault("style", {}).setdefault("formatting", {})
        guidelines["style"]["formatting"]["line_breaks"] = platform_nuance["line_breaks"]
    if platform == "instagram" and platform_nuance.get("emoji_freq"):
        guidelines.setdefault("style", {}).setdefault("formatting", {})
        guidelines["style"]["formatting"]["emoji_freq"] = platform_nuance["emoji_freq"]

    if platform == "reddit" and reddit:
        guidelines["reddit_info"] = {
            "subreddit": reddit.get("name"),
            "rules": reddit.get("rules_text") or reddit.get("rules"),
            "description": reddit.get("description_text") or reddit.get("description"),
        }
        # Ensure subreddit name normalized hint present
        if guidelines["reddit_info"].get("subreddit"):
            guidelines["notes"].append(f"Posting to r/{guidelines['reddit_info']['subreddit']}")

    return guidelines
