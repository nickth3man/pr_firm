import re
from typing import Dict

# Very conservative auto-fix; real implementation should use LLM with self-check

def rewrite_with_constraints(text: str, voice: Dict, guidelines: Dict) -> str:
    if not text:
        return text
    out = text
    # Replace em dashes with "; " to break run-ons without hyphen ambiguity
    out = out.replace("—", "; ")
    # Remove simple rhetorical contrast patterns
    out = re.sub(r"\bnot\s+(just\s+)?(.*?)(\s+but\s+)", "", out, flags=re.IGNORECASE)
    return out
