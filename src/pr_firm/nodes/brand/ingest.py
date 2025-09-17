from pocketflow import Node
from typing import Dict, Any

from pr_firm.utils.helpers.brand_bible_parser import parse as parse_brand_bible
from pr_firm.utils.content.brand_voice_mapper import brand_bible_to_voice


class BrandBibleIngestNode(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        return shared.get("brand_bible", {}).get("xml_raw", "")

    def exec(self, xml_raw: str) -> Dict[str, Any]:
        parsed, missing = parse_brand_bible(xml_raw)
        persona = brand_bible_to_voice(parsed)
        return {"parsed": parsed, "missing": missing, "persona": persona}

    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> str:
        shared.setdefault("brand_bible", {})
        shared["brand_bible"]["parsed"] = exec_res["parsed"]
        shared["brand_bible"]["missing"] = exec_res["missing"]
        shared["brand_bible"]["persona_voice"] = exec_res["persona"]
        # No streaming here per policy
        shared["workflow_state"]["current_stage"] = "voice_alignment"
        shared["workflow_state"]["completed_stages"].append("brand_bible_ingest")
        return "default"