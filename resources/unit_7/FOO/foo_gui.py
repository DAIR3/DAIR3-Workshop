"""
FOOGUI.py
GUI interface for the multi-agent chat system.
Compatible with HelperGUI.py and ClaudeGUI.py architecture.

By Juan B. Gutiérrez, Professor of Mathematics 
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""

import os
import sys
import json
import glob
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QLineEdit, QVBoxLayout,
    QPushButton, QTabWidget, QHBoxLayout, QCheckBox, QLabel, QScrollArea,
    QFileDialog, QMessageBox, QComboBox, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal, QEvent, Qt, QUrl, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont

from cls_foo import MultiAgentOrchestrator
from md_widget import MarkdownTextEdit
from md_loader import load_persona
from file_upload_worker import FileUploadWorker, format_usage
from cls_provider_catalog import engine_class_for, find_provider
from cls_rag import KnowledgeBase, build_rag_prompt, render_citations
from cls_file_router import RouteDecision, route_drop, extract_paths_from_drop
from widgets_common import ProviderModelSelector, RAGSettingsDialog


class BroadcastTextEdit(QTextEdit):
    """Custom QTextEdit that reliably handles Enter key for broadcasting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        
    def keyPressEvent(self, event):
        """Override keyPressEvent for direct Enter key handling"""
        # Handle all possible Enter key variations
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) or event.text() == '\r':
            # Check if Shift is held (for multiline input)
            if event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter: insert newline normally
                super().keyPressEvent(event)
            else:
                # Plain Enter: broadcast message
                text = self.toPlainText().strip()
                if text:
                    if self.parent_widget and hasattr(self.parent_widget, 'broadcast_message_text'):
                        self.parent_widget.broadcast_message_text(text)
                    self.clear()
                # Don't call super() to prevent newline insertion
                return
        
        # For all other keys, use default behavior
        super().keyPressEvent(event)


class AgentTextEdit(QTextEdit):
    """Custom QTextEdit for individual agent inputs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.agent_tab = parent  # Store reference to the AgentTab
        
    def keyPressEvent(self, event):
        """Handle Enter key for individual agent inputs"""
        # Handle all possible Enter key variations
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) or event.text() == '\r':
            # Check if Shift is held (for multiline input)
            if event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter: insert newline normally
                super().keyPressEvent(event)
            else:
                # Plain Enter: send message
                text = self.toPlainText().strip()
                if text and self.agent_tab:
                    self.setEnabled(False)
                    self.agent_tab.handle_input(text)
                    self.clear()
                return
        
        super().keyPressEvent(event)


class VulnerabilityWorker(QThread):
    """Worker thread for vulnerability analysis"""
    result_ready = pyqtSignal(dict, dict)  # Returns (requests_dict, responses_dict)
    
    def __init__(self, orchestrator, source_agent_name):
        super().__init__()
        self.orchestrator = orchestrator
        self.source_agent_name = source_agent_name
    
    def run(self):
        try:
            # Get the source agent's latest response for the request message
            source_agent = None
            for agent in self.orchestrator.agents:
                if agent.name == self.source_agent_name:
                    source_agent = agent
                    break
            
            if not source_agent or not source_agent.latest_response:
                self.result_ready.emit({}, {"Error": "No response found for source agent"})
                return
            
            # Build the request message that will be sent
            request_message = f"Agent {self.source_agent_name} answered the same question as follows, find flaws: {source_agent.latest_response}"
            
            # Send to other agents and get responses
            responses = self.orchestrator.send_vulnerability_analysis(self.source_agent_name)
            
            # Create requests dict for UI display
            requests = {}
            for agent_name in responses.keys():
                requests[agent_name] = request_message
            
            self.result_ready.emit(requests, responses)
        except Exception as e:
            self.result_ready.emit({}, {"Error": str(e)})


class JudgmentWorker(QThread):
    """Worker thread for judgment analysis"""
    result_ready = pyqtSignal(dict, dict)  # Returns (requests_dict, responses_dict)
    
    def __init__(self, orchestrator, source_agent_name):
        super().__init__()
        self.orchestrator = orchestrator
        self.source_agent_name = source_agent_name
    
    def run(self):
        try:
            # Call orchestrator to send judgment analysis
            # Now returns both responses and the actual messages sent
            responses, messages = self.orchestrator.send_judgment_analysis(self.source_agent_name)
            
            if not responses:
                self.result_ready.emit({}, {"Error": "No responses from harmonizer agents"})
                return
            
            # Use the actual messages that were sent (from orchestrator)
            # This ensures UI shows exactly what each agent received
            self.result_ready.emit(messages, responses)
            
        except Exception as e:
            self.result_ready.emit({}, {"Error": str(e)})

class ReflectionWorker(QThread):
    """Worker thread for reflection analysis"""
    result_ready = pyqtSignal(str, str)  # Returns (request_message, response)
    
    def __init__(self, orchestrator, target_agent_name):
        super().__init__()
        self.orchestrator = orchestrator
        self.target_agent_name = target_agent_name
    
    def run(self):
        try:
            # Collect reflections from harmonizer agents to build the request message
            reflections = []
            for agent in self.orchestrator.get_harmonizer_agents():
                if agent.latest_response and agent.latest_response.strip():
                    reflections.append(agent.latest_response.strip())
            
            if not reflections:
                self.result_ready.emit("", "No reflections found from harmonizer agents")
                return
            
            composite = "---".join(reflections)
            request_message = (
                "Judgment of your response has resulted in the observations that follow. "
                "Regenerate your version of the text under review taking into account the consensus of these observations. If you object to an observation, explain why. \n \n " + composite
            )
            
            response = self.orchestrator.send_reflection_analysis(self.target_agent_name)
            
            self.result_ready.emit(request_message, response if response else "No reflection response received")
        except Exception as e:
            self.result_ready.emit("", f"Error: {e}")


class AgentWorker(QThread):
    """Generic worker thread for agent interactions"""
    result_ready = pyqtSignal(str)
    
    def __init__(self, agent, message):
        super().__init__()
        self.agent = agent
        self.message = message
    
    def run(self):
        try:
            response = self.agent.send_message(self.message)
            self.result_ready.emit(response)
        except Exception as e:
            self.result_ready.emit(f"Error: {e}")


class AgentTab(QWidget):
    """Individual agent tab widget compatible with HelperGUI.py style"""
    
    def __init__(self, agent, orchestrator, config):
        super().__init__()
        self.agent = agent
        self.orchestrator = orchestrator
        self.config = config
        self.user = orchestrator.user
        self.name = agent.name
        self.loaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Initialize worker references
        self.worker = None
        self.vulnerability_worker = None
        self.judgment_worker = None
        self.reflection_worker = None

        # Initialize UI first
        self.init_ui()
        print(f"[tab:{self.name}] back in __init__ after init_ui", flush=True)

        # Print session header so the user can see which model and version
        # is behind this tab, plus when the session loaded.
        self._display_session_header()
        print(f"[tab:{self.name}] back in __init__ after _display_session_header", flush=True)

        # Check if history was already loaded during agent initialization
        has_history = hasattr(agent, 'history_data') and agent.history_data.get('history')
        if has_history and len(agent.history_data['history']) > 1:
            # Display the loaded history - no introduction needed
            print(f"[tab:{self.name}] displaying loaded history", flush=True)
            self.display_loaded_history()
            # Use QTimer to ensure gear icon removal happens after tab is fully added
            QTimer.singleShot(50, self.clear_tab_pending)
        else:
            # No history exists - this is a new chat, so introduce
            print(f"[tab:{self.name}] introducing (no prior history)", flush=True)
            self.handle_input("Introduce yourself.")
        print(f"[tab:{self.name}] __init__ end", flush=True)

    def _infer_provider_code(self):
        """Map an agent instance to its catalog provider code via the class
        name. Used to seed the Provider dropdown when the orchestrator hasn't
        attached an explicit code yet."""
        cls = type(self.agent).__name__
        if cls.startswith("Anthropic"):
            return "anthropic"
        if cls.startswith("Google"):
            return "gemini"
        if cls.startswith("Ollama"):
            return "ollama"
        return "openai"

    def _display_session_header(self):
        print(f"[tab:{self.name}] _display_session_header begin", flush=True)
        model_code = getattr(self.agent, "model", "?")
        provider_code = getattr(self.agent, "_provider_code", None) or self._infer_provider_code()
        prov = find_provider(provider_code)
        provider_label = prov.get("ds_display_name", provider_code) if prov else provider_code
        model_entry = getattr(self.agent, "model_entry", None) or {}
        friendly = model_entry.get("model_name") or model_code
        role = getattr(self.agent, "role_md", "?")
        self.text_area.append(f"**Model:** {friendly} (`{model_code}`, {provider_label}) - **Loaded:** {self.loaded_at}")
        self.text_area.append(f"**Agent:** {self.name} - **Role:** {role}")
        try:
            # Use manifest-only counters at startup so Chroma is NOT
            # initialized here; touching Chroma's PersistentClient on
            # some Windows setups crashes the host process before the
            # window can show.
            kb_line = (
                f"_{self.kb.backend_label()}, "
                f"sources: {self.kb.manifest_source_count()}, "
                f"chunks: {self.kb.manifest_chunk_count()}_"
            )
            self.text_area.append(kb_line)
        except Exception:
            pass
        self.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")

    def on_provider_model_changed(self, provider_code, model_code):
        """Swap this tab's agent to a new provider/model. Conversation is
        reset; persona/role and harmonizer flag are preserved."""
        current_provider = getattr(self.agent, "_provider_code", None) or self._infer_provider_code()
        if provider_code == current_provider and model_code == getattr(self.agent, "model", None):
            return

        common_md = getattr(self.agent, "common_md", "common.md")
        role_md = getattr(self.agent, "role_md", "general.md")
        try:
            instructions = load_persona(common_md, role_md, {
                "user": self.user,
                "name": self.name,
            })
        except Exception as e:
            self.text_area.append(f"**Failed to reload persona on provider switch:** {e}")
            return

        try:
            AgentClass = engine_class_for(provider_code)
            new_agent = AgentClass(
                model=model_code,
                name=self.name,
                instructions=instructions,
                user=self.user,
                config=self.config,
            )
        except Exception as e:
            self.text_area.append(f"**Failed to switch to {provider_code}/{model_code}:** {e}")
            return

        # Preserve cross-cutting metadata used elsewhere by the orchestrator
        # and by other handlers (vulnerability / judgment / reflection).
        new_agent.common_md = common_md
        new_agent.role_md = role_md
        new_agent.model_entry = getattr(self.agent, "model_entry", None)
        new_agent.harmonizer = getattr(self.agent, "harmonizer", False)
        new_agent._provider_code = provider_code

        # Replace inside the orchestrator's agent list at the same index.
        try:
            idx = self.orchestrator.agents.index(self.agent)
            self.orchestrator.agents[idx] = new_agent
        except ValueError:
            self.orchestrator.agents.append(new_agent)

        self.agent = new_agent
        self.text_area.clear()
        self._display_session_header()
        self.text_area.append(f"**Switched to:** {provider_code} / `{model_code}` - conversation reset.")
        self.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")

    def open_rag_settings(self):
        dlg = RAGSettingsDialog(self.name, self.kb, default_top_k=self.rag_top_k, parent=self)
        if dlg.exec_():
            self.rag_top_k = dlg.chosen_top_k()
            new_backend = dlg.chosen_backend()
            if new_backend and new_backend != self.kb.backend:
                try:
                    self.kb.set_backend(new_backend)
                    self.text_area.append(
                        f"_RAG backend set to {new_backend}; index was wiped (dimensions differ)._"
                    )
                except Exception as e:
                    self.text_area.append(f"**Failed to set RAG backend:** {e}")
            self.text_area.append(f"_{self.kb.backend_label()}_")

    def closeEvent(self, event):
        """Handle widget closure by stopping all worker threads"""
        self.stop_all_workers()
        super().closeEvent(event)

    def stop_all_workers(self):
        """Stop all worker threads before destruction"""
        try:
            workers = [
                ('worker', self.worker),
                ('vulnerability_worker', self.vulnerability_worker),
                ('judgment_worker', self.judgment_worker),
                ('reflection_worker', self.reflection_worker)
            ]
            
            for name, worker in workers:
                if worker and worker.isRunning():
                    worker.terminate()
                    if not worker.wait(1000):  # Wait up to 1 second
                        print(f"Warning: {name} for {self.name} did not terminate gracefully")
                    else:
                        print(f"Stopped {name} for {self.name}")
        except Exception as e:
            print(f"Error stopping workers for {self.name}: {e}")
    
    def init_ui(self):
        print(f"[tab:{self.name}] init_ui begin", flush=True)
        layout = QVBoxLayout()

        # Per-agent knowledge base + retrieval depth (read from main config).
        print(f"[tab:{self.name}] creating KnowledgeBase", flush=True)
        self.kb = KnowledgeBase(self.name)
        self.rag_top_k = int(self.config.get("rag_top_k", 4))
        print(f"[tab:{self.name}] KnowledgeBase OK (backend={self.kb.backend})", flush=True)

        # Per-tab provider+model selector. The agent gets rebuilt when either
        # changes (conversation resets).
        print(f"[tab:{self.name}] constructing ProviderModelSelector", flush=True)
        self.selector = ProviderModelSelector()
        print(f"[tab:{self.name}] selector OK", flush=True)
        current_provider = getattr(self.agent, "_provider_code", None) or self._infer_provider_code()
        current_model = getattr(self.agent, "model", "")
        print(f"[tab:{self.name}] set_selection({current_provider!r}, {current_model!r})", flush=True)
        self.selector.set_selection(current_provider, current_model)
        print(f"[tab:{self.name}] set_selection OK; connecting signal", flush=True)
        self.selector.selection_changed.connect(self.on_provider_model_changed)
        layout.addWidget(self.selector)
        print(f"[tab:{self.name}] selector added to layout", flush=True)

        # Agent controls row
        print(f"[tab:{self.name}] building controls row", flush=True)
        row = QHBoxLayout()
        self.checkbox = QCheckBox(f"Enable {self.name}")
        self.checkbox.setChecked(True)
        self.checkbox.stateChanged.connect(self.toggle_active)
        row.addWidget(self.checkbox)

        self.harmonizer_checkbox = QCheckBox("Harmonizer")
        self.harmonizer_checkbox.setChecked(getattr(self.agent, 'harmonizer', False))
        self.harmonizer_checkbox.stateChanged.connect(self.toggle_harmonizer)
        row.addWidget(self.harmonizer_checkbox)

        # Per-tab role dropdown: switches the agent's persona at runtime.
        print(f"[tab:{self.name}] building role combo", flush=True)
        row.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(self._discover_md_files())
        current_role = getattr(self.agent, "role_md", "general.md")
        if current_role in [self.role_combo.itemText(i) for i in range(self.role_combo.count())]:
            self.role_combo.setCurrentText(current_role)
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        row.addWidget(self.role_combo, 1)

        # RAG settings (gear) for this tab's kb. Gear glyph U+2699 matches
        # the "gear icon" wording used in cls_file_router messages and slides.
        print(f"[tab:{self.name}] building RAG button", flush=True)
        self.rag_btn = QPushButton("⚙ RAG")
        self.rag_btn.setFixedWidth(75)
        self.rag_btn.setToolTip("RAG settings: embedding backend, top-k, consent, re-index")
        self.rag_btn.clicked.connect(self.open_rag_settings)
        row.addWidget(self.rag_btn)

        layout.addLayout(row)
        print(f"[tab:{self.name}] controls row added", flush=True)

        # Status row: indeterminate progress bar + status label. Hidden when idle.
        print(f"[tab:{self.name}] building status row", flush=True)
        self.status_row = QWidget()
        status_layout = QHBoxLayout(self.status_row)
        status_layout.setContentsMargins(0, 0, 0, 0)
        self.upload_progress = QProgressBar()
        self.upload_progress.setRange(0, 0)  # indeterminate (animated marquee)
        self.upload_progress.setFixedWidth(140)
        self.upload_progress.setTextVisible(False)
        self.upload_status_label = QLabel("")
        status_layout.addWidget(self.upload_progress)
        status_layout.addWidget(self.upload_status_label, 1)
        self.status_row.setVisible(False)
        layout.addWidget(self.status_row)

        # Holds the active upload worker so it isn't garbage-collected mid-run.
        self.upload_worker = None

        # Text display area (renders Markdown via setMarkdown)
        print(f"[tab:{self.name}] building text_area + user_input", flush=True)
        self.text_area = MarkdownTextEdit()
        self.text_area.setAcceptDrops(True)  # Enable drag and drop like ClaudeGUI.py
        self.text_area.dragEnterEvent = self.dragEnterEvent
        self.text_area.dropEvent = self.dropEvent
        layout.addWidget(self.text_area)

        # User input area
        self.user_input = AgentTextEdit(self)
        self.user_input.setFixedHeight(60)
        self.user_input.setPlaceholderText("Type your message and press Enter")
        layout.addWidget(self.user_input)

        # Button row
        print(f"[tab:{self.name}] building button row", flush=True)
        button_row = QHBoxLayout()
        
        self.copy_button = QPushButton("Copy Latest Answer")
        self.copy_button.clicked.connect(self.copy_latest_answer)
        button_row.addWidget(self.copy_button)
        
        self.vulnerability_button = QPushButton("Vulnerability")
        self.vulnerability_button.clicked.connect(self.send_vulnerability_message)
        button_row.addWidget(self.vulnerability_button)
        
        self.judgment_button = QPushButton("Judgment")
        self.judgment_button.clicked.connect(self.send_judgment_message)
        button_row.addWidget(self.judgment_button)
        
        self.reflection_button = QPushButton("Reflection")
        self.reflection_button.clicked.connect(self.send_reflection_message)
        button_row.addWidget(self.reflection_button)
        
        layout.addLayout(button_row)
        self.setLayout(layout)
        print(f"[tab:{self.name}] layout set; applying font size", flush=True)

        # Apply font sizes
        fontsize = int(self.config.get("fontsize", 10))
        for widget in [self.text_area, self.user_input, self.copy_button,
                      self.vulnerability_button, self.judgment_button,
                      self.reflection_button, self.checkbox, self.harmonizer_checkbox,
                      self.role_combo, self.upload_status_label]:
            font = widget.font()
            font.setPointSize(fontsize)
            widget.setFont(font)
        print(f"[tab:{self.name}] init_ui end", flush=True)

    def _discover_md_files(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(script_dir, "*.md")))
        return [f for f in files if f != "common.md"]

    def on_role_changed(self, new_role):
        if not new_role or new_role == getattr(self.agent, "role_md", None):
            return
        common_md = getattr(self.agent, "common_md", "common.md")
        try:
            new_instructions = load_persona(common_md, new_role, {
                "user": self.user,
                "name": self.name,
            })
        except Exception as e:
            self.text_area.append(f"**Failed to load role `{new_role}`:** {e}")
            return
        self.agent.role_md = new_role
        self.agent.instructions = new_instructions
        # Reset the conversation so the new persona doesn't inherit prior context.
        try:
            self.agent.reset_conversation()
        except Exception as e:
            self.text_area.append(f"**Warning during reset:** {e}")
        self.text_area.clear()
        self._display_session_header()
        self.text_area.append(f"**Role changed to:** `{new_role}` — conversation reset.")
        self.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")

    def apply_font_size(self, size):
        font = QFont()
        font.setPointSize(int(size))
        for child in self.findChildren(QWidget):
            child.setFont(font)
        self.text_area.document().setDefaultFont(font)
        self.text_area.rerender()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events (compatible with ClaudeGUI.py)"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Dropping files on ANY tab broadcasts them to every active agent.
        Supports multi-file drops; one drop-mode prompt covers the batch."""
        paths = extract_paths_from_drop(event)
        if not paths:
            return
        main = self._find_main_window()
        if main is not None:
            main.broadcast_files(paths)
        else:
            # Fallback: deliver to this tab only via the unified router.
            decision = RouteDecision()
            route_drop(
                decision=decision,
                file_paths=paths,
                agent=self.agent,
                knowledge_base=self.kb,
                on_context=self.upload_file,
                on_rag_status=lambda m: self.text_area.append(f"_{m}_"),
                parent_widget=self,
                default_backend=self.config.get("rag_default_backend", "openai"),
            )

    def _find_main_window(self):
        parent = self.parent()
        while parent is not None and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()
        return parent

    def upload_file(self, file_path):
        """Deliver one file to this tab's agent on a background thread.

        Shows an indeterminate progress bar + status label while the worker
        runs so the GUI isn't silent or appears frozen. When the API returns,
        prints the response and the token usage (if reported)."""
        if self.upload_worker is not None and self.upload_worker.isRunning():
            self.text_area.append(f"_(Already uploading; ignored drop of `{file_path}`)_")
            return

        if not hasattr(self.agent, 'process_file_upload') and not hasattr(self.agent, 'upload_file'):
            self.text_area.append(f"File upload not supported for {self.name}")
            return

        agent = self.agent
        filename = os.path.basename(file_path)

        def do_upload(status_cb):
            # Runs on the worker thread. Returns (response_text, usage_dict|None).
            if hasattr(agent, 'process_file_upload'):
                try:
                    response = agent.process_file_upload(file_path, status_callback=status_cb)
                except TypeError:
                    response = agent.process_file_upload(file_path)
                usage = getattr(agent, '_last_usage', None)
                return response, usage
            # Legacy: only upload_file (vector store).
            status_cb("Uploading to OpenAI vector store (remote)")
            file_id = agent.upload_file(file_path)
            return (f"File uploaded successfully: ID `{file_id}`" if file_id else "File upload failed."), None

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
        # Also echo a faint trail in the chat log so the user has a record.
        self.text_area.append(f"_…{msg}_")

    def _on_upload_finished(self, response, usage):
        usage_str = format_usage(usage) if usage else ""
        if usage_str:
            self.text_area.append(f"_Done — tokens: {usage_str}_")
        else:
            self.text_area.append("_Done._")
        self._hide_upload_status()
        self.show_response(response)

    def _on_upload_error(self, msg):
        self._hide_upload_status()
        self.text_area.append(f"**Upload error:** {msg}")
        self.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")

    def toggle_active(self, state):
        """Toggle agent active state"""
        self.agent.active = bool(state)

    def toggle_harmonizer(self, state):
        """Toggle agent harmonizer state"""
        self.agent.harmonizer = bool(state)

    def mark_tab_pending(self):
        """Mark tab as pending with gear icon"""
        parent = self.parent()
        while parent and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()
        if parent:
            index = parent.tabs.indexOf(self)
            if index != -1:
                current_name = parent.tabs.tabText(index)
                if not current_name.startswith("⚙"):
                    parent.tabs.setTabText(index, f"⚙ {self.name}")

    def clear_tab_pending(self):
        """Clear pending gear icon from tab"""
        parent = self.parent()
        while parent and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()
        if parent:
            index = parent.tabs.indexOf(self)
            if index != -1:
                parent.tabs.setTabText(index, self.name)

    def display_loaded_history(self):
        """Display loaded conversation history in the text area"""
        try:
            history_data = self.agent.history_data.get('history', [])
            chat_id = self.agent.history_data.get('chat_id')
            
            if not history_data:
                return
            
            self.text_area.append("=== RESTORED CONVERSATION ===")
            if chat_id:
                self.text_area.append(f"Chat ID: {chat_id}")
            
            # For Claude agents, use display_history if available, otherwise use history
            display_data = getattr(self.agent, 'display_history', history_data)
            if not display_data:
                display_data = history_data
            
            for entry in display_data:
                if not isinstance(entry, dict):
                    continue
                    
                role = entry.get('role', 'unknown')
                content = entry.get('content', '')
                timestamp = entry.get('timestamp', '')
                
                # Skip system messages for display
                if role == 'user' and 'Introduce yourself as' in content:
                    continue
                    
                if role == 'user':
                    time_str = f" ({timestamp})" if timestamp else ""
                    self.text_area.append(f"{self.user}{time_str}: {content}")
                    self.text_area.append(">>>>>>>>>>>>>>>>>>>>>>>>>>")
                elif role == 'assistant':
                    time_str = f" ({timestamp})" if timestamp else ""
                    self.text_area.append(f"{self.name}{time_str}: {content}")
                    self.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")
                    # Update latest response for copy functionality
                    self.agent.latest_response = content
            
            message_count = len([e for e in display_data if e.get('role') in ['user', 'assistant']])
            self.text_area.append(f"=== CONVERSATION RESTORED ({message_count} messages) ===")
            
            integrity_text = self.agent.get_integrity_display_text()
            if integrity_text:
                self.text_area.append("=" * 50)
                self.text_area.append(integrity_text)
                self.text_area.append("=" * 50)            
            
        except Exception as e:
            self.text_area.append(f"Error displaying history: {e}")
            print(f"Error displaying history for {self.name}: {e}")

    def handle_input(self, text):
        """Handle user input to agent. RAG-augments the outgoing message if
        the per-agent knowledge base has any indexed content."""
        print(f"[tab:{self.name}] handle_input begin", flush=True)
        if not self.agent.active:
            return

        self.mark_tab_pending()
        self.text_area.append(f"{self.user}: {text}")
        self.text_area.append(">>>>>>>>>>>>>>>>>>>>>>>>>>")

        outgoing = text
        # IMPORTANT: use manifest_chunk_count, not count(). count() opens
        # the Chroma collection (which can crash the process on Windows
        # during ONNX/DLL load). manifest_chunk_count is pure file I/O and
        # is the authoritative count of what *we* ingested.
        if getattr(self, "kb", None) and self.kb.backend and self.kb.manifest_chunk_count() > 0:
            print(f"[tab:{self.name}] kb has {self.kb.manifest_chunk_count()} chunks; running RAG query", flush=True)
            try:
                chunks = self.kb.query(text, top_k=self.rag_top_k)
            except Exception as e:
                self.text_area.append(f"_(RAG query failed: {e}. Sending without retrieval.)_")
                chunks = []
            if chunks:
                self.text_area.append(render_citations(chunks))
                outgoing = build_rag_prompt(text, chunks)

        parent = self.parent()
        while parent and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()

        if parent and hasattr(parent, 'orchestrator'):
            self.worker = BlockchainAgentWorker(parent.orchestrator, self.agent, outgoing)
            self.worker.result_ready.connect(self.show_response)
            self.worker.start()
        else:
            self.worker = AgentWorker(self.agent, outgoing)
            self.worker.result_ready.connect(self.show_response)
            self.worker.start()

    def show_response(self, response):
        """Display agent response"""
        # Show integrity warning if present
        integrity_text = self.agent.get_integrity_display_text()
        if integrity_text:
            self.text_area.append("=" * 30)
            self.text_area.append(integrity_text)
            self.text_area.append("=" * 30)
        
        self.text_area.append(f"{self.name}: {response}")
        self.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")
        self.clear_tab_pending()  # Remove gear icon when finished
        self.user_input.setEnabled(True)
        
        # Notify parent that agent finished
        parent = self.parent()
        while parent and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()
        if parent and hasattr(parent, 'agent_finished'):
            parent.agent_finished()

    def send_vulnerability_message(self):
        """Send vulnerability analysis request (asynchronous)"""
        # Disable button to prevent multiple clicks
        self.vulnerability_button.setEnabled(False)
        
        parent = self.parent()
        while parent and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()
        
        if parent:
            # Mark other agent tabs as working
            for tab in parent.agent_tabs:
                if tab.name != self.name and tab.agent.active:
                    tab.mark_tab_pending()
                    tab.user_input.setEnabled(False)
        
        # Start async worker
        self.vulnerability_worker = VulnerabilityWorker(self.orchestrator, self.name)
        self.vulnerability_worker.result_ready.connect(self.handle_vulnerability_results)
        self.vulnerability_worker.start()
    
    def handle_vulnerability_results(self, requests, responses):
        """Handle vulnerability analysis results"""
        parent = self.parent()
        while parent and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()
        
        if parent:
            for agent_name, response in responses.items():
                # Find the agent tab and display both request and response
                for tab in parent.agent_tabs:
                    if tab.name == agent_name:
                        # Show the actual request message that was sent
                        if agent_name in requests:
                            tab.text_area.append(f"{self.user}: {requests[agent_name]}")
                            tab.text_area.append(">>>>>>>>>>>>>>>>>>>>>>>>>>")
                        # Show the response
                        tab.text_area.append(f"{tab.name}: {response}")
                        tab.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")
                        tab.clear_tab_pending()  # Remove gear icon
                        tab.user_input.setEnabled(True)  # Re-enable input
                        break
        
        # Re-enable button
        self.vulnerability_button.setEnabled(True)

    def send_judgment_message(self):
        """Send judgment analysis request (asynchronous)"""
        # Disable button to prevent multiple clicks
        self.judgment_button.setEnabled(False)
        
        parent = self.parent()
        while parent and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()
        
        if parent:
            # Mark harmonizer agent tabs as working
            for tab in parent.agent_tabs:
                if getattr(tab.agent, 'harmonizer', False) and tab.agent.active:
                    tab.mark_tab_pending()
                    tab.user_input.setEnabled(False)
        
        # Start async worker
        self.judgment_worker = JudgmentWorker(self.orchestrator, self.name)
        self.judgment_worker.result_ready.connect(self.handle_judgment_results)
        self.judgment_worker.start()
    
    def handle_judgment_results(self, requests, responses):
        """Handle judgment analysis results"""
        parent = self.parent()
        while parent and not isinstance(parent, MultiAgentChatGUI):
            parent = parent.parent()
        
        if parent:
            for agent_name, response in responses.items():
                # Find the agent tab and display both request and response
                for tab in parent.agent_tabs:
                    if tab.name == agent_name:
                        # Show the actual request message that was sent
                        if agent_name in requests:
                            tab.text_area.append(f"{self.user}: {requests[agent_name]}")
                            tab.text_area.append(">>>>>>>>>>>>>>>>>>>>>>>>>>")
                        # Show the response
                        tab.text_area.append(f"{tab.name}: {response}")
                        tab.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")
                        tab.clear_tab_pending()  # Remove gear icon
                        tab.user_input.setEnabled(True)  # Re-enable input
                        break
        
        # Re-enable button
        self.judgment_button.setEnabled(True)

    def send_reflection_message(self):
        """Send reflection analysis request (asynchronous)"""
        # Disable button and mark this tab as working
        self.reflection_button.setEnabled(False)
        self.mark_tab_pending()
        self.user_input.setEnabled(False)
        
        # Start async worker
        self.reflection_worker = ReflectionWorker(self.orchestrator, self.name)
        self.reflection_worker.result_ready.connect(self.handle_reflection_results)
        self.reflection_worker.start()
    
    def handle_reflection_results(self, request_message, response):
        """Handle reflection analysis results"""
        # Show the actual request message that was sent
        if request_message:
            self.text_area.append(f"{self.user}: {request_message}")
            self.text_area.append(">>>>>>>>>>>>>>>>>>>>>>>>>>")
        # Show the response
        self.text_area.append(f"{self.name}: {response}")
        self.text_area.append("<<<<<<<<<<<<<<<<<<<<<<<<<<")
        
        # Remove gear icon and re-enable controls
        self.clear_tab_pending()
        self.user_input.setEnabled(True)
        self.reflection_button.setEnabled(True)

    def copy_latest_answer(self):
        """Copy latest agent response to clipboard (compatible with HelperGUI.py)"""
        QApplication.clipboard().setText(self.agent.latest_response)
        self.text_area.append("Latest answer copied to clipboard.")


class MultiAgentChatGUI(QWidget):
    """Main GUI class for multi-agent chat system"""
    
    def __init__(self):
        super().__init__()

        # Load configuration and initialize orchestrator
        self.master_config_path = "config.json"
        print("[mac] load_configuration() ...", flush=True)
        self.load_configuration()
        print("[mac] load_configuration() done", flush=True)

        self.active_agents_working = 0

        print("[mac] init_ui() ...", flush=True)
        self.init_ui()
        print("[mac] init_ui() done", flush=True)

        print("[mac] create_agent_tabs() ...", flush=True)
        self.create_agent_tabs()
        print("[mac] create_agent_tabs() done", flush=True)

    def load_configuration(self):
        """Load configuration from appropriate location"""
        master_config = None
        
        # Try to load master config
        if not os.path.exists(self.master_config_path):
            print(f"Master config file not found: {self.master_config_path}")
            # Prompt user to select config file
            selected_config = self._prompt_for_config_file()
            if selected_config:
                self.master_config_path = selected_config
            else:
                # User cancelled - cannot proceed
                QMessageBox.critical(
                    None,
                    "Configuration Required",
                    "No configuration file selected. The application cannot start without a valid config file."
                )
                sys.exit(1)
        
        try:
            # Load master config
            with open(self.master_config_path, "r") as f:
                master_config = json.load(f)
            
            cwd = master_config["CONFIG"].get("CWD", "/chats")
            
            # If CWD is not /chats, check for config.json in that directory
            if cwd != "/chats":
                # Convert relative path to absolute if needed
                if cwd.startswith("/"):
                    cwd_path = cwd[1:]  # Remove leading slash for relative path
                else:
                    cwd_path = cwd
                
                config_in_cwd = os.path.join(cwd_path, "config.json")
                
                if os.path.exists(config_in_cwd):
                    print(f"Loading config from CWD: {config_in_cwd}")
                    with open(config_in_cwd, "r") as f:
                        self.current_config_data = json.load(f)
                    self.current_config_path = config_in_cwd
                else:
                    print(f"No config.json found in CWD: {cwd_path}, using master config")
                    self.current_config_data = master_config
                    self.current_config_path = self.master_config_path
            else:
                # CWD is /chats, use master config
                self.current_config_data = master_config
                self.current_config_path = self.master_config_path
            
            # Initialize orchestrator with current config
            self.orchestrator = MultiAgentOrchestrator(self.current_config_path)
            
        except FileNotFoundError as e:
            print(f"Configuration file not found: {e}")
            # Prompt user to select config file
            selected_config = self._prompt_for_config_file()
            if selected_config:
                self.master_config_path = selected_config
                # Retry loading with the selected config
                self.load_configuration()
            else:
                QMessageBox.critical(
                    None,
                    "Configuration Required",
                    "No configuration file selected. The application cannot start without a valid config file."
                )
                sys.exit(1)
                
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
            QMessageBox.critical(
                None,
                "Invalid Configuration",
                f"The configuration file is not valid JSON:\n{e}\n\nPlease select a valid config file."
            )
            # Prompt for a different config file
            selected_config = self._prompt_for_config_file()
            if selected_config:
                self.master_config_path = selected_config
                # Retry loading with the selected config
                self.load_configuration()
            else:
                sys.exit(1)
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Only use fallback if we have a valid master_config
            if master_config is not None:
                print("Using master config as fallback")
                self.current_config_data = master_config
                self.current_config_path = self.master_config_path
                try:
                    self.orchestrator = MultiAgentOrchestrator(self.master_config_path)
                except Exception as orch_error:
                    QMessageBox.critical(
                        None,
                        "Initialization Failed",
                        f"Failed to initialize orchestrator:\n{orch_error}"
                    )
                    sys.exit(1)
            else:
                QMessageBox.critical(
                    None,
                    "Configuration Error",
                    f"Failed to load configuration:\n{e}"
                )
                sys.exit(1)

    def _prompt_for_config_file(self):
        """
        Prompt user to select a configuration file.
        Returns the selected file path or None if cancelled.
        """
        QMessageBox.warning(
            None,
            "Config File Not Found",
            f"Configuration file not found: {self.master_config_path}\n\n"
            "Please select a valid configuration file (config.json or config_*.json)"
        )
        
        config_file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Configuration File",
            "",
            "Config Files (config*.json);;All JSON Files (*.json);;All Files (*.*)"
        )
        
        if config_file_path:
            print(f"User selected config file: {config_file_path}")
            return config_file_path
        else:
            print("User cancelled config file selection")
            return None
    

    def update_cwd_in_config(self, new_cwd):
        """Update the CWD in master config file"""
        try:
            # Always update the master config file
            with open(self.master_config_path, "r") as f:
                master_config = json.load(f)
            
            master_config["CONFIG"]["CWD"] = new_cwd
            
            with open(self.master_config_path, "w") as f:
                json.dump(master_config, f, indent=4)
            
            print(f"Updated CWD in master config to: {new_cwd}")
            
        except Exception as e:
            print(f"Error updating CWD in config: {e}")

    def restart_interface(self):
        """Restart the entire interface with new configuration"""
        try:
            print("Restarting interface with new configuration...")
            
            # Clear current interface
            self.clear_interface()
            
            # Reload configuration
            self.load_configuration()
            
            # Update window title with new CWD
            cwd = self.current_config_data["CONFIG"].get("CWD", "/chats")
            self.setWindowTitle(f"The Flaws of Others - Multi-agent Consensus - CWD: {cwd}")
            
            # Recreate interface
            self.create_agent_tabs()
            
            print("Interface restarted successfully")
            
        except Exception as e:
            print(f"Error restarting interface: {e}")

    def clear_interface(self):
        """Clear the current interface completely"""
        try:
            # Stop all running worker threads first
            for tab in self.agent_tabs:
                self.stop_agent_workers(tab)
            
            # Remove all agent tabs
            while self.tabs.count() > 0:
                widget = self.tabs.widget(0)
                self.tabs.removeTab(0)
                if widget:
                    widget.deleteLater()
            
            # Clear agent tabs list
            self.agent_tabs = []
            
            # Reset working agents counter
            self.active_agents_working = 0
            
            print("Interface cleared successfully")
            
        except Exception as e:
            print(f"Error clearing interface: {e}")

    def stop_agent_workers(self, tab):
        """Stop all worker threads for an agent tab"""
        try:
            # Stop main agent worker if running
            if hasattr(tab, 'worker') and tab.worker.isRunning():
                tab.worker.terminate()
                tab.worker.wait(1000)  # Wait up to 1 second for termination
                print(f"Stopped main worker for {tab.name}")
            
            # Stop vulnerability worker if running
            if hasattr(tab, 'vulnerability_worker') and tab.vulnerability_worker.isRunning():
                tab.vulnerability_worker.terminate()
                tab.vulnerability_worker.wait(1000)
                print(f"Stopped vulnerability worker for {tab.name}")
            
            # Stop judgment worker if running
            if hasattr(tab, 'judgment_worker') and tab.judgment_worker.isRunning():
                tab.judgment_worker.terminate()
                tab.judgment_worker.wait(1000)
                print(f"Stopped judgment worker for {tab.name}")
            
            # Stop reflection worker if running
            if hasattr(tab, 'reflection_worker') and tab.reflection_worker.isRunning():
                tab.reflection_worker.terminate()
                tab.reflection_worker.wait(1000)
                print(f"Stopped reflection worker for {tab.name}")
                
        except Exception as e:
            print(f"Error stopping workers for {tab.name}: {e}")

    def init_ui(self):
        """Initialize the main UI"""
        # Set window title with CWD
        cwd = self.current_config_data["CONFIG"].get("CWD", "/chats")
        self.setWindowTitle(f"The Flaws of Others - Multi-agent Consensus - CWD: {cwd}")
        self.setGeometry(100, 100, 800, 600)
        self.setAcceptDrops(True)  # Enable drag and drop

        # Get font size from config
        fontsize = int(self.orchestrator.config.get("fontsize", 10))
        self.font_size = fontsize

        # Shared drop-mode decision for the whole window. One prompt per
        # session; the toggle in the header flips it.
        self.route_decision = RouteDecision()

        # Top header row: spacer + drop-mode toggle + Font - / + buttons.
        self.header_layout = QHBoxLayout()
        self.header_layout.addStretch()
        self.drop_mode_btn = self.route_decision.create_toggle_button(self)
        self.header_layout.addWidget(self.drop_mode_btn)
        self.font_dec_btn = QPushButton("-")
        self.font_dec_btn.setFixedWidth(32)
        self.font_dec_btn.clicked.connect(lambda: self.apply_font_size(self.font_size - 1))
        self.font_inc_btn = QPushButton("+")
        self.font_inc_btn.setFixedWidth(32)
        self.font_inc_btn.clicked.connect(lambda: self.apply_font_size(self.font_size + 1))
        self.header_layout.addWidget(self.font_dec_btn)
        self.header_layout.addWidget(self.font_inc_btn)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"QTabBar::tab {{ font-size: {fontsize}pt; min-width: {fontsize * 15}px; padding: 10px; }}")
        self.tabs.currentChanged.connect(self.focus_current_input)
        
        # Create broadcast input
        self.user_input = BroadcastTextEdit(self)
        self.user_input.setPlaceholderText("Broadcast message to all active agents (Enter to send, Shift+Enter for newline)")
        self.user_input.setFixedHeight(60)
        self.user_input.setFocusPolicy(Qt.StrongFocus)
        font = self.user_input.font()
        font.setPointSize(fontsize)
        self.user_input.setFont(font)
        
        # Create buttons
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_all_agents)
        font = self.reset_button.font()
        font.setPointSize(fontsize)
        self.reset_button.setFont(font)
        
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_agent_files)
        font = self.load_button.font()
        font.setPointSize(fontsize)
        self.load_button.setFont(font)
        
        # Layout
        layout = QVBoxLayout()
        layout.addLayout(self.header_layout)
        layout.addWidget(self.tabs)

        label = QLabel("Message to All Active Agents:")
        font = label.font()
        font.setPointSize(fontsize)
        label.setFont(font)
        layout.addWidget(label)
        
        # Bottom row with buttons and broadcast field
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.reset_button)
        bottom_layout.addWidget(self.load_button)
        bottom_layout.addWidget(self.user_input, 1)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def broadcast_files(self, file_paths):
        """Route a (possibly multi-file) drop through the unified file router
        to every active agent. The drop-mode prompt is asked once per session
        and applies to the whole batch across all agents."""
        import traceback
        active_tabs = [t for t in getattr(self, "agent_tabs", []) if getattr(t.agent, "active", True)]
        if not active_tabs or not file_paths:
            return
        # Ensure the user has made a per-window choice once. Subsequent
        # broadcasts reuse it (toggle button to flip).
        self.route_decision.ensure_choice(self)
        default_backend = self.orchestrator.config.get("rag_default_backend", "openai")
        for tab in active_tabs:
            try:
                route_drop(
                    decision=self.route_decision,
                    file_paths=file_paths,
                    agent=tab.agent,
                    knowledge_base=tab.kb,
                    on_context=tab.upload_file,
                    on_rag_status=lambda m, t=tab: t.text_area.append(f"_{m}_"),
                    parent_widget=self,
                    default_backend=default_backend,
                )
            except Exception as e:
                # Defensive: keep the GUI alive even if route_drop blows up
                # in a way its internal handlers didn't catch. Print the
                # full traceback so the launching terminal records it.
                msg = f"broadcast_files: error delivering to {tab.name}: {type(e).__name__}: {e}"
                print(msg)
                traceback.print_exc()
                try:
                    tab.text_area.append(f"_{msg}_")
                except Exception:
                    pass

    # Legacy alias preserved so any old caller still works.
    def broadcast_file(self, file_path):
        self.broadcast_files([file_path])

    def apply_font_size(self, size):
        # Propagates font size to the main window's children and every agent tab.
        self.font_size = max(6, min(48, int(size)))
        font = QFont()
        font.setPointSize(self.font_size)
        for child in self.findChildren(QWidget):
            if isinstance(child, AgentTab):
                continue  # AgentTab handles its own widgets via apply_font_size below.
            child.setFont(font)
        # Keep the QTabBar styling in sync with the new size.
        self.tabs.setStyleSheet(
            f"QTabBar::tab {{ font-size: {self.font_size}pt; "
            f"min-width: {self.font_size * 15}px; padding: 10px; }}"
        )
        # Cascade into each agent tab so MarkdownTextEdit rerenders.
        for tab in getattr(self, "agent_tabs", []):
            try:
                tab.apply_font_size(self.font_size)
            except Exception:
                pass

    def create_agent_tabs(self):
        """Create tabs for each agent"""
        import traceback as _tb
        self.agent_tabs = []
        for agent in self.orchestrator.agents:
            try:
                print(f"[mac] building tab for agent {agent.name} ({type(agent).__name__}) ...", flush=True)
                tab = AgentTab(agent, self.orchestrator, self.orchestrator.config)
                print(f"[mac] tab built for {agent.name}; adding to QTabWidget", flush=True)
                self.tabs.addTab(tab, f"⚙ {agent.name}")
                self.agent_tabs.append(tab)
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(100, lambda t=tab: self.check_and_update_tab_status(t))
                print(f"[mac] tab for {agent.name} OK", flush=True)
            except BaseException as e:
                print(f"[mac] FAILED building tab for {agent.name}: {type(e).__name__}: {e}", flush=True)
                _tb.print_exc()
                # Re-raise so the outer __main__ handler prints + the user
                # sees a non-silent failure rather than a partially-built window.
                raise

    def check_and_update_tab_status(self, tab):
        """Check if tab should have gear icon removed after initialization"""
        # If agent has history and is not currently working, remove gear icon
        has_history = hasattr(tab.agent, 'history_data') and tab.agent.history_data.get('history')
        if has_history and len(tab.agent.history_data['history']) > 1:
            # History was loaded, ensure gear icon is removed
            tab.clear_tab_pending()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop on the main window chrome (outside any tab).
        Broadcasts to every active agent through the unified router."""
        paths = extract_paths_from_drop(event)
        if paths:
            self.broadcast_files(paths)

    def broadcast_message_text(self, text):
        """Broadcast message to all active agents"""
        print(f"Broadcasting message: '{text}' to active agents")
        
        # Disable broadcast input while agents work
        self.user_input.setEnabled(False)
        self.active_agents_working = 0
        
        # Send to all active agents
        for tab in self.agent_tabs:
            if tab.agent.active:
                self.active_agents_working += 1
                tab.handle_input(text)
        
        print(f"Message sent to {self.active_agents_working} active agents")
        
        # Re-enable immediately if no agents are active
        if self.active_agents_working == 0:
            self.user_input.setEnabled(True)

    def agent_finished(self):
        """Called when an agent finishes processing"""
        self.active_agents_working -= 1
        print(f"Agent finished. {self.active_agents_working} agents still working.")
        
        # Re-enable broadcast field when all agents are done
        if self.active_agents_working <= 0:
            self.active_agents_working = 0
            self.user_input.setEnabled(True)
            print("All agents finished. Broadcast field re-enabled.")

    def focus_current_input(self, index):
        """Handle tab focus changes"""
        if hasattr(self, 'user_input') and not self.user_input.hasFocus():
            if 0 <= index < len(self.agent_tabs):
                self.agent_tabs[index].user_input.setFocus()

    def showEvent(self, event):
        """Ensure broadcast field gets focus when window is shown"""
        super().showEvent(event)
        self.user_input.setFocus()

    def reset_all_agents(self):
        """Reset all agents with warning and file deletion"""
        cwd = self.current_config_data["CONFIG"].get("CWD", "/chats")
        
        # Show warning dialog
        warning_msg = (
            f"WARNING: Resetting the chat will delete the files for the agents "
            f"named in the active configuration file and in the current working directory ({cwd}). "
            f"New instances of agents will be created. Is this what you want?"
        )
        
        reply = QMessageBox.question(
            self, 
            'Reset Confirmation', 
            warning_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Default to No for safety
        )
        
        if reply == QMessageBox.Yes:
            print("User confirmed reset. Starting reset process...")
            
            # Show reset interface
            self.show_reset_interface()
            
            # Process events to update display
            QApplication.processEvents()
            
            # Delete agent files in current working directory
            self.delete_agent_files()
            
            # Small delay to show the reset message
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, self.complete_reset)
            
        else:
            print("Reset cancelled by user")

    def show_reset_interface(self):
        """Show reset message and clear interface"""
        try:
            # Clear all tabs first
            self.clear_interface()
            
            # Create a large reset message label
            reset_label = QLabel("Resetting interface...")
            reset_label.setAlignment(Qt.AlignCenter)
            reset_label.setStyleSheet("QLabel { font-size: 24pt; color: #333; padding: 50px; }")
            
            # Temporarily replace the tabs widget with the reset message
            layout = self.layout()
            
            # Remove tabs widget temporarily
            if hasattr(self, 'tabs'):
                layout.removeWidget(self.tabs)
                self.tabs.hide()
            
            # Insert reset label at the top
            layout.insertWidget(0, reset_label)
            self.reset_label = reset_label  # Store reference for removal
            
            print("Reset interface displayed")
            
        except Exception as e:
            print(f"Error showing reset interface: {e}")

    def complete_reset(self):
        """Complete the reset process by reloading configuration and creating fresh agents"""
        try:
            print("Completing reset process...")
            
            # Remove reset label
            if hasattr(self, 'reset_label'):
                self.layout().removeWidget(self.reset_label)
                self.reset_label.deleteLater()
                del self.reset_label
            
            # Show tabs widget again
            if hasattr(self, 'tabs'):
                self.tabs.show()
                self.layout().insertWidget(0, self.tabs)
            
            # Reload configuration
            self.load_configuration()
            
            # Update window title with new CWD
            cwd = self.current_config_data["CONFIG"].get("CWD", "/chats")
            self.setWindowTitle(f"The Flaws of Others - Multi-agent Consensus - CWD: {cwd}")
            
            # Create fresh agent tabs and initialize them
            self.create_fresh_agent_tabs()
            
            print("All agents reset and interface restarted with fresh agents")
            
        except Exception as e:
            print(f"Error completing reset: {e}")

    def create_fresh_agent_tabs(self):
        """Create fresh agent tabs and initialize all agents with introductions"""
        self.agent_tabs = []
        
        for agent in self.orchestrator.agents:
            tab = AgentTab(agent, self.orchestrator, self.orchestrator.config)
            # Start with gear icon - will be removed after introduction
            self.tabs.addTab(tab, f"⚙ {agent.name}")
            self.agent_tabs.append(tab)
            
            # Force introduction for all agents (fresh start)
            tab.handle_input("Introduce yourself.")
            
            print(f"Created fresh agent tab for {agent.name} and requested introduction")

    def delete_agent_files(self):
        """Delete agent conversation files for current agents"""
        try:
            cwd = self.current_config_data["CONFIG"].get("CWD", "/chats")
            
            # Convert CWD path to actual directory path
            if cwd.startswith("/"):
                cwd_path = cwd[1:]  # Remove leading slash for relative path
            else:
                cwd_path = cwd
            
            # Ensure the chats directory exists
            if not os.path.exists(cwd_path):
                print(f"CWD directory {cwd_path} does not exist, creating it...")
                os.makedirs(cwd_path, exist_ok=True)
                return
            
            # Delete files for each agent in current configuration
            for agent in self.orchestrator.agents:
                agent_name = agent.name
                file_path = os.path.join(cwd_path, f"{agent_name}.json")
                
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Deleted agent file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")
                else:
                    print(f"Agent file not found (will be created fresh): {file_path}")
            
            print(f"Agent file cleanup completed in directory: {cwd_path}")
            
        except Exception as e:
            print(f"Error during agent file deletion: {e}")

    def load_agent_files(self):
        """Load agent files from config file's directory and update CWD"""
        # Select config file instead of folder
        config_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select config.json file",
            "",
            "Config Files (config*.json);;All Files (*.*)"
        )
        
        if not config_file_path:
            print("No config file selected")
            return
        
        # Get the directory containing the config file
        folder_path = os.path.dirname(config_file_path)
        
        print(f"Selected config file: {config_file_path}")
        print(f"Loading agent JSON files from: {folder_path}")
        
        # Update CWD in master config
        # Convert absolute path to relative path format for config
        current_dir = os.getcwd()
        if folder_path.startswith(current_dir):
            relative_path = folder_path[len(current_dir):].replace("\\", "/")
            if not relative_path.startswith("/"):
                relative_path = "/" + relative_path
        else:
            # If not under current directory, use absolute path
            relative_path = folder_path.replace("\\", "/")
        
        self.update_cwd_in_config(relative_path)
        
        # Mark all tabs as working
        for tab in self.agent_tabs:
            tab.mark_tab_pending()
            tab.text_area.clear()
        
        results = self.orchestrator.load_agent_files(folder_path)
        
        # Display results and handle history display
        for tab in self.agent_tabs:
            if tab.name in results:
                result = results[tab.name]
                tab.text_area.append(f"=== LOAD RESULT ===")
                tab.text_area.append(result)
                
                # If chat history was loaded, display it - no introduction needed
                if "Chat history loaded" in result:
                    tab.display_loaded_history()
                
                tab.text_area.append("==================")
            tab.clear_tab_pending()  # Remove gear icon
        
        # After loading, restart interface to apply any config changes
        print("Restarting interface after load operation...")
        self.restart_interface()
    

class BlockchainAgentWorker(QThread):
    """Worker thread for blockchain-enabled agent interactions"""
    result_ready = pyqtSignal(str)
    
    def __init__(self, orchestrator, agent, message):
        super().__init__()
        self.orchestrator = orchestrator
        self.agent = agent
        self.message = message
    
    def run(self):
        try:
            response = self.orchestrator.send_message_with_integrity(self.agent, self.message)
            self.result_ready.emit(response)
        except Exception as e:
            self.result_ready.emit(f"Error: {e}")        


def _reset_agent_history_files(master_config_path="config.json"):
    """Delete agent .json history files before the orchestrator starts.

    Skips the slow conversation-replay path at startup. Resolves the active
    config the same way MultiAgentChatGUI.load_configuration does: if CWD has
    its own config.json, that one names the agents; otherwise the master config
    does.
    """
    if not os.path.exists(master_config_path):
        print(f"--reset: master config '{master_config_path}' not found; nothing to do")
        return

    try:
        with open(master_config_path, "r") as f:
            master_config = json.load(f)
    except Exception as e:
        print(f"--reset: could not parse '{master_config_path}': {e}")
        return

    cwd = master_config.get("CONFIG", {}).get("CWD", "/chats")
    cwd_path = cwd[1:] if cwd.startswith("/") else cwd

    config_in_cwd = os.path.join(cwd_path, "config.json")
    active_path = config_in_cwd if (cwd != "/chats" and os.path.exists(config_in_cwd)) else master_config_path
    try:
        with open(active_path, "r") as f:
            active_config = json.load(f)
    except Exception as e:
        print(f"--reset: could not parse active config '{active_path}': {e}")
        return

    if not os.path.isdir(cwd_path):
        print(f"--reset: CWD '{cwd_path}' does not exist; nothing to delete")
        return

    deleted = 0
    for entry in active_config.get("MODELS", []):
        name = entry.get("agent_name")
        if not name:
            continue
        file_path = os.path.join(cwd_path, f"{name}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"--reset: deleted {file_path}")
                deleted += 1
            except Exception as e:
                print(f"--reset: failed to delete {file_path}: {e}")
    print(f"--reset: removed {deleted} history file(s) from '{cwd_path}'")


if __name__ == "__main__":
    # Defensive __main__: anything that goes wrong before app.exec_() needs
    # to print loudly to stdout. PyQt5 can silently terminate the process on
    # uncaught exceptions in widget constructors on some Windows setups.
    import traceback as _tb
    try:
        print("[startup] argv =", sys.argv, flush=True)
        if "--reset" in sys.argv or "-r" in sys.argv:
            _reset_agent_history_files()

        print("[startup] creating QApplication", flush=True)
        app = QApplication([])

        print("[startup] constructing MultiAgentChatGUI", flush=True)
        window = MultiAgentChatGUI()

        print("[startup] calling window.show()", flush=True)
        window.show()

        print("[startup] entering app.exec_() event loop", flush=True)
        rc = app.exec_()
        print(f"[startup] event loop exited with code {rc}", flush=True)
    except SystemExit as e:
        print(f"[startup] SystemExit raised: code={e.code}", flush=True)
        raise
    except BaseException as e:
        print(f"[startup] UNHANDLED {type(e).__name__}: {e}", flush=True)
        _tb.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        raise