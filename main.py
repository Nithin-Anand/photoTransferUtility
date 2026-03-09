import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow
from app.settings import SettingsManager

if __name__ == "__main__":
    settings_path = Path(__file__).parent / "app_settings.json"
    settings = SettingsManager(settings_path)

    app = QApplication(sys.argv)
    window = MainWindow(settings)
    window.show()
    sys.exit(app.exec())
