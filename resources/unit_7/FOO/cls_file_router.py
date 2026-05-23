"""
cls_file_router.py
Unified file drop handler for every FOO GUI.

Two paths exist for a dropped file:

    CONTEXT      pass the file straight to the agent's native upload
                 (`process_file_upload`). Vendor-specific: PDF + image as
                 base64 / Files API; text inlined. One-shot — the model sees
                 it for this turn but it isn't persisted.

    RAG          ingest into the agent's persistent knowledge base
                 (FOO/knowledge/<agent>/). Chunk + embed + store. Subsequent
                 chat turns retrieve from it; the file stays available across
                 sessions.

Selection UX (hybrid, see slides_7.3):

    - First drop in a session: ``RouteDecision.ask_modal()`` shows a modal
      with two big buttons (Context / RAG). The choice is cached on the
      GUI's RouteDecision instance.

    - Subsequent drops: use the cached choice. The GUI exposes a small
      toggle button labeled e.g. "Drop -> Context" that the user can flip
      at any time.

    - Multi-file drops: one prompt covers the whole batch; incompatible
      files fall back to the other mode with a notice (image -> RAG isn't
      meaningful, so a PNG in a RAG batch is routed to Context with a
      warning printed to the chat).

GUIs wire this in by:

    1. Holding one ``RouteDecision`` instance per window.
    2. In dropEvent, calling ``route_drop(decision, file_paths, agent, ...)``.
    3. The router does ``decision.choose(window)`` once per session, then
       routes each file via the agent's upload path or the agent's
       KnowledgeBase.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
import os
import traceback

from PyQt5.QtWidgets import QMessageBox, QPushButton

from file_loader import classify_file
from cls_rag import ConsentRequiredError, consent_status


MODE_CONTEXT = "context"
MODE_RAG = "rag"


class RouteDecision:
    """Per-window state holding the active drop mode. Exposes a modal-once
    prompt and a toggle button the GUI can drop into its header row.

    Pedagogically: the first prompt is the moment a participant sees the
    distinction between "context" and "RAG" explained in plain language.
    The toggle keeps the current choice visible and switchable, so the
    posture is never hidden."""

    def __init__(self):
        self.mode = None  # set on first drop or by toggle
        self.toggle_button = None

    def is_set(self):
        return self.mode in (MODE_CONTEXT, MODE_RAG)

    def ensure_choice(self, parent_widget):
        """If no mode is set yet, ask the user. Returns the chosen mode."""
        if self.is_set():
            return self.mode

        box = QMessageBox(parent_widget)
        box.setWindowTitle("How should this file be used?")
        box.setText(
            "You dropped a file. There are two ways the agent can use it.\n\n"
            "Add to conversation context\n"
            "    The file is included in this turn only. The model sees its\n"
            "    contents; nothing is stored. Best for one-off questions.\n\n"
            "Add to the knowledge base (RAG)\n"
            "    The file is chunked, embedded, and stored under\n"
            "    knowledge/<AgentName>/. Future questions will retrieve\n"
            "    relevant excerpts. Best for reference material you want the\n"
            "    agent to consult across sessions.\n\n"
            "You can switch later with the toggle in the header row."
        )
        ctx_btn = box.addButton("Add to context", QMessageBox.AcceptRole)
        rag_btn = box.addButton("Add to knowledge base (RAG)", QMessageBox.ActionRole)
        box.setDefaultButton(ctx_btn)
        box.exec_()

        if box.clickedButton() is rag_btn:
            self.mode = MODE_RAG
        else:
            self.mode = MODE_CONTEXT
        self.refresh_toggle()
        return self.mode

    def set_mode(self, mode):
        if mode in (MODE_CONTEXT, MODE_RAG):
            self.mode = mode
            self.refresh_toggle()

    def create_toggle_button(self, parent=None):
        """Return a small QPushButton bound to this decision. Clicking it
        flips the mode. The GUI puts this in its header row."""
        btn = QPushButton(parent)
        btn.setFixedWidth(160)
        btn.clicked.connect(self._flip)
        self.toggle_button = btn
        self.refresh_toggle()
        return btn

    def _flip(self):
        if self.mode == MODE_RAG:
            self.mode = MODE_CONTEXT
        else:
            self.mode = MODE_RAG
        self.refresh_toggle()

    def refresh_toggle(self):
        if self.toggle_button is None:
            return
        if self.mode == MODE_RAG:
            self.toggle_button.setText("Drop -> RAG")
        elif self.mode == MODE_CONTEXT:
            self.toggle_button.setText("Drop -> Context")
        else:
            self.toggle_button.setText("Drop -> (ask)")


# ----- Routing --------------------------------------------------------------

def _is_rag_compatible(file_path):
    """RAG path supports text and PDFs; images / audio / unknown go to
    context only (no meaningful embedding for binary media)."""
    category, _ = classify_file(file_path)
    return category in ("text", "pdf")


def route_drop(
    decision,
    file_paths,
    agent,
    knowledge_base,
    on_context,
    on_rag_status,
    parent_widget,
    default_backend=None,
):
    """Route a (possibly multi-file) drop to the agent's chosen pipeline.

    Parameters
    ----------
    decision : RouteDecision
        Per-window mode holder. ensure_choice() is called once for the batch.
    file_paths : list[str]
        Absolute paths of dropped files.
    agent : object
        Has ``process_file_upload(path, status_callback=...)`` (the existing
        per-engine handler).
    knowledge_base : cls_rag.KnowledgeBase or None
        Agent's persistent kb. May be None if the user picked Context — in
        that case the RAG path is unreachable.
    on_context : callable(file_path) -> None
        Called for each file the router decides to send via context. The GUI
        wraps this in its existing upload-on-thread flow.
    on_rag_status : callable(message) -> None
        Status sink for RAG ingestion (printed to the chat or status line).
    parent_widget : QWidget
        Used as the parent for the modal-once choice dialog.
    """
    if not file_paths:
        return

    mode = decision.ensure_choice(parent_widget)

    if mode == MODE_CONTEXT:
        for fp in file_paths:
            on_context(fp)
        return

    # mode == MODE_RAG
    if knowledge_base is None:
        on_rag_status(
            "RAG mode requested but this agent has no knowledge base bound. "
            "Falling back to context for all files."
        )
        for fp in file_paths:
            on_context(fp)
        return

    if not knowledge_base.backend:
        # Auto-default the backend so the user doesn't have to open the
        # gear dialog for every fresh agent before their first drop. The
        # consent gate fires next, giving the user an explicit opt-in
        # moment even though we chose the backend implicitly.
        chosen_default = default_backend or "openai"
        try:
            knowledge_base.set_backend(chosen_default)
            on_rag_status(
                f"No embedding backend was set for this agent; auto-defaulting to "
                f"'{chosen_default}'. You can change this in the ⚙ RAG dialog."
            )
        except Exception as e:
            on_rag_status(
                f"RAG mode requested but auto-defaulting backend failed ({e}). "
                "Falling back to context for now."
            )
            for fp in file_paths:
                on_context(fp)
            return

    # Split files into RAG-compatible and incompatible up front. Incompatible
    # files (images / audio) go straight to context with a notice; only the
    # compatible ones are subject to the consent gate and ingestion.
    rag_files, ctx_files = [], []
    for fp in file_paths:
        if _is_rag_compatible(fp):
            rag_files.append(fp)
        else:
            ctx_files.append(fp)
    for fp in ctx_files:
        on_rag_status(
            f"{os.path.basename(fp)}: not RAG-compatible (image / audio). Routed to context."
        )
        on_context(fp)
    if not rag_files:
        return

    # Pre-flight consent check on the GUI thread. One dialog per batch
    # (not per file). This avoids showing nested modal dialogs from inside
    # an exception handler, which on some Windows setups can leave Qt in
    # an inconsistent state and terminate the host process.
    if not consent_status(knowledge_base.agent_name, knowledge_base.backend):
        from widgets_common import ConsentGateDialog
        on_rag_status(
            f"Consent gate triggered for backend '{knowledge_base.backend}'."
        )
        dlg = ConsentGateDialog(
            knowledge_base.agent_name,
            knowledge_base.backend,
            parent=parent_widget,
        )
        if not dlg.exec_():
            on_rag_status("Consent declined; all files routed to context.")
            for fp in rag_files:
                on_context(fp)
            return

    # Consent recorded. Ingest each file on the calling thread; any
    # exception (network, Chroma, file I/O) falls back to context with a
    # readable trace in the chat log rather than killing the GUI.
    for fp in rag_files:
        filename = os.path.basename(fp)
        try:
            n = knowledge_base.ingest_file(fp, status_callback=on_rag_status)
            on_rag_status(f"{filename}: indexed {n} chunk(s) into knowledge base.")
        except ConsentRequiredError:
            # Shouldn't fire after the pre-flight, but if some other path
            # revoked consent between then and now, fall back gracefully.
            on_rag_status(
                f"{filename}: consent was revoked mid-batch. Routed to context."
            )
            on_context(fp)
        except Exception as e:
            on_rag_status(
                f"{filename}: ingest failed ({type(e).__name__}: {e}). "
                "Routed to context."
            )
            # Print the full traceback to stderr so foo_gui's launching
            # terminal shows it. The GUI itself stays alive.
            traceback.print_exc()
            on_context(fp)


def extract_paths_from_drop(event):
    """Drag-and-drop event -> list of local file paths. Filters out URLs that
    aren't local files (e.g. http:// drags)."""
    urls = event.mimeData().urls()
    paths = []
    for u in urls or []:
        p = u.toLocalFile()
        if p:
            paths.append(p)
    return paths
