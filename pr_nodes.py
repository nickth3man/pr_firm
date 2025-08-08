from typing import Any, Dict, List
from pocketflow import Node
from utils.streaming import Stream
from utils.brand_bible_parser import parse as parse_brand_bible
from utils.brand_voice_mapper import brand_bible_to_voice
from utils.format_platform import build_guidelines


class EngagementManagerNode(Node):
    def exec(self, _):
        # In this minimal version, seed from defaults if not present in shared via post()
        return None

    def post(self, shared: Dict[str, Any], prep_res, exec_res):
        # Initialize shared store if missing
        shared.setdefault("config", {"style_policy": "strict"})
        shared.setdefault("task_requirements", {
            "platforms": ["email", "linkedin"],
            "intents_by_platform": {"email": {"type": "preset", "value": "outreach"}, "linkedin": {"type": "custom", "value": "thought leadership"}},
            "topic_or_goal": "Announce our new AI feature",
            "reddit": {"name": None, "rules": None, "description": None},
        })
        shared.setdefault("brand_bible", {
            "xml_raw": """
            <brand>
              <brand_name>Acme</brand_name>
              <voice>clear</voice>
              <tone>warm</tone>
              <forbiddens><item>em_dash</item></forbiddens>
            </brand>
            """.strip()
        })
        shared.setdefault("email_signature", "Best,\nAcme Team")
        shared.setdefault("house_style", {"blog": {"title_case": True}})
        shared.setdefault("platform_guidelines", {})
        shared.setdefault("content_pieces", {})
        shared.setdefault("style_compliance", {})
        shared.setdefault("workflow_state", {"current_stage": "engagement", "completed_stages": [], "revision_count": 0, "manual_review_required": False})
        shared.setdefault("final_campaign", {"approved_content": {}, "publishing_schedule": {}, "performance_predictions": {}, "edit_cycle_report": None})
        if "stream" not in shared or shared["stream"] is None:
            shared["stream"] = Stream()
        shared.setdefault("llm", {"model": "anthropic/claude-3.5-sonnet", "temperature": 0.7})

        shared["stream"].emit("milestone", "Engagement data prepared")
        shared["workflow_state"]["current_stage"] = "brand_bible_ingest"
        shared["workflow_state"]["completed_stages"].append("engagement")
        return "default"


class BrandBibleIngestNode(Node):
    def prep(self, shared: Dict[str, Any]):
        return shared.get("brand_bible", {}).get("xml_raw", "")

    def exec(self, xml_raw: str):
        parsed, missing = parse_brand_bible(xml_raw)
        persona = brand_bible_to_voice(parsed)
        return {"parsed": parsed, "missing": missing, "persona": persona}

    def post(self, shared: Dict[str, Any], prep_res, exec_res):
        shared.setdefault("brand_bible", {})
        shared["brand_bible"]["parsed"] = exec_res["parsed"]
        shared["brand_bible"]["missing"] = exec_res["missing"]
        shared["brand_bible"]["persona_voice"] = exec_res["persona"]
        shared["stream"].emit("milestone", "Brand Bible ingested")
        shared["workflow_state"]["current_stage"] = "voice_alignment"
        shared["workflow_state"]["completed_stages"].append("brand_bible_ingest")
        return "default"


class VoiceAlignmentNode(Node):
    def prep(self, shared: Dict[str, Any]):
        return shared.get("brand_bible", {}).get("persona_voice", {})

    def exec(self, persona_voice: Dict[str, Any]):
        # Enforce strict forbiddens (already set in mapper)
        return persona_voice

    def post(self, shared: Dict[str, Any], prep_res, exec_res):
        shared["persona_voice"] = exec_res
        shared["stream"].emit("milestone", "Voice alignment complete")
        shared["workflow_state"]["current_stage"] = "guidelines"
        shared["workflow_state"]["completed_stages"].append("voice_alignment")
        return "default"


class FormatGuidelinesNode(Node):
    def prep(self, shared: Dict[str, Any]):
        return {
            "platforms": shared.get("task_requirements", {}).get("platforms", []),
            "intents": shared.get("task_requirements", {}).get("intents_by_platform", {}),
            "persona": shared.get("persona_voice", {}),
            "reddit": shared.get("task_requirements", {}).get("reddit", {}),
        }

    def exec(self, prep):
        platforms: List[str] = prep["platforms"]
        intents = prep["intents"]
        persona = prep["persona"]
        reddit = prep["reddit"]
        out: Dict[str, Any] = {}
        for p in platforms:
            intent_val = intents.get(p, {}).get("value", "general") if isinstance(intents.get(p), dict) else intents.get(p, "general")
            out[p] = build_guidelines(p, persona, intent_val, platform_nuance={}, reddit=reddit if p == "reddit" else None)
        return out

    def post(self, shared: Dict[str, Any], prep_res, exec_res):
        shared["platform_guidelines"].update(exec_res)
        shared["stream"].emit("milestone", f"Guidelines ready for: {', '.join(exec_res.keys())}")
        shared["workflow_state"]["current_stage"] = "content_craftsman"
        shared["workflow_state"]["completed_stages"].append("guidelines")
        return "default"
