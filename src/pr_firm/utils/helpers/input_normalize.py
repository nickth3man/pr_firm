import re


def normalize_subreddit(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""

    # If URL or contains /r/<name>, extract name precisely
    m = re.search(r"(?:^https?://[^\s]+)?(?:^|/)r/([A-Za-z0-9_]+)\b", s, flags=re.IGNORECASE)
    if m:
        return m.group(1).lower()

    # Strip exactly a leading "r/" or "/r/" if present
    s = re.sub(r"^(?:/?r/)", "", s, flags=re.IGNORECASE)
    return s.lower()
