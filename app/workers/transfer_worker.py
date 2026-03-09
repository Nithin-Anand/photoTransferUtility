from PyQt6.QtCore import QThread, pyqtSignal
from app.core.transfer_core import run_transfer


class TransferWorker(QThread):
    ext_started = pyqtSignal(str, int)    # (ext, total)
    file_done = pyqtSignal(str, int, str) # (ext, current, filename)
    ext_complete = pyqtSignal(str, int)   # (ext, count)
    finished = pyqtSignal(dict)           # summary {ext: count}
    error = pyqtSignal(str)               # error message

    def __init__(self, src: str, dst: str, move: bool, dry_run: bool) -> None:
        super().__init__()
        self.src = src
        self.dst = dst
        self.move = move
        self.dry_run = dry_run

    def run(self) -> None:
        try:
            summary = run_transfer(
                self.src,
                self.dst,
                self.move,
                self.dry_run,
                on_start=lambda ext, total: self.ext_started.emit(ext, total),
                on_file_done=lambda ext, i, f: self.file_done.emit(ext, i, f),
                on_ext_complete=lambda ext, n: self.ext_complete.emit(ext, n),
            )
            self.finished.emit(summary)
        except Exception as e:
            self.error.emit(str(e))
