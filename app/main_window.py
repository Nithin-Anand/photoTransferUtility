from PyQt6.QtWidgets import QMainWindow, QTabWidget

from app.settings import SettingsManager
from app.tabs.transfer_tab import TransferTab
from app.tabs.raf_cleaner_tab import RafCleanerTab


class MainWindow(QMainWindow):
    def __init__(self, settings: SettingsManager) -> None:
        super().__init__()
        self.settings = settings
        self.setWindowTitle("Photo Transfer Utility")
        self.resize(700, 500)

        tabs = QTabWidget()
        tabs.addTab(TransferTab(settings), "Transfer Photos")
        tabs.addTab(RafCleanerTab(settings), "RAF Cleaner")
        self.setCentralWidget(tabs)
