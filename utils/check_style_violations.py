import re
from typing import Dict, List

# Hard bans (gate flow):
HARD_PATTERNS = [
    ("em_dash", re.compile(r"—")),
    ("rhetorical_contrast", re.compile(r"\bnot\s+(?:just\s+)?[^.?!]{0,80}?\s+but\b", re.IGNORECASE)),
]

# Soft fingerprints (do not gate flow, but reported):
SOFT_PATTERNS = [
    ("tidy_wrap_up", re.compile(r"\b(in conclusion|to sum up|in summary)\b", re.IGNORECASE)),
    ("listicle_cliche", re.compile(r"\b(\d+\s+(ways|tips|things)\b)", re.IGNORECASE)),
    ("weasel_words", re.compile(r"\b(world-class|cutting-edge|state-of-the-art|leverage|unlock|empower)\b", re.IGNORECASE)),
    ("monotone_rhythm", re.compile(r"(?:^|\n)(?:[A-Z][^.!?]{10,}[.!?]\s*){5,}", re.MULTILINE)),
]


def check_style_violations(text: str) -> Dict:
    """Detect style issues.

    Returns: {
      "violations": [{"type": str, "span": (start, end), "severity": "hard"|"soft"}...],
      "score": float
    }
    """
    violations: List[Dict] = []
    corpus = text or ""

    for name, pat in HARD_PATTERNS:
        for m in pat.finditer(corpus):
            violations.append({"type": name, "span": (m.start(), m.end()), "severity": "hard"})

    for name, pat in SOFT_PATTERNS:
        for m in pat.finditer(corpus):
            violations.append({"type": name, "span": (m.start(), m.end()), "severity": "soft"})

    # Style score penalizes both, with heavier penalty for hard
    hard_cnt = sum(1 for v in violations if v["severity"] == "hard")
    soft_cnt = sum(1 for v in violations if v["severity"] == "soft")
    score = max(0.0, 1.0 - 0.3 * hard_cnt - 0.1 * soft_cnt)
    return {"violations": violations, "score": score}
