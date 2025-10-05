import os
from file_copy_gui import FileCopyMoveUtility
from pathlib import Path

from save_data_handler import SaveDataHandler

if __name__ == "__main__":
    settings_path = Path(__file__).parent / "user_settings.json"
    save_data_handler = SaveDataHandler(settings_path)

    app = FileCopyMoveUtility(save_data_handler)
    app.run()