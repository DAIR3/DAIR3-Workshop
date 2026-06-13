"""
widgets_common.py
Shared Qt widgets for FOO GUIs: Provider+Model selector and RAG settings dialog.

These exist so the four active GUIs (agentClaude, agentGPTGUI, agentGoogleGUI,
foo_gui) all surface the same controls in the same layout. Put a
``ProviderModelSelector`` into the header row and a ``RAGSettingsDialog``
behind the gear button.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QPushButton,
    QDialog, QSpinBox, QDialogButtonBox, QMessageBox, QTextEdit
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from cls_provider_catalog import (
    load_catalog,
    available_providers_for_chat,
    models_for_provider,
    find_model,
    find_provider,
    resolve_legacy_model,
)
from cls_rag import (
    consent_text, consent_status, record_consent, revoke_consent
)


class ProviderModelSelector(QWidget):
    """Two combo boxes on a single row: Provider on the left, Model on the right.

    Emits ``selection_changed(provider_code, model_code)`` when either changes.
    The Model dropdown re-populates based on the current Provider.

    Use ``set_selection(provider, model)`` to seed initial state from a config
    file or to react to a parent restoring a saved choice.
    """

    selection_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Suspend flag MUST be set before any combo is populated, because
        # addItem() can synchronously fire currentIndexChanged when the
        # index transitions from -1 to 0. If the handler runs before
        # _suspend exists, AttributeError trips at exactly the wrong time.
        self._suspend = True

        self.catalog = load_catalog()
        self.providers = available_providers_for_chat(self.catalog)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("Provider:"))
        self.provider_combo = QComboBox()
        # Connect BEFORE populating so addItem-driven signals are intercepted,
        # but stay suspended so the handler short-circuits cleanly.
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        for p in self.providers:
            self.provider_combo.addItem(p.get("ds_display_name", p["cd_provider"]), p["cd_provider"])
        layout.addWidget(self.provider_combo, 1)

        layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        layout.addWidget(self.model_combo, 2)

        # Populate model list for the initially-selected provider.
        if self.providers:
            self._refresh_models(self.providers[0]["cd_provider"])

        # Done seeding; subsequent user-driven changes should propagate.
        self._suspend = False

    def _on_provider_changed(self, _idx):
        if self._suspend:
            return
        provider = self.provider_combo.currentData()
        if not provider:
            return
        self._refresh_models(provider)
        self._emit_current()

    def _on_model_changed(self, _idx):
        if self._suspend:
            return
        self._emit_current()

    def _refresh_models(self, provider_code):
        # Save-and-restore the suspend flag so nested calls (e.g. from
        # set_selection during __init__) don't clobber the outer state.
        prev = self._suspend
        self._suspend = True
        try:
            self.model_combo.clear()
            for m in models_for_provider(provider_code, self.catalog):
                self.model_combo.addItem(m.get("nm_display", m["cd_model"]), m["cd_model"])
        finally:
            self._suspend = prev

    def _emit_current(self):
        prov = self.provider_combo.currentData()
        mod = self.model_combo.currentData()
        if prov and mod:
            self.selection_changed.emit(prov, mod)

    def current_selection(self):
        return self.provider_combo.currentData(), self.model_combo.currentData()

    def set_selection(self, provider_code, model_code):
        """Seed the dropdowns. Tolerates a missing model by falling back to
        the first available model under the chosen provider, and a missing
        provider by resolving the model_code via the legacy mapper."""
        prev = self._suspend
        self._suspend = True
        try:
            if not provider_code:
                provider_code, _ = resolve_legacy_model(model_code, self.catalog)

            idx = self.provider_combo.findData(provider_code)
            if idx < 0 and self.provider_combo.count() > 0:
                idx = 0
                provider_code = self.provider_combo.itemData(0)
            if idx >= 0:
                self.provider_combo.setCurrentIndex(idx)

            self._refresh_models(provider_code)

            midx = self.model_combo.findData(model_code)
            if midx < 0 and self.model_combo.count() > 0:
                midx = 0
            if midx >= 0:
                self.model_combo.setCurrentIndex(midx)
        finally:
            self._suspend = prev


class RAGSettingsDialog(QDialog):
    """Per-agent RAG settings: embedding backend, top-k, and a 'Re-index now'
    button. Hands the chosen values back to the caller; the caller persists
    them and triggers re-indexing if necessary.

    Construct with ``RAGSettingsDialog(agent_name, kb, parent=...)`` where
    ``kb`` is a ``cls_rag.KnowledgeBase`` (or None if not yet bound)."""

    def __init__(self, agent_name, kb, default_top_k=4, parent=None):
        super().__init__(parent)
        self.agent_name = agent_name
        self.kb = kb
        self.setWindowTitle(f"RAG settings - {agent_name}")
        self.setMinimumWidth(420)

        from cls_rag import available_backends
        backends_available = available_backends()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Embedding backend:"))
        self.backend_combo = QComboBox()
        # Always show both choices; mark unavailable ones in the label.
        if "openai" in backends_available:
            self.backend_combo.addItem("OpenAI - text-embedding-3-small (cloud)", "openai")
        else:
            self.backend_combo.addItem("OpenAI - text-embedding-3-small (set OPENAI_API_KEY)", "openai")
        if "ollama" in backends_available:
            self.backend_combo.addItem("Ollama - nomic-embed-text (local, private)", "ollama")
        else:
            self.backend_combo.addItem("Ollama - nomic-embed-text (Ollama daemon not reachable)", "ollama")

        # Pre-select the kb's current backend if set.
        if kb and kb.backend:
            idx = self.backend_combo.findData(kb.backend)
            if idx >= 0:
                self.backend_combo.setCurrentIndex(idx)
        layout.addWidget(self.backend_combo)

        layout.addSpacing(8)
        topk_row = QHBoxLayout()
        topk_row.addWidget(QLabel("Top-k retrieved chunks per query:"))
        self.topk_spin = QSpinBox()
        self.topk_spin.setRange(1, 20)
        self.topk_spin.setValue(default_top_k)
        topk_row.addWidget(self.topk_spin)
        topk_row.addStretch()
        layout.addLayout(topk_row)

        layout.addSpacing(8)
        if kb:
            sources_count = len(kb.manifest.get("files", {}))
            chunks_count = kb.count() if kb.backend else 0
            layout.addWidget(QLabel(
                f"Sources on disk: {sources_count}    Chunks indexed: {chunks_count}"
            ))
            layout.addWidget(QLabel(f"Knowledge directory: {kb.sources_dir}"))

            # Consent status for the currently-selected backend in this dialog.
            self._consent_label = QLabel("")
            layout.addWidget(self._consent_label)
            self._refresh_consent_label()

            consent_row = QHBoxLayout()
            self.revoke_btn = QPushButton("Revoke consent for selected backend")
            self.revoke_btn.setToolTip(
                "Forces the consent gate to re-prompt on the next ingest. "
                "Useful after a policy review or backend change."
            )
            self.revoke_btn.clicked.connect(self._do_revoke)
            consent_row.addWidget(self.revoke_btn)
            consent_row.addStretch()
            layout.addLayout(consent_row)

            # Reflect consent status when the user changes the backend choice.
            self.backend_combo.currentIndexChanged.connect(self._refresh_consent_label)

            self.reindex_btn = QPushButton("Re-index all sources now")
            self.reindex_btn.clicked.connect(self._do_reindex)
            layout.addWidget(self.reindex_btn)
        else:
            layout.addWidget(QLabel("No knowledge base bound to this agent yet."))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _refresh_consent_label(self):
        if not self.kb:
            return
        backend = self.backend_combo.currentData()
        status = consent_status(self.kb.agent_name, backend)
        if status:
            self._consent_label.setText(
                f"Consent: recorded for '{backend}' at {status.get('given_at', '?')}"
            )
        else:
            self._consent_label.setText(
                f"Consent: NOT YET recorded for '{backend}' - first ingest will prompt."
            )

    def _do_revoke(self):
        if not self.kb:
            return
        backend = self.backend_combo.currentData()
        revoke_consent(self.kb.agent_name, backend)
        self._refresh_consent_label()
        QMessageBox.information(
            self,
            "Consent revoked",
            f"Consent for backend '{backend}' has been revoked. The consent "
            "gate will re-prompt on the next ingest."
        )

    def _do_reindex(self):
        if not self.kb:
            return
        chosen = self.backend_combo.currentData()
        try:
            self.kb.set_backend(chosen)
            # Re-indexing implies the user wants the existing material to remain
            # indexed under the (possibly newly-chosen) backend; if consent has
            # not been recorded, present the gate now rather than failing mid-loop.
            if not consent_status(self.kb.agent_name, chosen):
                dlg = ConsentGateDialog(self.kb.agent_name, chosen, parent=self)
                if not dlg.exec_():
                    QMessageBox.warning(self, "Re-index cancelled",
                                        "Consent was not affirmed; no re-index performed.")
                    return
            count = self.kb.ingest_all_sources()
            QMessageBox.information(
                self,
                "Re-index complete",
                f"Indexed {count} chunk(s) across {len(self.kb.manifest.get('files', {}))} source file(s)."
            )
            self._refresh_consent_label()
        except Exception as e:
            QMessageBox.critical(self, "Re-index failed", str(e))

    def chosen_backend(self):
        return self.backend_combo.currentData()

    def chosen_top_k(self):
        return self.topk_spin.value()


class ConsentGateDialog(QDialog):
    """Modal disclosure shown before the first ingest under a given backend.

    The text is provided by ``cls_rag.consent_text(backend)`` so the policy
    language lives next to the policy enforcement. Affirmation is captured
    by ``cls_rag.record_consent(agent, backend)``; the dialog itself only
    asks Yes/No.

    Required call site: the file router catches ``ConsentRequiredError``
    from ``KnowledgeBase.ingest_file``, instantiates this dialog, and on
    Accept calls ``record_consent`` then retries the ingest.
    """

    def __init__(self, agent_name, backend, parent=None):
        super().__init__(parent)
        self.agent_name = agent_name
        self.backend = backend
        self.setWindowTitle(f"RAG consent gate - {agent_name} ({backend})")
        self.setMinimumWidth(640)
        self.setMinimumHeight(420)

        layout = QVBoxLayout(self)

        header = QLabel(
            f"<b>About to embed material into the knowledge base for '{agent_name}'.</b>"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        body = QTextEdit()
        body.setReadOnly(True)
        # Use monospace so the numbered list lines up; the disclosure text
        # is line-wrapped inside cls_rag for readability.
        f = QFont("Consolas")
        f.setStyleHint(QFont.Monospace)
        body.setFont(f)
        body.setPlainText(consent_text(backend))
        layout.addWidget(body, 1)

        layout.addWidget(QLabel(
            "Click 'I affirm' to record consent for this backend, or 'Cancel' "
            "to abort. The decision is persisted in index_manifest.json and "
            "can be revoked from the RAG settings dialog."
        ))

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        affirm_btn = QPushButton("I affirm")
        affirm_btn.setDefault(True)
        affirm_btn.clicked.connect(self.accept)
        buttons.addWidget(affirm_btn)
        layout.addLayout(buttons)

    def accept(self):
        record_consent(self.agent_name, self.backend)
        super().accept()
