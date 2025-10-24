# Local Website Automation Agent

A lightweight natural-language agent that uses a local LLM via Ollama (or LM Studio API-compatible) as the "brain" and Playwright as the "hands" to automate websites like buying insurance on Geico.

## Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama installed and running (`ollama serve`), with a model pulled (e.g., `ollama pull llama3.1:8b`)
- System browsers installed (Chromium/Chrome)

## Setup
```bash
# From project root
python -m venv .venv
source .venv/bin/activate
pip install -r agent/requirements.txt

# Install Playwright browsers
python -m playwright install chromium
# optionally
python -m playwright install chrome
```

Create `agent/.env` based on `.env.example`:
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
BROWSER=chromium
HEADLESS=false
# Optional: select Chrome channel when using chromium launcher
# CHROME_CHANNEL=chrome
```

## Run
```bash
# Activate the venv first if not already
action="Buy auto insurance on geico.com and start a quote"
python agent/agent.py "$action"
```

Notes:
- The agent will narrate steps and then execute them using Playwright.
- You can switch to a different local model by changing `OLLAMA_MODEL`.

## Troubleshooting
- If Playwright cannot find a browser, run: `python -m playwright install chromium`
- Ensure Ollama is running: `ollama serve` and the model exists: `ollama pull llama3.1:8b`
- To run headless, set `HEADLESS=true`.
