import re
from typing import Dict, List

HARD_PATTERNS = [
    ("em_dash", re.compile(r"—")),
    ("rhetorical_contrast", re.compile(r"\bnot\s+(?:just\s+)?[^.?!]{0,80}?\s+but\b", re.IGNORECASE)),
]


def check_style_violations(text: str) -> Dict:
    """Detect hard-banned patterns and compute a naive score.

    Returns: {"violations": [{"type": str, "span": (start, end)}...], "score": float}
    """
    violations: List[Dict] = []
    for name, pat in HARD_PATTERNS:
        for m in pat.finditer(text or ""):
            violations.append({"type": name, "span": (m.start(), m.end())})

    # Naive style score: 1.0 if no violations, else decreases
    score = max(0.0, 1.0 - 0.2 * len(violations))
    return {"violations": violations, "score": score}
