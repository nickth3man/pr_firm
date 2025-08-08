from typing import List, Dict, Optional
from utils.openrouter_client import chat as or_chat

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_llm(messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.7) -> str:
    """Standardized LLM call via OpenRouter client.

    - messages: list of {"role", "content"}
    - model: optional override; otherwise uses OPENROUTER_MODEL
    - temperature: decoding temperature
    """
    return or_chat(messages, model=model, temperature=temperature)

if __name__ == "__main__":
    test_messages = [{"role": "user", "content": "What is the meaning of life?"}]
    print(call_llm(test_messages))
