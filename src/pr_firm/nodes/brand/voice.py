from pocketflow import Node
from typing import Dict, Any


class VoiceAlignmentNode(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return shared.get("brand_bible", {}).get("persona_voice", {})

    def exec(self, persona_voice: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize tone axes/styles; ensure forbiddens include hard bans
        persona_voice = dict(persona_voice or {})
        persona_voice.setdefault("axes", {}).setdefault("formality", "medium")
        persona_voice.setdefault("axes", {}).setdefault("vividness", "balanced")
        persona_voice.setdefault("styles", {}).setdefault("voice", persona_voice.get("styles", {}).get("voice", "clear"))
        forb = persona_voice.setdefault("forbiddens", {})
        forb["em_dash"] = True
        forb["rhetorical_contrast"] = True
        return persona_voice

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        # Write back to brand_bible.persona_voice per schema
        shared.setdefault("brand_bible", {})
        shared["brand_bible"]["persona_voice"] = exec_res
        # No streaming here per policy
        shared["workflow_state"]["current_stage"] = "guidelines"
        shared["workflow_state"]["completed_stages"].append("voice_alignment")
        return "default"