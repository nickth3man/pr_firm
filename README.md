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


## Troubleshooting

### Common Setup Issues

#### 1. **OpenRouter API Key Issues**

**Error**: `openai.AuthenticationError: Incorrect API key provided`
- **Solution**: Verify your `OPENROUTER_API_KEY` in `.env` is correct
- **Check**: Visit [OpenRouter Keys](https://openrouter.ai/keys) to verify your key
- **Test**: Run `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key loaded:', bool(os.getenv('OPENROUTER_API_KEY')))"`

**Error**: `openai.RateLimitError: Rate limit exceeded`
- **Solution**: Check your OpenRouter account limits or upgrade your plan
- **Workaround**: Add delays between requests or reduce batch sizes

#### 2. **Virtual Environment Issues**

**Error**: `ModuleNotFoundError: No module named 'pocketflow'`
- **Solution**: Ensure you're in the correct virtual environment
- **Check**: Run `which python` or `python --version` to verify environment
- **Fix**: Activate venv: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)

**Error**: `pip install -r requirements.txt` fails
- **Solution**: Upgrade pip first: `pip install --upgrade pip`
- **Alternative**: Install packages individually: `pip install pocketflow openai python-dotenv PyYAML gradio`

#### 3. **Python Version Issues**

**Error**: `Python 3.9+ required but found 3.8`
- **Solution**: Check Python version: `python --version`
- **Fix**: Install Python 3.9+ or use `python3` instead of `python`

#### 4. **Environment File Issues**

**Error**: `.env file not found`
- **Solution**: Copy `.env.example` to `.env`: `cp .env.example .env`
- **Check**: Ensure `.env` exists in project root: `ls -la .env`

**Error**: `Environment variable not loaded`
- **Solution**: Verify `.env` format (no spaces around `=`)
- **Test**: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENROUTER_API_KEY', 'NOT_FOUND'))"`

#### 5. **Model/Platform Issues**

**Error**: `openai.NotFoundError: The model 'xyz' does not exist`
- **Solution**: Check available models at [OpenRouter Models](https://openrouter.ai/models)
- **Fix**: Update `OPENROUTER_MODEL` in `.env` to a valid model name

**Error**: Platform-specific content generation fails
- **Solution**: Verify platform intents are properly configured
- **Check**: Review `assets/presets.json` for platform-specific settings

### Testing Setup

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest tests/unit/      # Run unit tests directory
```

#### Common Test Issues

**Error**: `pytest not found`
- **Solution**: Install test dependencies: `pip install pytest pytest-cov pytest-asyncio`

**Error**: `ModuleNotFoundError` in tests
- **Solution**: Ensure test environment has all dependencies: `pip install -r requirements.txt`

### Performance Optimization

#### Common Performance Issues

**Slow LLM Responses**
- **Solution**: Experiment with different models in `OPENROUTER_MODEL`
- **Alternative**: Use models with faster inference times

**Memory Issues**
- **Solution**: Reduce batch sizes in PocketFlow configurations
- **Monitor**: Use `utils/streaming.py` to monitor memory usage

**Rate Limiting**
- **Solution**: Implement exponential backoff in your flows
- **Configure**: Adjust retry settings in node configurations

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Look for detailed error messages in console output
2. **Verify versions**: Run `pip list` to check installed package versions
3. **Test components**: Use `python -c "import pocketflow; print('PocketFlow OK')"` to test individual components
4. **Community support**: Check [PocketFlow GitHub](https://github.com/the-pocket/PocketFlow) for similar issues

### Development Mode

For development and debugging:

```bash
# Enable verbose logging
export PYTHONPATH=$PYTHONPATH:.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"

# Run with debug mode
python main.py --debug

# Test individual components
python -c "from utils.call_llm import call_llm; print(call_llm('Hello'))"
```

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

