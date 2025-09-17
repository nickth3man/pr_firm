from pocketflow import Node
from typing import Dict, Any
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

from pr_firm.utils.llm.call_llm import call_llm
from pr_firm.core.shared_store import initialize_shared_store


class EngagementManagerNode(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "task_requirements": shared.get("task_requirements", {}),
            "brand_bible": shared.get("brand_bible", {}),
            "house_style": shared.get("house_style", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep: Dict[str, Any]) -> Dict[str, Any]:
        # Propose auto-intents if any platform marked as type "auto"
        intents_by_platform = dict(prep.get("task_requirements", {}).get("intents_by_platform", {}))
        platforms = prep.get("task_requirements", {}).get("platforms", [])
        topic = prep.get("task_requirements", {}).get("topic_or_goal", "")
        auto_platforms = [p for p in platforms if (isinstance(intents_by_platform.get(p), dict) and intents_by_platform.get(p, {}).get("type") == "auto")]
        if not auto_platforms:
            return {"auto_intents": {}}
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.3)
        prompt = (
            "Suggest concise posting intents per platform for the given topic."
            " Respond in YAML mapping platform->intent string.\n"
            f"Platforms: {', '.join(auto_platforms)}\nTopic: {topic}"
        )
        messages = [
            {"role": "system", "content": "You are a marketing strategist."},
            {"role": "user", "content": prompt},
        ]
        resp = call_llm(messages, model=model, temperature=temperature)
        auto_map: Dict[str, str] = {}
        if yaml:
            try:
                y = yaml.safe_load(resp)
                if isinstance(y, dict):
                    auto_map = {str(k).lower(): str(v) for k, v in y.items()}
            except Exception:
                auto_map = {}
        return {"auto_intents": auto_map}

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        # Initialize shared store using common function
        initialize_shared_store(shared)

        # Merge auto-intents if produced
        auto_map = (exec_res or {}).get("auto_intents", {})
        if auto_map:
            intents = shared["task_requirements"].setdefault("intents_by_platform", {})
            for plat, intent in auto_map.items():
                intents[plat] = {"type": "auto", "value": intent}

        # Stream engagement milestone only (per streaming policy)
        shared["stream"].emit("milestone", "Engagement data prepared")
        shared["workflow_state"]["current_stage"] = "brand_bible_ingest"
        shared["workflow_state"]["completed_stages"].append("engagement")
        return "default"