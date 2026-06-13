"""
clsAnthropic.py
Anthropic Claude Agent class for multi-agent chat system.
Compatible with ClaudeChat.py and ClaudeGUI.py architecture.

By Juan B. Gutiérrez, Professor of Mathematics 
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""

import os
import anthropic
import json
import sys
import uuid
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
#from cls_blockchain import IntegrityManager


def _extract_anthropic_usage(response):
    """Pull token usage off an Anthropic Messages response. Returns None if absent."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    inp = getattr(usage, "input_tokens", None)
    out = getattr(usage, "output_tokens", None)
    return {"input": inp, "output": out, "total": (inp + out) if (inp is not None and out is not None) else None}


def _extract_text(response):
    """Concatenate all text blocks from an Anthropic Messages response.

    Why: Claude 4.x with extended thinking can return one or more ThinkingBlocks
    before any TextBlock, so the old `response.content[0].text` raised
    AttributeError. A response that hit stop_reason='max_tokens' before producing
    any text yields content=[] and raised IndexError. Walking content and
    concatenating every block that exposes `.text` handles both.

    Returns ("", stop_reason) if no text block was found, so callers can build
    a useful error message instead of crashing.
    """
    blocks = getattr(response, "content", None) or []
    pieces = [b.text for b in blocks if getattr(b, "text", None)]
    stop_reason = getattr(response, "stop_reason", None)
    return ("\n".join(pieces), stop_reason)


# Anthropic deprecated the temperature parameter on Opus 4.7+. Older Sonnet/Haiku
# still accept it. Returns {'temperature': value} only for models that allow it.
_TEMPERATURE_DEPRECATED_PREFIXES = ("claude-opus-4-7",)


def _temperature_kwarg(model, value):
    for prefix in _TEMPERATURE_DEPRECATED_PREFIXES:
        if model.startswith(prefix):
            return {}
    return {"temperature": value}


class ClaudeWorker(QThread):
    """Worker thread for Claude API calls to prevent GUI blocking"""
    result_ready = pyqtSignal(str)

    def __init__(self, user_input, client, model, history):
        super().__init__()
        self.user_input = user_input
        self.client = client
        self.model = model
        self.history = history

    def run(self):
        try:
            # Clean history to remove timestamps before sending to API
            clean_history = []
            for entry in self.history:
                if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                    clean_entry = {
                        "role": entry["role"],
                        "content": entry["content"]
                    }
                    clean_history.append(clean_entry)
            
            # Add current user input
            clean_history.append({"role": "user", "content": self.user_input})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100000,
                messages=clean_history,
                **_temperature_kwarg(self.model, 0.99),
            )
            content, stop_reason = _extract_text(response)
            if not content:
                content = f"(no text content; stop_reason={stop_reason})"

            # Add response with timestamp to the original history
            timestamp = datetime.now().isoformat()
            self.history.append({
                "role": "assistant", 
                "content": content,
                "timestamp": timestamp
            })
            
            self.result_ready.emit(content)
        except Exception as e:
            self.result_ready.emit(f"Error: {e}")


class AnthropicAgent:
    """Anthropic Claude Agent class compatible with ClaudeChat.py architecture"""
    
    def __init__(self, model, name, instructions, user, config, model_entry=None):
        self.model = model
        self.name = name
        self.user = user
        self.config = config
        self.latest_response = ""
        self.active = True
        self.integrity_issues = []
        self.integrity_valid = True        

        # Build instructions with preamble
        preamble = f"Address the user as Dr. {user}.\n\n Introduce yourself as {name}, AI assistant.\n\n "
        
        # Add agent-specific directive if available
        agent_directive = ""
        if model_entry and "agent_directive" in model_entry:
            agent_directive = f"\n\nAgent specific instructions:\n{model_entry['agent_directive']}\n"
        
        self.instructions = preamble + instructions + agent_directive
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set. Claude agents will not function.")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Initialize conversation history
        self.history = []
        self.history.append({"role": "user", "content": self.instructions})
        self.display_history = []  # For UI display with timestamps
        
        # Set up history file path using CWD from config
        cwd = config.get("CWD", "/chats")
        if cwd.startswith("/"):
            cwd_path = cwd[1:]  # Remove leading slash for relative path
        else:
            cwd_path = cwd
            
        self.history_file = os.path.join(cwd_path, f"{self.name}.json")
        print(f"Anthropic Agent {self.name} will use history file: {self.history_file}")
        
        # Ensure the directory exists
        os.makedirs(cwd_path, exist_ok=True)
        
        # History tracking
        self.history_data = {"history": self.history, "seeded": True, "chat_id": None}
        
        # Load latest conversation
        self.load_latest_conversation()

    def send_message(self, message):
        """
        Send a message to Claude.
        Returns the response or error message.
        Note: The orchestrator handles ALL blockchain integrity - both user and assistant messages.
        This method should NOT add anything to history.
        """
        try:
            # Get current history for API call (clean for API)
            clean_history = []
            for entry in self.history:
                if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                    clean_entry = {
                        "role": entry["role"],
                        "content": entry["content"]
                    }
                    clean_history.append(clean_entry)
            
            # Add the current user message for API call
            clean_history.append({"role": "user", "content": message})
            
            # Send to Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=clean_history,
                **_temperature_kwarg(self.model, 0.99),
            )
            content, stop_reason = _extract_text(response)
            if not content:
                content = f"(no text content; stop_reason={stop_reason})"

            # DO NOT add anything to history here - orchestrator handles this
            # Just update latest_response for copy functionality
            self.latest_response = content
            self._last_usage = _extract_anthropic_usage(response)
            return content
            
        except Exception as e:
            return f"Error: {e}"

    def create_worker(self, user_input):
        """Create a worker thread for GUI use"""
        return ClaudeWorker(user_input, self.client, self.model, self.history)

    def load_latest_conversation(self):
        """Load the latest conversation if it exists"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                if isinstance(saved_data, dict) and 'history' in saved_data:
                    history = saved_data.get('history', [])
                    if len(history) > 1:  # More than just the initial system message
                        print(f"Loading latest conversation for {self.name}")
                        self.restore_conversation_from_history(saved_data)
                        return True
            except Exception as e:
                print(f"Error loading latest conversation for {self.name}: {e}")
        return False

    def restore_conversation_from_history(self, saved_data):
        """Restore conversation from saved history data"""
        history = saved_data.get('history', [])
        chat_id = saved_data.get('chat_id', None)
        seeded = saved_data.get('seeded', False)
        
        # Clean the conversation history for API compatibility and add missing timestamps
        self.history.clear()
        self.display_history = []
        current_time = datetime.now().isoformat()
        
        for entry in history:
            if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                # Create clean entry for API calls (no timestamps)
                clean_entry = {
                    "role": entry["role"],
                    "content": entry["content"]
                }
                self.history.append(clean_entry)
                
                # Create display entry with timestamp (add if missing)
                display_entry = dict(entry)  # Copy the original entry
                if 'timestamp' not in display_entry or not display_entry['timestamp']:
                    display_entry['timestamp'] = current_time
                    print(f"Added missing timestamp to {display_entry['role']} message for {self.name}")
                
                self.display_history.append(display_entry)
        
        # Generate chat ID if missing
        if not chat_id:
            chat_id = str(uuid.uuid4())
            print(f"Generated new chat ID for {self.name}: {chat_id}")
        
        self.history_data = {
            "history": self.display_history,  # Save full history with timestamps
            "seeded": seeded,
            "chat_id": chat_id
        }
        
        # Save the updated history with timestamps and chat ID
        self.save_conversation()

    def save_conversation(self):
        """Save the current conversation to file"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to write chat log for {self.name}: {e}")

    def reset_conversation(self):
        """Reset the conversation"""
        self.history.clear()
        self.history.append({"role": "user", "content": self.instructions})
        self.display_history = []
        self.history_data = {"history": self.history, "seeded": True, "chat_id": None}
        self.latest_response = ""
        self.save_conversation()
        print(f"Conversation reset for {self.name}")

    def get_info(self):
        """Get agent information"""
        return {
            "name": self.name,
            "model": self.model,
            "chat_id": self.history_data.get("chat_id"),
            "active": self.active,
            "message_count": len(self.history)
        }

    def process_file_upload(self, file_path, status_callback=None):
        """Drag-and-drop file handler. Dispatches by file category:

        - Text (.txt/.md/.csv/.json/.yaml/source code/...): inline contents.
        - Image (jpeg/png/gif/webp): native base64 image content block.
        - PDF: native base64 document content block (preserves layout/images).

        If status_callback is provided, it is called with short progress strings
        (e.g. "Reading file (local)") so a GUI can show a spinner + status text.
        After a successful API call, self._last_usage holds the token counts.
        """
        from file_loader import classify_file, read_text, read_base64

        def _emit(msg):
            if status_callback:
                status_callback(msg)

        try:
            _emit("Classifying file (local)")
            category, mime = classify_file(file_path)
            filename = os.path.basename(file_path)

            if category == "text":
                _emit("Reading text file (local)")
                text = read_text(file_path)
                message = (
                    f"I've uploaded a text file '{filename}'. Contents:\n\n"
                    f"{text}\n\nPlease acknowledge and stand by for questions."
                )
                _emit("Sending to Anthropic Claude (remote)")
                return self.send_message(message)

            if category == "image":
                _emit("Base64-encoding image (local)")
                b64 = read_base64(file_path)
                _emit("Sending image to Anthropic Claude (remote)")
                return self._send_with_blocks([
                    {"type": "image", "source": {
                        "type": "base64", "media_type": mime, "data": b64
                    }},
                    {"type": "text", "text": (
                        f"I've attached an image '{filename}'. "
                        "Please acknowledge and stand by for questions."
                    )},
                ])

            if category == "pdf":
                _emit("Base64-encoding PDF (local)")
                b64 = read_base64(file_path)
                _emit("Sending PDF to Anthropic Claude (remote)")
                return self._send_with_blocks([
                    {"type": "document", "source": {
                        "type": "base64", "media_type": "application/pdf", "data": b64
                    }},
                    {"type": "text", "text": (
                        f"I've attached a PDF '{filename}'. "
                        "Please acknowledge and stand by for questions."
                    )},
                ])

            return f"Unsupported file type: {mime or 'unknown'} ({filename})"
        except Exception as e:
            return f"Error processing file: {e}"

    def _send_with_blocks(self, content_blocks):
        """Send a user message whose content is a list of Anthropic content
        blocks (image, document, text). Mirrors send_message() but takes
        structured content. Does not mutate self.history (orchestrator owns it)."""
        try:
            clean_history = []
            for entry in self.history:
                if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                    clean_history.append({
                        "role": entry["role"],
                        "content": entry["content"],
                    })
            clean_history.append({"role": "user", "content": content_blocks})

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=clean_history,
                **_temperature_kwarg(self.model, 0.99),
            )
            content, stop_reason = _extract_text(response)
            if not content:
                content = f"(no text content; stop_reason={stop_reason})"
            self.latest_response = content
            self._last_usage = _extract_anthropic_usage(response)
            return content
        except Exception as e:
            return f"Error: {e}"

    def get_integrity_display_text(self):
        """Get text to display integrity issues in GUI"""
        if not hasattr(self, 'integrity_valid') or self.integrity_valid:
            return ""
        
        if hasattr(self, 'integrity_issues') and self.integrity_issues:
            warning_text = "⚠️ LOG TAMPERED. TRUST HAS BEEN BREACHED. BLOCKCHAIN FAILS\n"
            warning_text += "Integrity Issues:\n"
            for issue in self.integrity_issues:
                warning_text += f"- {issue}\n"
            return warning_text
        
        return "⚠️ INTEGRITY STATUS UNKNOWN"
