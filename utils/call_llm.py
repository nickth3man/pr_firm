from typing import List, Dict, Optional
import time
import threading
from utils.openrouter_client import chat as or_chat

# Simple rate limiter + circuit breaker wrapper around the OpenRouter chat client.
# - Rate limiter: allow up to `max_calls` per `period_s` seconds using a fixed-window counter.
# - Circuit breaker: open the circuit after `failure_threshold` consecutive failures, stay open
#   for `open_duration_s` seconds, then attempt half-open checks.


class SimpleRateLimiter:
    def __init__(self, max_calls: int = 10, period_s: int = 1):
        self.max_calls = max_calls
        self.period_s = period_s
        self._lock = threading.Lock()
        self._window_start = time.time()
        self._count = 0

    def allow(self) -> bool:
        now = time.time()
        with self._lock:
            if now - self._window_start >= self.period_s:
                self._window_start = now
                self._count = 0
            if self._count < self.max_calls:
                self._count += 1
                return True
            return False


class SimpleCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, open_duration_s: int = 30):
        self.failure_threshold = failure_threshold
        self.open_duration_s = open_duration_s
        self._failures = 0
        self._state = "closed"  # closed, open, half_open
        self._opened_at = 0.0
        self._lock = threading.Lock()

    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            if self._state != "closed":
                self._state = "closed"

    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._state = "open"
                self._opened_at = time.time()

    def allow_request(self) -> bool:
        with self._lock:
            if self._state == "closed":
                return True
            if self._state == "open":
                if time.time() - self._opened_at >= self.open_duration_s:
                    # transition to half-open; allow a trial request
                    self._state = "half_open"
                    return True
                return False
            # half_open: allow a single request to test
            return True


# Global simple defaults; tests or calling code can replace these if needed
_RATE_LIMITER = SimpleRateLimiter(max_calls=10, period_s=1)
_CIRCUIT_BREAKER = SimpleCircuitBreaker(failure_threshold=5, open_duration_s=30)


def call_llm(messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.7) -> str:
    """Call the LLM with basic rate-limiting and a circuit breaker.

    This is intentionally lightweight and synchronous to match existing usage.
    If the circuit is open or rate limit is exceeded, raise a RuntimeError so callers
    can decide how to handle (retries, fallbacks).
    """

    if not _RATE_LIMITER.allow():
        raise RuntimeError("Rate limit exceeded for LLM calls")

    if not _CIRCUIT_BREAKER.allow_request():
        raise RuntimeError("LLM circuit breaker is open")

    try:
        resp = or_chat(messages, model=model, temperature=temperature)
        _CIRCUIT_BREAKER.record_success()
        return resp
    except Exception:
        _CIRCUIT_BREAKER.record_failure()
        raise


if __name__ == "__main__":
    test_messages = [{"role": "user", "content": "What is the meaning of life?"}]
    print(call_llm(test_messages))
