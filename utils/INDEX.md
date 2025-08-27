# /utils/INDEX.md

## Purpose and Overview

Utility modules supporting parsing, guideline building, LLM access, style checks, streaming progress, and local preset storage. Nodes in `nodes.py` use these utilities during `prep/exec/post` steps.

## Files and Descriptions

- `__init__.py`: Package marker.
- `openrouter_client.py`: OpenAI‑compatible client configured for OpenRouter. Reads `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL`.
- `call_llm.py`: Thin wrapper around `openrouter_client.chat()` for standardized LLM calls.
- `brand_bible_parser.py`: Tolerant XML parser extracting `brand_name`, `voice`, `tone`, and `forbiddens`.
- `brand_voice_mapper.py`: Maps parsed Brand Bible to a `persona_voice` structure with controlled vocabulary and defaults.
- `format_platform.py`: Deterministic per‑platform guideline builder. Returns unified schema: `limits`, `structure`, `style`, `hashtags`, `links`, `markdown`, `cta`, `notes`, `section_budgets`.
- `rewrite_with_constraints.py`: Conservative text rewrite to remove banned patterns (e.g., em dash, rhetorical contrasts) while keeping meaning.
- `check_style_violations.py`: Detects hard bans and soft fingerprints; returns `{"violations": [...], "score": float}`.
- `report_builder.py`: Concise summary when maximum revision cycles are hit.
- `progress.py`: Utility to convert stage counts to percentage.
- `input_normalize.py`: Normalizes subreddit names/URLs to canonical identifiers.
- `presets.py`: Local JSON store for presets (brand bibles, email signatures, blog styles). Uses `PRESETS_PATH` or defaults to `assets/presets.json`.
- `streaming.py`: Milestone‑only stream buffer for UI/CLI progress updates.

## Usage

Common patterns (examples):

- LLM call:

  ```python
  from utils.call_llm import call_llm
  resp = call_llm([{"role": "user", "content": "Hello"}], model="anthropic/claude-3.5-sonnet", temperature=0.7)
  ```

- Build guidelines:

  ```python
  from utils.format_platform import build_guidelines
  g = build_guidelines("linkedin", persona_voice, "thought leadership", platform_nuance={"hashtag_count_range": [0,3]})
  ```

- Presets:

  ```python
  from utils.presets import save_preset, get_preset
  save_preset("email_sigs", "Standard", {"content": "Best,\\nAcme Team"})
  sig = get_preset("email_sigs", "Standard")
  ```

## Dependencies / Prerequisites

- `openai` package (for OpenRouter OpenAI‑compatible client)
- Environment variables: `OPENROUTER_API_KEY` (required), `OPENROUTER_BASE_URL` (optional), `OPENROUTER_MODEL` (optional), `PRESETS_PATH` (optional)
- See `requirements.txt` for full Python dependencies.
