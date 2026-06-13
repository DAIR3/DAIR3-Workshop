"""
agentClaude.py
Single-agent chat GUI seeded with Anthropic Claude. Uses the shared
SingleAgentGUI from single_agent_gui.py: Provider + Model dropdowns, unified
file drop (Context or RAG), per-agent knowledge base, role switcher.

CLI:
    python agentClaude.py                  # default role: general.md
    python agentClaude.py researcher.md
    python agentClaude.py grant_writer_NIH.md

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
import argparse
import _bootstrap  # noqa: F401  -- inserts <root>/classes and <root>/apps into sys.path
from single_agent_gui import launch


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Single-Claude-agent chat GUI.")
    parser.add_argument(
        "role_md",
        nargs="?",
        default="general.md",
        help="Path to a role markdown file (default: general.md). Examples: researcher.md, grant_writer_NIH.md, article_reviewer.md.",
    )
    args = parser.parse_args()
    launch(preferred_provider="anthropic", window_title="JuanClaude", role_md=args.role_md)
