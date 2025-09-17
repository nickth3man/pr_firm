import re
from typing import Dict

# Very conservative auto-fix; real implementation should use LLM with self-check

def rewrite_with_constraints(text: str, voice: Dict, guidelines: Dict) -> str:
    if not text:
        return text

    # 1) Replace em dashes with "; " to avoid banned punctuation while preserving cadence
    out = text.replace("—", "; ")

    # 2) Transform rhetorical contrast to non-contrastive phrasing rather than deleting content.
    #    Examples:
    #      "not X but Y"        -> "X and Y"
    #      "not just X but Y"   -> "X and Y"
    # Keep it conservative to avoid dropping surrounding text.
    def _rc_sub(match: re.Match) -> str:
        # match groups: optional "just ", group for X, and the trailing " but "
        x = (match.group(2) or "").strip()
        # We cannot directly capture Y via this regex; do a localized replace from the original span
        # Strategy: Replace the leading "not [just ]<x> but" with "<x> and" and leave following text intact
        prefix = text[: match.start()]
        suffix = text[match.end():]
        # Build the replacement fragment
        return f"{x} and "

    # Replace the leading contrast phrase with coordination, leaving the rest of the sentence.
    # We run this iteratively to handle multiple instances.
    pattern = re.compile(r"\bnot\s+(?:just\s+)?([^.,;!?]{1,80}?)\s+but\s+", re.IGNORECASE)
    last = None
    while last != out:
        last = out
        out = pattern.sub(lambda m: f"{m.group(1).strip()} and ", out)

    return out
