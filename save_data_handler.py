import json
from loguru import logger
from pathlib import Path

class SaveDataHandler:

    def __init__(self, settings_file_location: Path):
        self.source_path = ""
        self.destination_path = ""
        self.settings_file_location = settings_file_location

        try:
            with open(self.settings_file_location, "r", encoding="utf-8") as f:
                settings_data = json.load(f)
                self.source_path = settings_data.get("source_path", "")
                self.destination_path = settings_data.get("destination_path", "")

                logger.info(f"Loaded settings from {self.settings_file_location}")

        except FileNotFoundError:
            logger.warning(f"Settings file not present at {self.settings_file_location}.")

        except json.JSONDecodeError:
            logger.warning(f"Settings file at {self.settings_file_location} is corrupted or not valid JSON.")

    def update_settings(self, source_path: str, destination_path: str):
        self.source_path = source_path
        self.destination_path = destination_path
        self._persist_settings()

    def _persist_settings(self):
        settings_data = {
            "source_path": self.source_path,
            "destination_path": self.destination_path
        }
        with open(self.settings_file_location, "w") as f:
            json.dump(settings_data, f, indent=4)
            logger.info(f"Settings saved to {self.settings_file_location}")