def normalize_subreddit(s: str) -> str:
    s = (s or "").strip()
    if s.startswith("http"):
        # crude extraction
        parts = s.split("/")
        if "r" in parts:
            idx = parts.index("r")
            if idx + 1 < len(parts):
                s = parts[idx + 1]
    s = s.lstrip("r/")
    return s.lower()
