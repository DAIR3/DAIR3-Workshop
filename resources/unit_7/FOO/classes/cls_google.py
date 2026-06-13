"""
clsGoogle.py
Google Gemini Agent class for multi-agent chat system.
Compatible with cls_anthropic.py / cls_openai.py architecture.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""

import os
import json
import sys
import uuid
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from google import genai
from google.genai import types
#from cls_blockchain import IntegrityManager


def _to_gemini_role(role):
    # Gemini uses "model" where Claude/OpenAI use "assistant"
    return "model" if role == "assistant" else "user"


def _extract_gemini_usage(response):
    """Pull token usage off a Gemini generate_content response. Returns None if absent."""
    meta = getattr(response, "usage_metadata", None)
    if meta is None:
        return None
    inp = getattr(meta, "prompt_token_count", None)
    out = getattr(meta, "candidates_token_count", None)
    tot = getattr(meta, "total_token_count", None)
    return {"input": inp, "output": out, "total": tot}


def _history_to_contents(history):
    """Convert internal {role, content} history into Gemini contents."""
    contents = []
    for entry in history:
        if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
            contents.append({
                "role": _to_gemini_role(entry["role"]),
                "parts": [{"text": entry["content"]}],
            })
    return contents


class GoogleWorker(QThread):
    """Worker thread for Gemini API calls to prevent GUI blocking"""
    result_ready = pyqtSignal(str)

    def __init__(self, user_input, client, model, system_instruction, history):
        super().__init__()
        self.user_input = user_input
        self.client = client
        self.model = model
        self.system_instruction = system_instruction
        self.history = history

    def run(self):
        try:
            # Clean history (strip timestamps) for the API call
            clean_history = []
            for entry in self.history:
                if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                    clean_history.append({
                        "role": entry["role"],
                        "content": entry["content"],
                    })

            # Append the current user input
            clean_history.append({"role": "user", "content": self.user_input})

            response = self.client.models.generate_content(
                model=self.model,
                contents=_history_to_contents(clean_history),
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                ),
            )
            content = response.text

            # Record assistant turn with timestamp on the live history
            timestamp = datetime.now().isoformat()
            self.history.append({
                "role": "assistant",
                "content": content,
                "timestamp": timestamp,
            })

            self.result_ready.emit(content)
        except Exception as e:
            self.result_ready.emit(f"Error: {e}")


class GoogleAgent:
    """Google Gemini Agent class compatible with cls_anthropic.py architecture"""

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

        # Gemini takes system_instruction separately from messages, so this is the
        # system prompt rather than the first user turn.
        self.instructions = preamble + instructions + agent_directive

        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) not set. Google agents will not function.")

        self.client = genai.Client(api_key=api_key)

        # Conversation history holds only user/assistant turns
        self.history = []
        self.display_history = []  # For UI display with timestamps

        # Set up history file path using CWD from config
        cwd = config.get("CWD", "/chats")
        if cwd.startswith("/"):
            cwd_path = cwd[1:]  # Remove leading slash for relative path
        else:
            cwd_path = cwd

        self.history_file = os.path.join(cwd_path, f"{self.name}.json")
        print(f"Google Agent {self.name} will use history file: {self.history_file}")

        # Ensure the directory exists
        os.makedirs(cwd_path, exist_ok=True)

        # History tracking
        self.history_data = {"history": self.history, "seeded": True, "chat_id": None}

        # Load latest conversation
        self.load_latest_conversation()

    def send_message(self, message):
        """
        Send a message to Gemini.
        Returns the response or error message.
        Note: The orchestrator handles ALL blockchain integrity - both user and assistant messages.
        This method should NOT add anything to history.
        """
        try:
            # Build clean history for the API call
            clean_history = []
            for entry in self.history:
                if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                    clean_history.append({
                        "role": entry["role"],
                        "content": entry["content"],
                    })
            clean_history.append({"role": "user", "content": message})

            response = self.client.models.generate_content(
                model=self.model,
                contents=_history_to_contents(clean_history),
                config=types.GenerateContentConfig(
                    system_instruction=self.instructions,
                ),
            )
            content = response.text

            # DO NOT add anything to history here - orchestrator handles this
            self.latest_response = content
            self._last_usage = _extract_gemini_usage(response)
            return content

        except Exception as e:
            return f"Error: {e}"

    def create_worker(self, user_input):
        """Create a worker thread for GUI use"""
        return GoogleWorker(user_input, self.client, self.model, self.instructions, self.history)

    def load_latest_conversation(self):
        """Load the latest conversation if it exists"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)

                if isinstance(saved_data, dict) and 'history' in saved_data:
                    history = saved_data.get('history', [])
                    if len(history) > 0:
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
                # Clean entry for API calls (no timestamps)
                clean_entry = {
                    "role": entry["role"],
                    "content": entry["content"],
                }
                self.history.append(clean_entry)

                # Display entry with timestamp (add if missing)
                display_entry = dict(entry)
                if 'timestamp' not in display_entry or not display_entry['timestamp']:
                    display_entry['timestamp'] = current_time
                    print(f"Added missing timestamp to {display_entry['role']} message for {self.name}")

                self.display_history.append(display_entry)

        # Generate chat ID if missing
        if not chat_id:
            chat_id = str(uuid.uuid4())
            print(f"Generated new chat ID for {self.name}: {chat_id}")

        self.history_data = {
            "history": self.display_history,
            "seeded": seeded,
            "chat_id": chat_id,
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
            "message_count": len(self.history),
        }

    def process_file_upload(self, file_path, status_callback=None):
        """Drag-and-drop file handler. Dispatches by file category:

        - Text (.txt/.md/.csv/.json/.yaml/source code/...): inline contents.
        - Image / PDF: upload via the Gemini Files API and reference it in
          the next generate_content call (preserves images and layout).

        If status_callback is provided, it is called with short progress
        strings. After a successful API call, self._last_usage holds the
        token counts.
        """
        import time
        from file_loader import classify_file, read_text

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
                _emit("Sending to Google Gemini (remote)")
                return self.send_message(message)

            if category in ("image", "pdf"):
                _emit("Uploading to Gemini Files API (remote)")
                my_file = self.client.files.upload(file=file_path)
                # Wait for asynchronous processing (PDF/video) to finish.
                if getattr(my_file, "state", None) and str(my_file.state).endswith("PROCESSING"):
                    _emit("Waiting for Gemini to process file (remote)")
                while getattr(my_file, "state", None) and str(my_file.state).endswith("PROCESSING"):
                    time.sleep(1)
                    my_file = self.client.files.get(name=my_file.name)
                _emit("Generating response from Google Gemini (remote)")
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        my_file,
                        (
                            f"I've attached '{filename}'. "
                            "Please acknowledge and stand by for questions."
                        ),
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=self.instructions,
                    ),
                )
                content = response.text
                self.latest_response = content
                self._last_usage = _extract_gemini_usage(response)
                return content

            return f"Unsupported file type: {mime or 'unknown'} ({filename})"
        except Exception as e:
            return f"Error processing file: {e}"

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
