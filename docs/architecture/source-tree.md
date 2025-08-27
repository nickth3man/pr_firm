---
title: "pr_firm Source Tree"
---

Top-level files and directories:

- `flow.py` — flow assembly and BatchFlow for platform guidelines
- `nodes.py` — Node implementations
- `main.py` — example runner and optional Gradio UI
- `utils/` — utility modules (LLM client, brand parser, style checks, presets, etc.)
- `docs/` — documentation (PRD, architecture, stories)
- `rules/` — agent rules and coding guidelines
- `.bmad-core/` — BMAD templates and config
- `web-bundles/agents/` — agent personas and templates

## Notable utils

- `utils/openrouter_client.py` — OpenRouter/OpenAI wrapper
- `utils/call_llm.py` — LLM wrapper
- `utils/brand_bible_parser.py` — parse brand bible XML
- `utils/brand_voice_mapper.py` — map parsed bible to persona voice
- `utils/format_platform.py` — generate Guidelines per platform
- `utils/rewrite_with_constraints.py` — conservative rewrite to remove banned patterns
- `utils/check_style_violations.py` — detect hard/soft style violations
- `utils/presets.py` — manage local presets
- `utils/streaming.py` — milestone streaming
