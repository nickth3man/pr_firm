from typing import Dict, List


def build_report(violations_history: List[Dict], last_draft: str, platform: str) -> str:
    hard = sum(len(item.get("violations", [])) for item in violations_history)
    lines = [
        f"Edit cycle reached maximum for {platform}.",
        f"Total checks: {len(violations_history)}; total issues flagged: {hard}.",
        "Last draft snippet:",
        (last_draft[:240] + ("..." if len(last_draft) > 240 else "")),
    ]
    return "\n".join(lines)
