"""
single_agent_gui.py
Generic single-agent chat window used by agentClaude.py, agentGPTGUI.py and
agentGoogleGUI.py. One implementation; the three entry-point scripts differ
only in which provider they preselect in the Provider dropdown.

Layout (header row, left to right):
    Provider:  [combo]   Model: [combo]   Role: [combo]   [Drop->Context]
    [RAG]   [-]  [+]

The Provider+Model selectors live behind ``ProviderModelSelector`` in
widgets_common; the file drop goes through ``cls_file_router.route_drop``;
the RAG configuration sits behind the [RAG] gear button.

Dropped files honor the user's drop-mode selection. Plain chat messages are
RAG-augmented automatically when the agent's KnowledgeBase has indexed
content (top-k retrieved, citations rendered above the answer).

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
import os
import sys
import io
import json
import glob
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QComboBox, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont

from md_widget import MarkdownTextEdit
from md_loader import load_persona
from file_upload_worker import FileUploadWorker, format_usage
from cls_provider_catalog import engine_class_for, find_model, find_provider
from cls_rag import KnowledgeBase, build_rag_prompt, render_citations
from cls_file_router import RouteDecision, route_drop, extract_paths_from_drop
from widgets_common import ProviderModelSelector, RAGSettingsDialog


# Force UTF-8 stdout/stderr so non-ASCII tracebacks render.
if sys.stdout and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class ChatWorker(QThread):
    """Runs the agent's send_message on a background thread. Result includes
    the response text and the retrieved chunks (so the GUI can render
    citations even on the worker's return)."""
    result_ready = pyqtSignal(str, list)

    def __init__(self, agent, message, chunks):
        super().__init__()
        self.agent = agent
        self.message = message
        self.chunks = chunks

    def run(self):
        try:
            text = self.agent.send_message(self.message)
            self.result_ready.emit(text, self.chunks)
        except Exception as e:
            self.result_ready.emit(f"Error: {e}", [])


class SingleAgentGUI(QWidget):
    """One window, one agent. The agent can be swapped at runtime via the
    Provider + Model dropdowns; conversation resets on swap so context
    doesn't leak between models."""

    DEFAULT_WINDOW_TITLE = "FOO - Single-Agent Chat"

    def __init__(self, role_md_path="general.md", preferred_provider=None, window_title=None):
        super().__init__()

        with open("config.json", "r", encoding="utf-8") as f:
            self.config_data = json.load(f)
        self.config = self.config_data["CONFIG"]

        self.user = self.config["user"]
        self.name = self.config["name"]
        self.common_md = self.config.get("common_md", "common.md")
        self.role_md = role_md_path
        self.font_size = int(self.config.get("fontsize", 12))
        self.loaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.latest_response = ""

        # Resolve initial provider + model from CLI override or config defaults.
        self.provider_code = (
            preferred_provider
            or self.config.get("default_provider")
            or "openai"
        )
        self.model_code = self._default_model_for(self.provider_code)

        self.instructions = load_persona(self.common_md, self.role_md, {
            "user": self.user,
            "name": self.name,
        })

        # Per-window drop-mode decision (hybrid: ask once, toggle thereafter).
        self.route_decision = RouteDecision()

        # Per-agent persistent knowledge base. Backend is None until the user
        # picks one through the RAG settings dialog or via the first drop.
        self.kb = KnowledgeBase(self.name)
        self.rag_top_k = int(self.config.get("rag_top_k", 4))

        # Build the underlying agent. May fail if the API key for the
        # preferred provider isn't set; in that case we fall back to the
        # first provider that does have a key.
        self.agent = self._build_agent()

        self.init_gui(window_title or self.DEFAULT_WINDOW_TITLE)

    # --- provider/model plumbing -------------------------------------------

    def _default_model_for(self, provider_code):
        """Pick a sensible default model for a provider from config.json's
        provider-specific knobs."""
        if provider_code == "anthropic":
            return self.config.get("claude_model", "claude-sonnet-4-6")
        if provider_code == "gemini":
            return self.config.get("google_model", "gemini-2.5-flash")
        if provider_code == "ollama":
            return self.config.get("ollama_model", "llama3.1")
        return self.config.get("default_model") or self.config.get("model", "gpt-5.5")

    def _build_agent(self):
        AgentClass = engine_class_for(self.provider_code)
        return AgentClass(
            model=self.model_code,
            name=self.name,
            instructions=self.instructions,
            user=self.user,
            config=self.config,
        )

    def on_selection_changed(self, provider_code, model_code):
        if provider_code == self.provider_code and model_code == self.model_code:
            return
        self.provider_code = provider_code
        self.model_code = model_code
        try:
            self.agent = self._build_agent()
        except Exception as e:
            self.text_area.append(f"**Failed to switch to {provider_code}/{model_code}:** {e}")
            return
        self.text_area.clear()
        self._display_session_header()
        self.text_area.append(f"**Switched to:** {provider_code} / `{model_code}` - conversation reset.")
        self.text_area.append("---")

    # --- GUI ----------------------------------------------------------------

    def init_gui(self, window_title):
        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, 820, 560)
        self.setAcceptDrops(True)

        layout = QVBoxLayout()

        # --- Header row 1: Provider + Model selector ---
        self.selector = ProviderModelSelector()
        self.selector.set_selection(self.provider_code, self.model_code)
        # The set_selection above will have ALSO emitted selection_changed
        # if the requested model wasn't the catalog's first entry. Connect
        # AFTER set_selection so the initial seed doesn't trigger a rebuild.
        self.selector.selection_changed.connect(self.on_selection_changed)
        layout.addWidget(self.selector)

        # --- Header row 2: Role + drop-mode toggle + RAG gear + font controls ---
        header2 = QHBoxLayout()
        header2.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(self._discover_md_files())
        if self.role_md in [self.role_combo.itemText(i) for i in range(self.role_combo.count())]:
            self.role_combo.setCurrentText(self.role_md)
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        header2.addWidget(self.role_combo, 1)

        self.drop_mode_btn = self.route_decision.create_toggle_button(self)
        header2.addWidget(self.drop_mode_btn)

        # Gear glyph U+2699 matches the "gear icon" referenced in error messages
        # (cls_file_router) and in the slides.
        self.rag_btn = QPushButton("⚙ RAG")
        self.rag_btn.setFixedWidth(75)
        self.rag_btn.setToolTip("RAG settings: embedding backend, top-k, consent, re-index")
        self.rag_btn.clicked.connect(self.open_rag_settings)
        header2.addWidget(self.rag_btn)

        header2.addStretch()
        self.font_dec_btn = QPushButton("-")
        self.font_dec_btn.setFixedWidth(32)
        self.font_dec_btn.clicked.connect(lambda: self.apply_font_size(self.font_size - 1))
        self.font_inc_btn = QPushButton("+")
        self.font_inc_btn.setFixedWidth(32)
        self.font_inc_btn.clicked.connect(lambda: self.apply_font_size(self.font_size + 1))
        header2.addWidget(self.font_dec_btn)
        header2.addWidget(self.font_inc_btn)

        layout.addLayout(header2)

        # Status row for uploads / RAG ingestion.
        self.status_row = QWidget()
        status_layout = QHBoxLayout(self.status_row)
        status_layout.setContentsMargins(0, 0, 0, 0)
        self.upload_progress = QProgressBar()
        self.upload_progress.setRange(0, 0)
        self.upload_progress.setFixedWidth(140)
        self.upload_progress.setTextVisible(False)
        self.upload_status_label = QLabel("")
        status_layout.addWidget(self.upload_progress)
        status_layout.addWidget(self.upload_status_label, 1)
        self.status_row.setVisible(False)
        layout.addWidget(self.status_row)
        self.upload_worker = None

        self.text_area = MarkdownTextEdit(self)
        layout.addWidget(self.text_area)

        self._display_session_header()

        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Type your message and press Enter")
        layout.addWidget(self.user_input)

        self.copy_button = QPushButton("Copy Latest Answer")
        self.copy_button.clicked.connect(self.copy_latest_answer)
        layout.addWidget(self.copy_button)

        self.user_input.returnPressed.connect(self.on_enter_pressed)

        self.setLayout(layout)
        self.apply_font_size(self.font_size)

    def _display_session_header(self):
        prov = find_provider(self.provider_code)
        provider_label = prov.get("ds_display_name", self.provider_code) if prov else self.provider_code
        self.text_area.append(
            f"**Model:** `{self.model_code}` ({provider_label}) - **Loaded:** {self.loaded_at}"
        )
        self.text_area.append(f"**Agent:** {self.name} - **Role:** {self.role_md}")
        # Use manifest-only counters at startup; touching Chroma here can
        # crash the host process on some Windows setups before the window
        # is shown. See KnowledgeBase.manifest_chunk_count for the rationale.
        self.text_area.append(
            f"_{self.kb.backend_label()}, "
            f"sources: {self.kb.manifest_source_count()}, "
            f"chunks: {self.kb.manifest_chunk_count()}_"
        )
        self.text_area.append("---")

    def _discover_md_files(self):
        here = os.path.dirname(os.path.abspath(__file__))
        files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(here, "*.md")))
        return [f for f in files if f != "common.md"]

    def apply_font_size(self, size):
        self.font_size = max(6, min(48, int(size)))
        font = QFont()
        font.setPointSize(self.font_size)
        for child in self.findChildren(QWidget):
            child.setFont(font)
        self.text_area.document().setDefaultFont(font)
        self.text_area.rerender()

    def on_role_changed(self, role):
        if not role or role == self.role_md:
            return
        self.role_md = role
        self.instructions = load_persona(self.common_md, self.role_md, {
            "user": self.user,
            "name": self.name,
        })
        # Rebuild the agent so the new system prompt takes effect.
        try:
            self.agent = self._build_agent()
        except Exception as e:
            self.text_area.append(f"**Failed to reload agent with role `{role}`:** {e}")
            return
        self.text_area.clear()
        self._display_session_header()
        self.text_area.append(f"**Role changed to:** `{role}` - conversation reset.")
        self.text_area.append("---")

    # --- RAG settings -------------------------------------------------------

    def open_rag_settings(self):
        dlg = RAGSettingsDialog(self.name, self.kb, default_top_k=self.rag_top_k, parent=self)
        if dlg.exec_():
            self.rag_top_k = dlg.chosen_top_k()
            new_backend = dlg.chosen_backend()
            if new_backend and new_backend != self.kb.backend:
                try:
                    self.kb.set_backend(new_backend)
                    self.text_area.append(f"_RAG backend set to {new_backend}; index was wiped (dimensions differ)._")
                except Exception as e:
                    self.text_area.append(f"**Failed to set RAG backend:** {e}")
            self.text_area.append(f"_{self.kb.backend_label()}_")

    # --- file drop ----------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        paths = extract_paths_from_drop(event)
        if not paths:
            return
        # If user picks RAG but hasn't set a backend yet, ask via the gear
        # dialog first. The router will fall back to context if still unset.
        if self.route_decision.mode is None:
            # ensure_choice runs inside route_drop, but we want to provoke
            # the RAG dialog if the user picks RAG and no backend exists.
            pass
        route_drop(
            decision=self.route_decision,
            file_paths=paths,
            agent=self.agent,
            knowledge_base=self.kb,
            on_context=self._upload_via_context,
            on_rag_status=self._rag_log,
            parent_widget=self,
            default_backend=self.config.get("rag_default_backend", "openai"),
        )

    def _rag_log(self, message):
        self.text_area.append(f"_{message}_")

    def _upload_via_context(self, file_path):
        if self.upload_worker is not None and self.upload_worker.isRunning():
            self.text_area.append(f"_(Already uploading; ignored drop of `{file_path}`)_")
            return
        filename = os.path.basename(file_path)
        agent = self.agent

        def do_upload(status_cb):
            try:
                response = agent.process_file_upload(file_path, status_callback=status_cb)
            except TypeError:
                response = agent.process_file_upload(file_path)
            usage = getattr(agent, "_last_usage", None)
            return response, usage

        self.text_area.append(f"**Processing file:** `{filename}`")
        self.text_area.append(">>>>>>>>>>>>>>>>>>>>>>>>>>")
        self._show_upload_status("Starting upload...")

        self.upload_worker = FileUploadWorker(do_upload)
        self.upload_worker.status.connect(self._on_upload_status)
        self.upload_worker.finished_ok.connect(self._on_upload_finished)
        self.upload_worker.finished_err.connect(self._on_upload_error)
        self.upload_worker.start()

    def _show_upload_status(self, msg):
        self.upload_status_label.setText(msg)
        self.status_row.setVisible(True)

    def _hide_upload_status(self):
        self.status_row.setVisible(False)
        self.upload_status_label.setText("")

    def _on_upload_status(self, msg):
        self._show_upload_status(msg)
        self.text_area.append(f"_...{msg}_")

    def _on_upload_finished(self, response, usage):
        usage_str = format_usage(usage) if usage else ""
        if usage_str:
            self.text_area.append(f"_Done - tokens: {usage_str}_")
        else:
            self.text_area.append("_Done._")
        self._hide_upload_status()
        self.latest_response = response
        self.text_area.append(f"{self.name}: {response}")
        self.text_area.append("---")

    def _on_upload_error(self, msg):
        self._hide_upload_status()
        self.text_area.append(f"**Upload error:** {msg}")
        self.text_area.append("---")

    # --- chat ---------------------------------------------------------------

    def on_enter_pressed(self):
        text = self.user_input.text().strip()
        if text:
            self.process_user_input(text)
        self.user_input.clear()

    def process_user_input(self, user_input):
        self.text_area.append(f"{self.user}: {user_input}")
        self.text_area.append(">>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.user_input.setEnabled(False)

        # If the knowledge base has any indexed content, retrieve and assemble
        # a RAG-augmented prompt. Otherwise send the message as-is.
        # NOTE: manifest_chunk_count is pure file I/O; count() would open
        # Chroma which can crash the process on Windows during ONNX DLL load.
        chunks = []
        outgoing = user_input
        if self.kb.backend and self.kb.manifest_chunk_count() > 0:
            try:
                chunks = self.kb.query(user_input, top_k=self.rag_top_k)
            except Exception as e:
                self.text_area.append(f"_(RAG query failed: {e}. Sending without retrieval.)_")
                chunks = []
            if chunks:
                outgoing = build_rag_prompt(user_input, chunks)

        self.worker = ChatWorker(self.agent, outgoing, chunks)
        self.worker.result_ready.connect(self.display_results)
        self.worker.start()

    def display_results(self, response, chunks):
        self.latest_response = response
        if chunks:
            self.text_area.append(render_citations(chunks))
        self.text_area.append(f"{self.name}: {response}")
        self.text_area.append("---")
        self.user_input.setEnabled(True)

    def copy_latest_answer(self):
        QApplication.clipboard().setText(self.latest_response or "")
        self.text_area.append("Latest answer copied to clipboard.")


def launch(preferred_provider=None, window_title=None, role_md="general.md"):
    """Convenience entry point used by the three single-agent CLI scripts."""
    app = QApplication([])
    win = SingleAgentGUI(
        role_md_path=role_md,
        preferred_provider=preferred_provider,
        window_title=window_title,
    )
    win.show()
    app.exec_()
