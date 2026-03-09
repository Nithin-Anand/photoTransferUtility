from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QCheckBox, QProgressBar, QFileDialog,
    QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt

from app.settings import SettingsManager
from app.workers.transfer_worker import TransferWorker
from app.core.transfer_core import discover_extensions


class TransferTab(QWidget):
    def __init__(self, settings: SettingsManager) -> None:
        super().__init__()
        self.settings = settings
        self._worker: TransferWorker | None = None
        self._progress_bars: dict[str, QProgressBar] = {}
        self._progress_labels: dict[str, QLabel] = {}
        self._progress_row_widgets: list[QWidget] = []

        self._build_ui()
        self._load_recents()

    # ------------------------------------------------------------------ #
    # UI construction                                                      #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # Source row
        self._src_combo = QComboBox()
        self._src_combo.setEditable(True)
        self._src_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        src_browse = QPushButton("Browse…")
        src_browse.clicked.connect(self._browse_src)
        root.addLayout(self._labeled_row("Source Folder", self._src_combo, src_browse))

        # Destination row
        self._dst_combo = QComboBox()
        self._dst_combo.setEditable(True)
        self._dst_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dst_browse = QPushButton("Browse…")
        dst_browse.clicked.connect(self._browse_dst)
        root.addLayout(self._labeled_row("Dest Folder", self._dst_combo, dst_browse))

        # Options
        opts = QHBoxLayout()
        self._move_chk = QCheckBox("Move files (instead of copy)")
        self._dry_run_chk = QCheckBox("Dry Run")
        opts.addWidget(self._move_chk)
        opts.addSpacing(20)
        opts.addWidget(self._dry_run_chk)
        opts.addStretch()
        root.addLayout(opts)

        # Start button
        self._start_btn = QPushButton("Start Transfer")
        self._start_btn.setFixedHeight(36)
        self._start_btn.clicked.connect(self._start_transfer)
        root.addWidget(self._start_btn)

        # Progress section — populated dynamically per transfer
        self._progress_widget = QWidget()
        self._prog_layout = QVBoxLayout(self._progress_widget)
        self._prog_layout.setContentsMargins(0, 8, 0, 0)
        self._prog_layout.setSpacing(6)

        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._prog_layout.addWidget(self._status_label)

        self._progress_widget.hide()
        root.addWidget(self._progress_widget)
        root.addStretch()

    def _setup_progress_bars(self, extensions: list[str]) -> None:
        """Rebuild progress bars to match the extensions found in src."""
        for w in self._progress_row_widgets:
            self._prog_layout.removeWidget(w)
            w.deleteLater()
        self._progress_row_widgets.clear()
        self._progress_bars.clear()
        self._progress_labels.clear()

        # Re-insert status label at end after adding new rows
        self._prog_layout.removeWidget(self._status_label)

        for ext in extensions:
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            ext_lbl = QLabel(ext)
            ext_lbl.setFixedWidth(40)
            bar = QProgressBar()
            bar.setTextVisible(False)
            count_lbl = QLabel("—")
            count_lbl.setFixedWidth(60)
            rl.addWidget(ext_lbl)
            rl.addWidget(bar)
            rl.addWidget(count_lbl)
            self._prog_layout.addWidget(row)
            self._progress_bars[ext] = bar
            self._progress_labels[ext] = count_lbl
            self._progress_row_widgets.append(row)

        self._prog_layout.addWidget(self._status_label)

    @staticmethod
    def _labeled_row(label: str, combo: QComboBox, btn: QPushButton) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(100)
        row.addWidget(lbl)
        row.addWidget(combo)
        row.addWidget(btn)
        return row

    # ------------------------------------------------------------------ #
    # Recent paths                                                         #
    # ------------------------------------------------------------------ #

    def _load_recents(self) -> None:
        self._src_combo.addItems(self.settings.recent_sources)
        self._dst_combo.addItems(self.settings.recent_destinations)

    # ------------------------------------------------------------------ #
    # Browse                                                               #
    # ------------------------------------------------------------------ #

    def _browse_src(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if path:
            self._src_combo.setCurrentText(path)

    def _browse_dst(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if path:
            self._dst_combo.setCurrentText(path)

    # ------------------------------------------------------------------ #
    # Transfer                                                             #
    # ------------------------------------------------------------------ #

    def _start_transfer(self) -> None:
        src = self._src_combo.currentText().strip()
        dst = self._dst_combo.currentText().strip()

        if not src or not dst:
            QMessageBox.warning(self, "Missing paths", "Please select both source and destination folders.")
            return

        extensions = discover_extensions(src)
        if not extensions:
            QMessageBox.warning(self, "Empty folder", "No files found in the source folder.")
            return

        self.settings.add_recent_source(src)
        self.settings.add_recent_destination(dst)
        self._sync_combo(self._src_combo, self.settings.recent_sources)
        self._sync_combo(self._dst_combo, self.settings.recent_destinations)

        self._setup_progress_bars(extensions)
        self._status_label.setText("")
        self._progress_widget.show()
        self._start_btn.setEnabled(False)

        self._worker = TransferWorker(src, dst, self._move_chk.isChecked(), self._dry_run_chk.isChecked())
        self._worker.ext_started.connect(self._on_ext_started)
        self._worker.file_done.connect(self._on_file_done)
        self._worker.ext_complete.connect(self._on_ext_complete)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @staticmethod
    def _sync_combo(combo: QComboBox, items: list[str]) -> None:
        current = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(items)
        combo.setCurrentText(current)
        combo.blockSignals(False)

    # ------------------------------------------------------------------ #
    # Worker slots                                                         #
    # ------------------------------------------------------------------ #

    def _on_ext_started(self, ext: str, total: int) -> None:
        bar = self._progress_bars[ext]
        bar.setMaximum(total)
        bar.setValue(0)
        self._progress_labels[ext].setText(f"0 / {total}")

    def _on_file_done(self, ext: str, current: int, filename: str) -> None:
        bar = self._progress_bars[ext]
        bar.setValue(current)
        total = bar.maximum()
        self._progress_labels[ext].setText(f"{current} / {total}")
        self._status_label.setText(f"{'Moving' if self._move_chk.isChecked() else 'Copying'} {filename}…")

    def _on_ext_complete(self, ext: str, count: int) -> None:
        self._progress_labels[ext].setText(str(count))

    def _on_finished(self, summary: dict) -> None:
        self._start_btn.setEnabled(True)
        dry = self._dry_run_chk.isChecked()
        msg = "Dry run complete — no files were moved." if dry else "Transfer complete."
        details = "\n".join(f"{ext}: {n} files" for ext, n in summary.items() if n > 0)
        self._status_label.setText(msg)
        QMessageBox.information(self, "Done", f"{msg}\n\n{details}" if details else msg)

    def _on_error(self, message: str) -> None:
        self._start_btn.setEnabled(True)
        self._status_label.setText(f"Error: {message}")
        QMessageBox.critical(self, "Transfer Error", message)
