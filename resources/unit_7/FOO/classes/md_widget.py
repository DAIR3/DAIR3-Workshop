"""
md_widget.py
Drop-in QTextEdit subclass that renders content as Markdown via Qt's native
QTextEdit.setMarkdown() (available since Qt 5.14). Each call to append() adds
a block to an internal buffer and re-renders the document so prior content
keeps its Markdown formatting.

Legacy ASCII separators ('>>>>>>...', '<<<<<<...', repeated '=' bars) are
rewritten to horizontal rules so they render cleanly under Markdown instead
of as nested blockquotes.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
from PyQt5.QtWidgets import QTextEdit


class MarkdownTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self._blocks = []

    def append(self, text):
        text = self._normalize(text)
        self._blocks.append(text)
        self._render()

    def clear(self):
        self._blocks = []
        super().clear()

    def rerender(self):
        # Re-apply setMarkdown after font/document changes so the new font sticks.
        self._render()

    def _render(self):
        self.setMarkdown("\n\n".join(self._blocks) if self._blocks else "")
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())

    @staticmethod
    def _normalize(text):
        stripped = text.strip()
        if not stripped:
            return text
        # Lines made up entirely of '>' (or '<') — the old chat separators —
        # would render as deeply-nested blockquotes. Replace with a hrule.
        if set(stripped) <= {">", "<", "="} and len(stripped) >= 4:
            return "---"
        return text
