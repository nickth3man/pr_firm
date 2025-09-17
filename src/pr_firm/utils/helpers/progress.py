from typing import Tuple


def progress_for_stage(completed: int, total: int) -> Tuple[int, str]:
    total = max(1, total)
    pct = int((completed / total) * 100)
    return pct, f"{pct}% complete"
