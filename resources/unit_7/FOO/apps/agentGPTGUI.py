"""
agentGPTGUI.py
Single-agent chat GUI seeded with OpenAI. Uses the shared SingleAgentGUI from
single_agent_gui.py: Provider + Model dropdowns, unified file drop (Context
or RAG), per-agent knowledge base, role switcher.

CLI:
    python agentGPTGUI.py                  # default role: general.md
    python agentGPTGUI.py researcher.md
    python agentGPTGUI.py grant_writer_NIH.md

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
import argparse
import _bootstrap  # noqa: F401  -- inserts <root>/classes and <root>/apps into sys.path
from single_agent_gui import launch


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Single-OpenAI-agent chat GUI.")
    parser.add_argument(
        "role_md",
        nargs="?",
        default="general.md",
        help="Path to a role markdown file (default: general.md). Examples: researcher.md, grant_writer_NIH.md, article_reviewer.md.",
    )
    args = parser.parse_args()
    launch(preferred_provider="openai", window_title="JuanGPT", role_md=args.role_md)
