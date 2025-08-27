---
title: "pr_firm Technical Summary"
---

This technical summary extracts key runtime and architecture details useful for engineers implementing the Brownfield enhancements.

## Runtime & Requirements

- Python 3.x runtime
- Environment:
  - `OPENROUTER_API_KEY` required for LLM calls
  - Optional: `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`
- Optional dependency: `gradio` (UI wrapper in `main.py`)

## Architecture Overview

- The project follows a Node+Flow graph in `flow.py` and `nodes.py` using a PocketFlow-like abstraction.
- Core nodes handle ingestion, LLM calls, rewrite, compliance checks, and packaging.

## Testing & Validation

- Unit test targets:
  - `utils/brand_bible_parser.py` parsing edge cases
  - `utils/format_platform.py` guideline generation rules
  - `utils/rewrite_with_constraints.py` conservative rewrites
  - `nodes.ContentCraftsmanNode` section generation behavior (mock LLM)

## CI Recommendations

- Add pipeline steps: lint, unit tests, integration test (mock LLM), and an optional smoke run with real LLM creds in a secure job only.
