"""
Shared store initialization and management for PR Firm.
"""
"""Shared store initialization and management for PR Firm."""

from typing import Dict, Any

from pr_firm.utils.helpers.streaming import Stream
from pr_firm.utils.data.presets import get_preset, save_preset
from pr_firm.utils.helpers.input_normalize import normalize_subreddit


def initialize_shared_store(shared: Dict[str, Any]) -> None:
    """Initialize the shared store with default schema."""
    shared.setdefault("config", {"style_policy": "strict"})
    shared.setdefault("task_requirements", {
        "platforms": ["email", "linkedin"],
        "intents_by_platform": {
            "email": {"type": "preset", "value": "outreach"},
            "linkedin": {"type": "custom", "value": "thought leadership"},
        },
        "topic_or_goal": "Announce our new AI feature",
        "subreddit_name_or_title": None,
        "urgency_level": "normal",
    })
    shared.setdefault("brand_bible", {
        "xml_raw": (
            "<brand>\n"
            "  <brand_name>Acme</brand_name>\n"
            "  <voice>clear</voice>\n"
            "  <tone>warm</tone>\n"
            "  <forbiddens><item>em_dash</item></forbiddens>\n"
            "</brand>"
        )
    })
    # house_style nested structure
    shared.setdefault("house_style", {
        "email_signature": {"name": None, "content": "Best,\nAcme Team"},
        "blog_style": {"name": None, "content": '{"title_case": true}'},
    })
    # top-level reddit structure
    shared.setdefault("reddit", {"rules_text": None, "description_text": None})
    shared.setdefault("platform_nuance", {
        "linkedin": {"whitespace_density": "high", "para_length": "short", "hashtag_placement": "end"},
        "twitter": {"thread_ok_above_chars": 240, "hashtag_count_range": [0, 3]},
        "instagram": {"emoji_freq": "moderate", "line_breaks": "liberal", "hashtag_count_range": [8, 20]},
        "reddit": {"markdown_blocks": ["lists", "bold"], "tl_dr_required": True},
        "email": {"subject_target_chars": 50, "single_cta_required": True},
        "blog": {"h2_h3_depth": "deep", "link_density": "medium"},
    })

    # Initialize other structures
    shared.setdefault("platform_guidelines", {})
    shared.setdefault("content_pieces", {})
    shared.setdefault("style_compliance", {})
    shared.setdefault("workflow_state", {
        "current_stage": "engagement",
        "completed_stages": [],
        "revision_count": 0,
        "manual_review_required": False,
    })
    shared.setdefault("final_campaign", {
        "approved_content": {},
        "publishing_schedule": {},
        "performance_predictions": {},
        "edit_cycle_report": None,
    })
    if "stream" not in shared or shared["stream"] is None:
        shared["stream"] = Stream()
    shared.setdefault("llm", {"model": "anthropic/claude-3.5-sonnet", "temperature": 0.7})

    # Presets integration (load if preset_name provided and content missing)
    bb = shared.get("brand_bible", {})
    preset_name = bb.get("preset_name")
    if preset_name and not bb.get("xml_raw"):
        preset = get_preset("brand_bibles", preset_name)
        if preset and preset.get("xml_raw"):
            shared["brand_bible"]["xml_raw"] = preset["xml_raw"]
    # Optional save brand bible
    if bb.get("save_as_preset") and bb.get("preset_name") and bb.get("xml_raw"):
        save_preset("brand_bibles", bb["preset_name"], {"xml_raw": bb["xml_raw"]})
    # Email signature preset
    es = shared.get("house_style", {}).get("email_signature", {})
    if es.get("name") and not es.get("content"):
        sig = get_preset("email_sigs", es["name"]) or {}
        if sig.get("content"):
            shared["house_style"]["email_signature"]["content"] = sig["content"]
    if es.get("save_as_preset") and es.get("name") and es.get("content"):
        save_preset("email_sigs", es["name"], {"content": es["content"]})
    # Blog style preset
    bs = shared.get("house_style", {}).get("blog_style", {})
    if bs.get("name") and not bs.get("content"):
        st = get_preset("blog_styles", bs["name"]) or {}
        if st.get("content"):
            shared["house_style"]["blog_style"]["content"] = st["content"]
    if bs.get("save_as_preset") and bs.get("name") and bs.get("content"):
        save_preset("blog_styles", bs["name"], {"content": bs["content"]})

    # Normalize subreddit name/title if present
    sr = shared.get("task_requirements", {}).get("subreddit_name_or_title")
    if sr:
        shared["task_requirements"]["subreddit_name_or_title"] = normalize_subreddit(sr)