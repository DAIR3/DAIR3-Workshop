"""
clsOpenAI.py
OpenAI Agent class for multi-agent chat system, backed by the Responses API.
Compatible with Helper.py command-line interface architecture.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""

import os
import uuid
import openai
import json
import sys
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
# from cls_blockchain import IntegrityManager


def _extract_openai_usage(response):
    """Pull token usage off an OpenAI Responses API response. Returns None if absent."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    inp = getattr(usage, "input_tokens", None)
    out = getattr(usage, "output_tokens", None)
    tot = getattr(usage, "total_tokens", None)
    return {"input": inp, "output": out, "total": tot}


class _ConversationHandle:
    # Stable conversation identifier used as chat_id in history files;
    # replaces the removed Assistants API thread object.
    def __init__(self, conversation_id):
        self.id = conversation_id


class OpenAIWorker(QThread):
    """Worker thread for OpenAI API calls to prevent GUI blocking"""
    result_ready = pyqtSignal(str)

    def __init__(self, user_input, agent):
        super().__init__()
        self.user_input = user_input
        self.agent = agent  # owns client, model, instructions, conversation state

    def run(self):
        if self.agent.is_busy:
            self.result_ready.emit(f"Agent {self.agent.name} is busy processing a previous request. Please wait.")
            return

        try:
            self.agent.is_busy = True
            response_text = self.agent._invoke_response(self.user_input)
            self.result_ready.emit(response_text)
        except Exception as e:
            self.result_ready.emit(f"Error: {e}")
        finally:
            self.agent.is_busy = False


class OpenAIAgent:
    """OpenAI Agent class compatible with Helper.py architecture"""

    def __init__(self, model, name, instructions, user, config, model_entry=None):
        self.model = model
        self.name = name
        self.user = user
        self.config = config
        self.latest_response = ""
        self.active = True
        self.is_busy = False
        self.integrity_issues = []
        self.integrity_valid = True

        # Build instructions with preamble (compatible with Helper.py style)
        preamble = f"Please address the user as Dr. {user}.\n\n Introduce yourself as {name}, AI assistant.\n\n "

        # Add agent-specific directive if available
        agent_directive = ""
        if model_entry and "agent_directive" in model_entry:
            agent_directive = f"\n\nAgent specific instructions:\n{model_entry['agent_directive']}\n"

        self.instructions = preamble + instructions + agent_directive

        # Initialize OpenAI client
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("API key is not set. Please set the OPENAI_API_KEY environment variable.")

        self.client = openai.OpenAI()

        # Stable conversation identifier (persisted as chat_id in history files).
        # The Responses API has no thread; we keep this id only for history bookkeeping.
        self.thread = _ConversationHandle(f"conv_{uuid.uuid4().hex}")

        # Responses API continuity pointer; updated after every successful turn.
        self.previous_response_id = None

        # Vector store backing the file_search tool; created lazily on first upload.
        self.vector_store_id = None

        # Set up history file path using CWD from config
        cwd = config.get("CWD", "/chats")
        if cwd.startswith("/"):
            cwd_path = cwd[1:]  # Remove leading slash for relative path
        else:
            cwd_path = cwd

        self.history_file = os.path.join(cwd_path, f"{self.name}.json")
        print(f"OpenAI Agent {self.name} will use history file: {self.history_file}")

        # Ensure the directory exists
        os.makedirs(cwd_path, exist_ok=True)

        # History tracking
        self.history_data = {"history": [], "seeded": True, "chat_id": None}

        # Load latest conversation
        self.load_latest_conversation()

    def _tools(self):
        if self.vector_store_id:
            return [{"type": "file_search", "vector_store_ids": [self.vector_store_id]}]
        return None

    def _invoke_response(self, message):
        """Call the Responses API and return the assistant text. Updates conversation state."""
        kwargs = {
            "model": self.model,
            "instructions": self.instructions,
            "input": message,
        }
        if self.previous_response_id:
            kwargs["previous_response_id"] = self.previous_response_id
        tools = self._tools()
        if tools:
            kwargs["tools"] = tools

        response = self.client.responses.create(**kwargs)
        self.previous_response_id = response.id
        text = response.output_text
        self.latest_response = text
        self._last_usage = _extract_openai_usage(response)
        return text

    def upload_file(self, file_path):
        """
        Upload a file to OpenAI and register it in a vector store so file_search can read it.
        Returns the file ID if successful; otherwise returns None.
        """
        try:
            with open(file_path, 'rb') as file_data:
                file_object = self.client.files.create(
                    file=file_data,
                    purpose='assistants'
                )
            print(f"File uploaded successfully: ID {file_object.id}")

            if self.vector_store_id is None:
                vs = self.client.vector_stores.create(name=f"{self.name}_files")
                self.vector_store_id = vs.id

            self.client.vector_stores.files.create_and_poll(
                vector_store_id=self.vector_store_id,
                file_id=file_object.id,
            )
            return file_object.id
        except Exception as e:
            print(f"Failed to upload file: {e}")
            return None

    def send_message(self, message):
        """
        Send a message to the OpenAI agent.
        Returns the response or error message.
        Note: The orchestrator handles ALL blockchain integrity.
        This method should NOT add anything to history.
        """
        if self.is_busy:
            return f"Agent {self.name} is busy processing a previous request. Please wait."

        try:
            self.is_busy = True
            return self._invoke_response(message)
        except Exception as e:
            return f"Error: {e}"
        finally:
            self.is_busy = False

    def process_file_upload(self, file_path, status_callback=None):
        """Drag-and-drop file handler. Dispatches by file category:

        - Text (.txt/.md/.csv/.json/.yaml/source code/...): inline contents.
        - Image: base64 input_image content block in the next Responses call.
        - PDF: base64 input_file content block in the next Responses call
          (preserves layout and embedded images).

        If status_callback is provided, it is called with short progress
        strings. After a successful API call, self._last_usage holds the
        token counts.
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
                _emit("Sending to OpenAI Responses API (remote)")
                return self.send_message(message)

            if category == "image":
                _emit("Base64-encoding image (local)")
                b64 = read_base64(file_path)
                _emit("Sending image to OpenAI Responses API (remote)")
                return self._invoke_with_content([
                    {"type": "input_image",
                     "image_url": f"data:{mime};base64,{b64}"},
                    {"type": "input_text", "text": (
                        f"I've attached an image '{filename}'. "
                        "Please acknowledge and stand by for questions."
                    )},
                ])

            if category == "pdf":
                _emit("Base64-encoding PDF (local)")
                b64 = read_base64(file_path)
                _emit("Sending PDF to OpenAI Responses API (remote)")
                return self._invoke_with_content([
                    {"type": "input_file",
                     "filename": filename,
                     "file_data": f"data:application/pdf;base64,{b64}"},
                    {"type": "input_text", "text": (
                        f"I've attached a PDF '{filename}'. "
                        "Please acknowledge and stand by for questions."
                    )},
                ])

            return f"Unsupported file type: {mime or 'unknown'} ({filename})"
        except Exception as e:
            return f"Error processing file: {e}"

    def _invoke_with_content(self, content_blocks):
        """Send a Responses API call whose user message has structured content
        (input_text / input_image / input_file). Updates previous_response_id."""
        if self.is_busy:
            return f"Agent {self.name} is busy processing a previous request. Please wait."
        try:
            self.is_busy = True
            kwargs = {
                "model": self.model,
                "instructions": self.instructions,
                "input": [{"role": "user", "content": content_blocks}],
            }
            if self.previous_response_id:
                kwargs["previous_response_id"] = self.previous_response_id
            tools = self._tools()
            if tools:
                kwargs["tools"] = tools
            response = self.client.responses.create(**kwargs)
            self.previous_response_id = response.id
            text = response.output_text
            self.latest_response = text
            self._last_usage = _extract_openai_usage(response)
            return text
        except Exception as e:
            return f"Error: {e}"
        finally:
            self.is_busy = False

    def create_worker(self, user_input):
        """Create a worker thread for GUI use"""
        return OpenAIWorker(user_input, self)

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

        # Update history data
        self.history_data = {
            "history": history,
            "seeded": seeded,
            "chat_id": chat_id,
            "openai_thread_id": self.thread.id
        }

        # Process history entries to add missing timestamps and fix thread ID
        current_time = datetime.now().isoformat()
        updated_history = []

        for entry in history:
            if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                # Add timestamp if missing
                if 'timestamp' not in entry or not entry['timestamp']:
                    entry['timestamp'] = current_time
                    print(f"Added missing timestamp to {entry['role']} message for {self.name}")

                updated_history.append(entry)

        # Update the history with fixed entries
        self.history_data["history"] = updated_history

        # Assign current conversation ID if missing or different
        if not chat_id or chat_id != self.thread.id:
            self.history_data["chat_id"] = self.thread.id
            print(f"Updated thread ID for {self.name}: {self.thread.id}")

        # Replay prior conversation as a priming turn so previous_response_id is set
        if len(updated_history) > 0:
            context_message = "We will continue the following conversation we started earlier:\n\n"
            for entry in updated_history:
                role = entry.get('role', 'unknown')
                content = entry.get('content', '')
                timestamp = entry.get('timestamp', '')

                if role == 'user':
                    context_message += f"User ({timestamp}): {content}\n"
                elif role == 'assistant':
                    context_message += f"Assistant ({timestamp}): {content}\n"

            context_message += "\nPlease continue from where we left off."

            try:
                self._invoke_response(context_message)
            except Exception as e:
                print(f"Error sending context to OpenAI for {self.name}: {e}")

        # Save the updated history with timestamps and conversation ID
        self.save_conversation()

    def save_conversation(self):
        """Save the current conversation to file"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to write chat log for {self.name}: {e}")

    def reset_conversation(self):
        """Reset the conversation and start a fresh handle"""
        try:
            self.is_busy = True
            self.thread = _ConversationHandle(f"conv_{uuid.uuid4().hex}")
            self.previous_response_id = None
            self.history_data = {"history": [], "seeded": True, "chat_id": None}
            self.latest_response = ""
            self.save_conversation()
            print(f"Conversation reset for {self.name}")
        except Exception as e:
            print(f"Error resetting conversation for {self.name}: {e}")
        finally:
            self.is_busy = False

    def get_info(self):
        """Get agent information (compatible with Helper.py info display)"""
        return {
            "name": self.name,
            "model": self.model,
            "assistant_id": None,
            "thread_id": self.thread.id,
            "active": self.active
        }

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
