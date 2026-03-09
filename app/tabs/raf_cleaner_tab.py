from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QCheckBox, QListWidget, QFileDialog,
    QMessageBox, QSizePolicy, QFrame,
)

from app.settings import SettingsManager
from app.core.raf_core import (
    preview_raf_deletion, execute_raf_deletion,
    preview_jpg_deletion, execute_jpg_deletion,
)


class RafCleanerTab(QWidget):
    def __init__(self, settings: SettingsManager) -> None:
        super().__init__()
        self.settings = settings
        self._build_ui()
        self._load_recents()

    # ------------------------------------------------------------------ #
    # UI construction                                                      #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # Folder row
        self._folder_combo = QComboBox()
        self._folder_combo.setEditable(True)
        self._folder_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_folder)

        row = QHBoxLayout()
        lbl = QLabel("JPG Folder")
        lbl.setFixedWidth(100)
        row.addWidget(lbl)
        row.addWidget(self._folder_combo)
        row.addWidget(browse_btn)
        root.addLayout(row)

        # Dry run
        self._dry_run_chk = QCheckBox("Dry Run")
        root.addWidget(self._dry_run_chk)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        root.addWidget(sep)

        # RAF-cleaning buttons
        raf_row = QHBoxLayout()
        raf_lbl = QLabel("Orphaned RAFs:")
        raf_lbl.setFixedWidth(120)
        self._preview_raf_btn = QPushButton("Preview")
        self._preview_raf_btn.clicked.connect(self._preview_rafs)
        self._clean_raf_btn = QPushButton("Clean RAF Files")
        self._clean_raf_btn.clicked.connect(self._clean_rafs)
        raf_row.addWidget(raf_lbl)
        raf_row.addWidget(self._preview_raf_btn)
        raf_row.addWidget(self._clean_raf_btn)
        raf_row.addStretch()
        root.addLayout(raf_row)

        # JPG-cleaning buttons
        jpg_row = QHBoxLayout()
        jpg_lbl = QLabel("Orphaned JPGs:")
        jpg_lbl.setFixedWidth(120)
        self._preview_jpg_btn = QPushButton("Preview")
        self._preview_jpg_btn.clicked.connect(self._preview_jpgs)
        self._clean_jpg_btn = QPushButton("Clean JPG Files")
        self._clean_jpg_btn.clicked.connect(self._clean_jpgs)
        jpg_row.addWidget(jpg_lbl)
        jpg_row.addWidget(self._preview_jpg_btn)
        jpg_row.addWidget(self._clean_jpg_btn)
        jpg_row.addStretch()
        root.addLayout(jpg_row)

        # Result area
        self._folder_label = QLabel("")
        root.addWidget(self._folder_label)

        self._list_widget = QListWidget()
        root.addWidget(self._list_widget)

    # ------------------------------------------------------------------ #
    # Recent paths                                                         #
    # ------------------------------------------------------------------ #

    def _load_recents(self) -> None:
        self._folder_combo.addItems(self.settings.recent_raf_folders)

    # ------------------------------------------------------------------ #
    # Browse                                                               #
    # ------------------------------------------------------------------ #

    def _browse_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select JPG Folder")
        if path:
            self._folder_combo.setCurrentText(path)

    # ------------------------------------------------------------------ #
    # RAF operations                                                       #
    # ------------------------------------------------------------------ #

    def _current_folder(self) -> str | None:
        folder = self._folder_combo.currentText().strip()
        if not folder:
            QMessageBox.warning(self, "No folder", "Please select a JPG folder.")
            return None
        return folder

    def _preview_rafs(self) -> None:
        folder = self._current_folder()
        if folder:
            self._show_result(preview_raf_deletion(folder), mode="raf")

    def _clean_rafs(self) -> None:
        folder = self._current_folder()
        if not folder:
            return
        dry_run = self._dry_run_chk.isChecked()
        if not dry_run and not self._confirm("permanently delete orphaned RAF files"):
            return
        self._save_recent(folder)
        self._show_result(execute_raf_deletion(folder, dry_run), mode="raf", executed=True)

    # ------------------------------------------------------------------ #
    # JPG operations                                                       #
    # ------------------------------------------------------------------ #

    def _preview_jpgs(self) -> None:
        folder = self._current_folder()
        if folder:
            self._show_result(preview_jpg_deletion(folder), mode="jpg")

    def _clean_jpgs(self) -> None:
        folder = self._current_folder()
        if not folder:
            return
        dry_run = self._dry_run_chk.isChecked()
        if not dry_run and not self._confirm("permanently delete orphaned JPG files"):
            return
        self._save_recent(folder)
        self._show_result(execute_jpg_deletion(folder, dry_run), mode="jpg", executed=True)

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _confirm(self, action_description: str) -> bool:
        answer = QMessageBox.question(
            self,
            "Confirm deletion",
            f"This will {action_description}. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def _save_recent(self, folder: str) -> None:
        self.settings.add_recent_raf_folder(folder)
        self._sync_combo(self._folder_combo, self.settings.recent_raf_folders)

    def _show_result(self, result: dict, mode: str, executed: bool = False) -> None:
        self._list_widget.clear()

        if result["error"]:
            QMessageBox.warning(self, "Error", result["error"])
            return

        if mode == "raf":
            folder_path = result["raf_folder"]
            folder_label = f"RAF folder: {folder_path}"
        else:
            folder_path = result["jpg_folder"]
            folder_label = f"JPG folder: {folder_path}"

        self._folder_label.setText(folder_label)

        files = result.get("files_to_delete", result.get("deleted", []))
        dry_run = result.get("dry_run", False)

        if executed and not dry_run:
            header = f"Deleted ({len(files)}):"
        elif dry_run:
            header = f"Would delete ({len(files)}):"
        else:
            header = f"Files to delete ({len(files)}):"

        self._list_widget.addItem(header)
        for f in files:
            self._list_widget.addItem(f"  {f}")
        if not files:
            self._list_widget.addItem("  (none)")

    @staticmethod
    def _sync_combo(combo: QComboBox, items: list[str]) -> None:
        current = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(items)
        combo.setCurrentText(current)
        combo.blockSignals(False)
