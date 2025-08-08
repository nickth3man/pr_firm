import json
import os
from typing import Any, Dict, List, Optional

_PRESETS_PATH = os.getenv("PRESETS_PATH", os.path.join(os.path.dirname(__file__), "..", "assets", "presets.json"))


def _ensure_file() -> None:
    os.makedirs(os.path.dirname(_PRESETS_PATH), exist_ok=True)
    if not os.path.exists(_PRESETS_PATH):
        with open(_PRESETS_PATH, "w", encoding="utf-8") as f:
            json.dump({"brand_bibles": {}, "email_sigs": {}, "blog_styles": {}}, f, indent=2)


def _read() -> Dict[str, Any]:
    _ensure_file()
    with open(_PRESETS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(data: Dict[str, Any]) -> None:
    with open(_PRESETS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_preset(category: str, name: str, payload: Dict[str, Any]) -> None:
    data = _read()
    data.setdefault(category, {})[name] = payload
    _write(data)


def get_preset(category: str, name: str) -> Optional[Dict[str, Any]]:
    data = _read()
    return data.get(category, {}).get(name)


def list_presets(category: str) -> List[str]:
    data = _read()
    return sorted(list(data.get(category, {}).keys()))
