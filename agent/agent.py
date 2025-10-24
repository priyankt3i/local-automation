from __future__ import annotations
import os
import asyncio
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
import sys
from pathlib import Path
from rich.console import Console
from interpreter import Interpreter

from browser import BrowserController

console = Console()


@dataclass
class AgentConfig:
    ollama_host: str
    ollama_model: str
    browser: str = "chromium"
    headless: bool = False

    @staticmethod
    def from_env() -> "AgentConfig":
        # Ensure we load .env from the agent directory and allow importing local modules
        agent_dir = Path(__file__).resolve().parent
        if str(agent_dir) not in sys.path:
            sys.path.insert(0, str(agent_dir))
        load_dotenv(dotenv_path=agent_dir / ".env", override=False)
        return AgentConfig(
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            browser=os.getenv("BROWSER", "chromium"),
            headless=os.getenv("HEADLESS", "false").lower() == "true",
        )


def create_interpreter(cfg: AgentConfig) -> Interpreter:
    itp = Interpreter()
    # Use local Ollama as the LLM backend
    itp.llm.api_base = cfg.ollama_host
    itp.llm.api_key = "ollama"  # not used by Ollama
    itp.llm.model = cfg.ollama_model
    itp.auto_run = True
    itp.max_output_tokens = 4096
    # Safer defaults; you can allow shell with caution
    itp.system_message = (
        "You are an automation agent. You can write Python to control Playwright "
        "via the provided BrowserController to accomplish user goals on websites. "
        "Prefer deterministic selectors, wait for network idle when needed, and "
        "explain your plan briefly before acting. Ask for missing info."
    )
    return itp


async def run_goal(goal: str, cfg: Optional[AgentConfig] = None) -> None:
    cfg = cfg or AgentConfig.from_env()
    console.rule("Agent Starting")
    console.print(f"Model: [bold]{cfg.ollama_model}[/bold] @ {cfg.ollama_host}")
    console.print(f"Browser: [bold]{cfg.browser}[/bold], headless={cfg.headless}")

    itp = create_interpreter(cfg)

    # Inject a helper into the interpreter's Python environment
    # so the model can import and use BrowserController.
    itp.imports = [
        # Make sure the interpreter can import our local browser helper
        "import sys, os",
        "sys.path.insert(0, os.path.dirname(__file__))",
        "from browser import BrowserController",
    ]

    # Instruct the agent with a high-level tool description
    tool_context = f"""
You have access to a Playwright wrapper named BrowserController with methods:
- launch() auto-called in context manager
- goto(url)
- click(selector)
- fill(selector, value)
- wait_for_selector(selector, timeout_ms=15000)
- text_content(selector)
Use CSS selectors. Prefer labels and placeholders for forms.
When completing tasks on websites, narrate next steps, then execute.
"""

    prompt = f"Goal: {goal}\n\n{tool_context}\nReturn success when the goal is completed."

    # Run interaction. User can type follow-ups in the terminal session.
    await asyncio.to_thread(itp.chat, prompt)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Natural-language website automation agent")
    parser.add_argument("goal", type=str, nargs="+", help="What you want to achieve")
    args = parser.parse_args()

    goal = " ".join(args.goal)

    try:
        asyncio.run(run_goal(goal))
    except KeyboardInterrupt:
        console.print("\nInterrupted.")


if __name__ == "__main__":
    main()
