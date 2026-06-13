"""
cls_blockchain.py
No-op stub for the blockchain integrity manager used by cls_foo.py.

The real cls_blockchain module is not bundled with this folder. This stub
provides the same surface used by MultiAgentOrchestrator so the multi-agent
GUI can run without actually performing any integrity checking. Every method
returns a sensible empty/identity value; conversations work normally, just
without blockchain verification.

If you ever obtain the real cls_blockchain.py, drop it in place of this file.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""


class _NoOpBlockchain:
    def get_chain_metadata(self, history):
        return {"total_blocks": len(history) if history else 0, "salt": ""}


class IntegrityManager:
    def __init__(self, global_salt=None):
        self.global_salt = global_salt or ""
        self._chains = {}

    def get_or_create_blockchain(self, agent_name, metadata=None):
        if agent_name not in self._chains:
            self._chains[agent_name] = _NoOpBlockchain()
        return self._chains[agent_name]

    def migrate_existing_history(self, agent_name, history):
        return history if history is not None else []

    def verify_agent_integrity(self, agent_name, history):
        return True, []

    def add_message_with_integrity(self, agent_name, role, content, timestamp, history):
        return {"role": role, "content": content, "timestamp": timestamp}

    def get_integrity_report(self, agent_name, history):
        return {
            "integrity_valid": True,
            "errors": [],
            "metadata": {"total_blocks": len(history) if history else 0},
        }

    def rebuild_agent_chain(self, agent_name, history, start_index):
        return history if history is not None else []
