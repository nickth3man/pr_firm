from typing import Generator, List, Tuple
import time

class Stream:
    """Milestone-only streaming utility.

    Usage:
        s = Stream()
        s.emit("info", "Starting...")
        for role, text, ts in s.messages():
            ...
    """

    def __init__(self) -> None:
        self._buffer: List[Tuple[str, str, float]] = []

    def emit(self, role: str, text: str) -> None:
        self._buffer.append((role, text, time.time()))
        # For CLI demo, also print immediately
        print(f"[{role}] {text}")

    def messages(self) -> Generator[Tuple[str, str, float], None, None]:
        for item in self._buffer:
            yield item
