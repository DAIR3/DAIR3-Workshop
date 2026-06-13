"""
file_upload_worker.py
QThread wrapper that runs an agent's process_file_upload off the GUI thread.

The wrapped callable should accept a single argument: a status_callback that
takes a string. The worker re-emits each status string as a Qt signal so the
GUI can update a progress label without blocking.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
from PyQt5.QtCore import QThread, pyqtSignal


class FileUploadWorker(QThread):
    status = pyqtSignal(str)
    finished_ok = pyqtSignal(str, object)   # response_text, usage_dict (may be None)
    finished_err = pyqtSignal(str)

    def __init__(self, run_callable):
        """run_callable: fn(status_cb: Callable[[str], None]) -> (response: str, usage: dict|None)"""
        super().__init__()
        self._run = run_callable

    def run(self):
        try:
            result = self._run(lambda msg: self.status.emit(msg))
            if isinstance(result, tuple) and len(result) == 2:
                response, usage = result
            else:
                response, usage = result, None
            self.finished_ok.emit(response, usage)
        except Exception as e:
            self.finished_err.emit(str(e))


def format_usage(usage):
    """Render a usage dict (any of 'input'/'output'/'total' / API-specific keys)
    as a short human-readable string. Returns '' if no useful info."""
    if not usage:
        return ""
    keys = {k.lower(): v for k, v in usage.items() if v is not None}
    inp = keys.get("input") or keys.get("input_tokens") or keys.get("prompt_token_count") or keys.get("prompt")
    out = keys.get("output") or keys.get("output_tokens") or keys.get("candidates_token_count") or keys.get("completion")
    tot = keys.get("total") or keys.get("total_tokens") or keys.get("total_token_count")
    parts = []
    if inp is not None:
        parts.append(f"in: {inp}")
    if out is not None:
        parts.append(f"out: {out}")
    if tot is not None and (inp is None or out is None):
        parts.append(f"total: {tot}")
    return " / ".join(parts)
