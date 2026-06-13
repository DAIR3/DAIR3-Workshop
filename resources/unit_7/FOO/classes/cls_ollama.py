"""
cls_ollama.py
Ollama Agent class for the multi-agent chat system.

Mirrors the public interface of cls_anthropic.AnthropicAgent and
cls_google.GoogleAgent so the orchestrator and the GUIs can treat all engines
uniformly. Talks to a local (or LAN) Ollama daemon over its HTTP API; no SDK
required beyond ``requests``.

Endpoints used (Ollama >= 0.1.30):
  POST /api/chat        — single-turn or multi-turn chat with messages array.
  POST /api/embed       — embeddings for one or many texts.
  GET  /api/tags        — list locally-installed models (used by ping()).

Multimodal: ``llava``, ``llama3.2-vision`` and friends accept base64 images
via a per-message ``images`` field. Image drop uses that path; text drop
inlines the file contents. PDFs are not handled natively by Ollama, so this
agent extracts plain text from PDFs via PyMuPDF when available and inlines
the result.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
import os
import json
import uuid
from datetime import datetime

import requests


DEFAULT_BASE_URL = "http://localhost:11434"


def _base_url():
    """Resolve the Ollama base URL. Honors OLLAMA_HOST if set; else uses the
    DEFAULT_BASE_URL. providers.json carries the same default but isn't read
    here to keep this class importable without the catalog."""
    return os.environ.get("OLLAMA_HOST", DEFAULT_BASE_URL).rstrip("/")


def _extract_ollama_usage(response_json):
    """Pull a usage dict in the same shape used by the other engine classes."""
    if not isinstance(response_json, dict):
        return None
    inp = response_json.get("prompt_eval_count")
    out = response_json.get("eval_count")
    if inp is None and out is None:
        return None
    total = None
    if inp is not None and out is not None:
        total = inp + out
    return {"input": inp, "output": out, "total": total}


class OllamaAgent:
    """Ollama Agent — local LLM served by a running Ollama daemon."""

    def __init__(self, model, name, instructions, user, config, model_entry=None):
        self.model = model
        self.name = name
        self.user = user
        self.config = config
        self.latest_response = ""
        self.active = True
        self.integrity_issues = []
        self.integrity_valid = True

        preamble = (
            f"Address the user as Dr. {user}.\n\n"
            f" Introduce yourself as {name}, AI assistant.\n\n "
        )
        agent_directive = ""
        if model_entry and "agent_directive" in model_entry:
            agent_directive = (
                f"\n\nAgent specific instructions:\n{model_entry['agent_directive']}\n"
            )
        self.instructions = preamble + instructions + agent_directive

        self.base_url = _base_url()
        self.timeout = int(config.get("ollama_timeout_s", 300))

        self.history = []
        self.display_history = []

        cwd = config.get("CWD", "/chats")
        cwd_path = cwd[1:] if cwd.startswith("/") else cwd
        self.history_file = os.path.join(cwd_path, f"{self.name}.json")
        os.makedirs(cwd_path, exist_ok=True)
        print(f"Ollama Agent {self.name} will use history file: {self.history_file}")

        self.history_data = {"history": self.history, "seeded": True, "chat_id": None}
        self.load_latest_conversation()

    def _post(self, path, payload):
        url = f"{self.base_url}{path}"
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _build_messages(self, user_message_content):
        """Combine system instructions + history + the new user turn into the
        Ollama /api/chat ``messages`` array. ``user_message_content`` may be
        a plain string OR a dict with explicit ``content``/``images`` keys."""
        messages = [{"role": "system", "content": self.instructions}]
        for entry in self.history:
            if isinstance(entry, dict) and "role" in entry and "content" in entry:
                messages.append({"role": entry["role"], "content": entry["content"]})
        if isinstance(user_message_content, dict):
            messages.append({"role": "user", **user_message_content})
        else:
            messages.append({"role": "user", "content": user_message_content})
        return messages

    def send_message(self, message):
        """Send a text message. The orchestrator owns history, so this does
        not mutate self.history (matches the other engine classes)."""
        try:
            payload = {
                "model": self.model,
                "messages": self._build_messages(message),
                "stream": False,
            }
            data = self._post("/api/chat", payload)
            content = (data.get("message") or {}).get("content", "")
            self.latest_response = content
            self._last_usage = _extract_ollama_usage(data)
            return content
        except requests.exceptions.ConnectionError:
            return (
                f"Error: cannot reach Ollama at {self.base_url}. "
                "Is the daemon running? (`ollama serve`)"
            )
        except Exception as e:
            return f"Error: {e}"

    def process_file_upload(self, file_path, status_callback=None):
        """Drag-and-drop handler. Text in-lines; images send via Ollama's
        ``images`` field (multimodal models only); PDFs are text-extracted
        when PyMuPDF is available, else rejected with a clear message."""
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
                msg = (
                    f"I've uploaded a text file '{filename}'. Contents:\n\n"
                    f"{text}\n\nPlease acknowledge and stand by for questions."
                )
                _emit(f"Sending to Ollama ({self.model}, local)")
                return self.send_message(msg)

            if category == "image":
                _emit("Base64-encoding image (local)")
                b64 = read_base64(file_path)
                _emit(f"Sending image to Ollama ({self.model}, local)")
                payload = {
                    "model": self.model,
                    "messages": self._build_messages({
                        "content": (
                            f"I've attached an image '{filename}'. "
                            "Please acknowledge and stand by for questions."
                        ),
                        "images": [b64],
                    }),
                    "stream": False,
                }
                data = self._post("/api/chat", payload)
                content = (data.get("message") or {}).get("content", "")
                self.latest_response = content
                self._last_usage = _extract_ollama_usage(data)
                return content

            if category == "pdf":
                _emit("Extracting text from PDF (local)")
                try:
                    import fitz  # PyMuPDF
                except ImportError:
                    return (
                        "Ollama agents cannot natively read PDFs. Install PyMuPDF "
                        "(`pip install PyMuPDF`) so the text can be extracted "
                        "locally before sending."
                    )
                doc = fitz.open(file_path)
                text = "\n\n".join(page.get_text() for page in doc)
                doc.close()
                msg = (
                    f"I've uploaded a PDF '{filename}'. Extracted text:\n\n"
                    f"{text}\n\nPlease acknowledge and stand by for questions."
                )
                _emit(f"Sending to Ollama ({self.model}, local)")
                return self.send_message(msg)

            return f"Unsupported file type: {mime or 'unknown'} ({filename})"
        except Exception as e:
            return f"Error processing file: {e}"

    def load_latest_conversation(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                if isinstance(saved, dict) and saved.get("history"):
                    self.restore_conversation_from_history(saved)
                    return True
            except Exception as e:
                print(f"Error loading latest conversation for {self.name}: {e}")
        return False

    def restore_conversation_from_history(self, saved_data):
        history = saved_data.get("history", [])
        chat_id = saved_data.get("chat_id")
        seeded = saved_data.get("seeded", False)
        now = datetime.now().isoformat()

        self.history.clear()
        self.display_history = []
        for entry in history:
            if isinstance(entry, dict) and "role" in entry and "content" in entry:
                self.history.append({"role": entry["role"], "content": entry["content"]})
                display = dict(entry)
                display.setdefault("timestamp", now)
                self.display_history.append(display)

        if not chat_id:
            chat_id = str(uuid.uuid4())
        self.history_data = {
            "history": self.display_history,
            "seeded": seeded,
            "chat_id": chat_id,
        }
        self.save_conversation()

    def save_conversation(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to write chat log for {self.name}: {e}")

    def reset_conversation(self):
        self.history.clear()
        self.display_history = []
        self.history_data = {"history": self.history, "seeded": True, "chat_id": None}
        self.latest_response = ""
        self.save_conversation()
        print(f"Conversation reset for {self.name}")

    def get_info(self):
        return {
            "name": self.name,
            "model": self.model,
            "chat_id": self.history_data.get("chat_id"),
            "active": self.active,
            "message_count": len(self.history),
        }

    def get_integrity_display_text(self):
        if not hasattr(self, "integrity_valid") or self.integrity_valid:
            return ""
        if hasattr(self, "integrity_issues") and self.integrity_issues:
            t = "WARNING: LOG TAMPERED. TRUST HAS BEEN BREACHED. BLOCKCHAIN FAILS\n"
            t += "Integrity Issues:\n"
            for issue in self.integrity_issues:
                t += f"- {issue}\n"
            return t
        return "WARNING: INTEGRITY STATUS UNKNOWN"

    @classmethod
    def ping(cls):
        """Quick liveness check. Returns the list of locally-installed model
        names, or raises if the daemon isn't reachable."""
        url = f"{_base_url()}/api/tags"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return [m.get("name") for m in r.json().get("models", [])]


def embed_with_ollama(texts, model="nomic-embed-text"):
    """One-shot embedding helper used by cls_rag when the user picks the
    local embedding backend. Returns a list of float vectors in the same
    order as ``texts``."""
    if isinstance(texts, str):
        texts = [texts]
    r = requests.post(
        f"{_base_url()}/api/embed",
        json={"model": model, "input": texts},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("embeddings") or [data.get("embedding")]
