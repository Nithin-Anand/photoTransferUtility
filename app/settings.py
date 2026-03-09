import json
from pathlib import Path

_MAX_RECENT = 5

_DEFAULT: dict = {
    "transfer": {
        "recent_sources": [],
        "recent_destinations": [],
    },
    "raf_cleaner": {
        "recent_folders": [],
    },
}


class SettingsManager:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict = {}
        self._load()

    # ------------------------------------------------------------------ #
    # Public accessors                                                     #
    # ------------------------------------------------------------------ #

    @property
    def recent_sources(self) -> list[str]:
        return self._data["transfer"]["recent_sources"]

    @property
    def recent_destinations(self) -> list[str]:
        return self._data["transfer"]["recent_destinations"]

    @property
    def recent_raf_folders(self) -> list[str]:
        return self._data["raf_cleaner"]["recent_folders"]

    def add_recent_source(self, path: str) -> None:
        self._prepend("transfer", "recent_sources", path)

    def add_recent_destination(self, path: str) -> None:
        self._prepend("transfer", "recent_destinations", path)

    def add_recent_raf_folder(self, path: str) -> None:
        self._prepend("raf_cleaner", "recent_folders", path)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _prepend(self, section: str, key: str, value: str) -> None:
        lst: list[str] = self._data[section][key]
        if value in lst:
            lst.remove(value)
        lst.insert(0, value)
        self._data[section][key] = lst[:_MAX_RECENT]
        self._save()

    def _load(self) -> None:
        import copy
        self._data = copy.deepcopy(_DEFAULT)
        if self._path.exists():
            try:
                with self._path.open("r", encoding="utf-8") as f:
                    saved = json.load(f)
                for section in _DEFAULT:
                    if section in saved:
                        for key in _DEFAULT[section]:
                            if key in saved[section]:
                                self._data[section][key] = saved[section][key]
            except (json.JSONDecodeError, KeyError):
                pass  # corrupt file — start fresh

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
