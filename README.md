# README.md

<h1 align="center">Virtual PR Firm – Formatting‑First Content System</h1>

<p align="center">
  <a href="https://the-pocket.github.io/PocketFlow" target="_blank">
    <img src="./assets/banner.png" width="800" />
  </a>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/" target="_blank"><img alt="Python" src="https://img.shields.io/badge/Python-%E2%89%A53.9-blue" /></a>
  <a href="https://the-pocket.github.io/PocketFlow" target="_blank"><img alt="Made with PocketFlow" src="https://img.shields.io/badge/Made%20with-PocketFlow-8A2BE2" /></a>
  <a href="https://openrouter.ai" target="_blank"><img alt="OpenRouter" src="https://img.shields.io/badge/LLM-OpenRouter-green" /></a>
</p>

Virtual PR Firm generates platform‑optimized, on‑brand copy for Email, Instagram, Twitter/X, Reddit, LinkedIn, and Blog. It uses a formatting‑first pipeline powered by PocketFlow (a ~100‑line workflow framework) to:

- Produce per‑platform guidelines from a Brand Bible and intent
- Draft content section‑by‑section with strict length/placement constraints
- Remove AI fingerprints while enforcing hard bans (no em dash; no rhetorical contrasts)
- Validate style, brand alignment, and authenticity
- Package outputs with a simple publishing schedule and performance predictions


### Key Features
- Workflow graph with retries and a revision loop (max 5)
- Batch processing across selected platforms
- Milestone streaming for progress updates
- Local JSON presets for Brand Bible and house style
- OpenRouter‑backed LLM calls through an OpenAI‑compatible client


## Installation

### Prerequisites
- Python 3.9 or newer (3.10+ recommended)
- An OpenRouter API key (`OPENROUTER_API_KEY`)

### 1) Clone and set up a virtual environment

```bash
git clone <your-fork-or-clone-url> pr_firm
cd pr_firm

# Windows PowerShell
python -m venv .venv
. .venv\Scripts\Activate.ps1

# macOS/Linux
# python3 -m venv .venv
# source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment

Create a `.env` file (you can copy `.env.example`) and set at least:

```dotenv
OPENROUTER_API_KEY=YOUR_KEY_HERE
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1     # optional
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet         # optional override
```

Notes:
- Never commit real API keys. `.env.example` is a template—replace with your own values.
- Presets are stored at `assets/presets.json` by default; override with `PRESETS_PATH` if desired.


## Usage

### Quickstart (CLI)

```bash
python main.py
```

This runs the end‑to‑end flow with sensible defaults (Email + LinkedIn). You’ll see:
- A list of platforms processed
- Draft previews
- Optional schedule/predictions and an edit‑cycle report (if max revisions hit)

### Launch Minimal UI (Gradio)

```bash
python -c "from main import launch_gradio; launch_gradio()"
```

The UI accepts platforms, a topic/goal, an optional subreddit, and Brand Bible XML. It streams milestones and returns per‑platform drafts.

### Programmatic Example

```python
from flow import create_pr_flow

shared = {
    "task_requirements": {
        "platforms": ["email", "linkedin", "reddit"],
        "topic_or_goal": "Announce our new AI feature",
        "subreddit_name_or_title": "r/MachineLearning",
        "intents_by_platform": {
            "email": {"type": "preset", "value": "outreach"},
            "linkedin": {"type": "custom", "value": "thought leadership"},
            # "reddit" may rely on subreddit rules/description provided in shared["reddit"]
        },
    },
    "brand_bible": {"xml_raw": "<brand>...</brand>"},
    "llm": {"model": "anthropic/claude-3.5-sonnet", "temperature": 0.7},
}

pr_flow = create_pr_flow()
pr_flow.run(shared)

print(shared["final_campaign"])  # approved_content, schedule, predictions, report
```


## Project Structure

See also directory‑level `INDEX.md` files for details.

```
pr_firm/
├── main.py                     # Entry point (CLI); optional Gradio launcher
├── flow.py                     # PocketFlow graph wiring (nodes + transitions)
├── nodes.py                    # All node implementations (prep → exec → post)
├── utils/                      # Utilities for LLM calls, parsing, style, presets
├── docs/                       # High‑level design docs
├── assets/                     # Static assets and locally stored presets
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # This document
```

Highlights:
- `utils/openrouter_client.py`: OpenAI‑compatible client for OpenRouter
- `utils/call_llm.py`: Thin wrapper used by nodes to call the LLM
- `utils/brand_bible_parser.py` → `utils/brand_voice_mapper.py`: Voice/Persona
- `utils/format_platform.py`: Deterministic per‑platform guideline builder
- `utils/rewrite_with_constraints.py`: Remove AI fingerprints without breaking rules
- `utils/check_style_violations.py`: Hard and soft style checks
- `utils/presets.py`: Local JSON store for Brand Bible/Email sig/Blog style


## Configuration

Environment variables read at runtime:

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `OPENROUTER_API_KEY` | Yes | — | Auth for OpenRouter |
| `OPENROUTER_BASE_URL` | No | `https://openrouter.ai/api/v1` | API base URL |
| `OPENROUTER_MODEL` | No | `anthropic/claude-3.5-sonnet` | Default model override |
| `PRESETS_PATH` | No | `assets/presets.json` | Location of local presets JSON |


## Contributing

We welcome improvements! Suggested workflow:

1. Fork the repo and create a feature branch
2. Use clear commit messages and keep edits focused
3. Add/adjust documentation when behavior or inputs change
4. Open a Pull Request describing the change, rationale, and testing

Coding notes:
- Keep nodes small and single‑purpose; prefer clear `prep/exec/post` boundaries
- Avoid catching exceptions in utilities used by nodes; rely on node retries
- Log milestone progress through `utils/streaming.Stream`


## License

Specify your preferred license for this project (e.g., MIT) and include a `LICENSE` file.


## Contact

For questions or support, please open an issue on your repository host, or contact the maintainers.

