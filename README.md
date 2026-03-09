# Photo Transfer Utility

A desktop application for importing photos from a camera's SD card and cleaning up orphaned RAW/JPEG pairs afterward. Built with PyQt6.

## Features

### Transfer Photos

Copies or moves all files from a source folder to a destination folder, automatically sorting them into subfolders by file extension. For example, transferring into a folder called `March` produces:

```
March/
  March_jpg/
  March_raf/
  March_mov/
```

Hidden files (`.DS_Store`, etc.) are excluded. Progress is shown per file type, and the UI remains responsive during transfer.

Options:
- **Move files** — deletes originals after copying (defaults to copy)
- **Dry run** — shows what would happen without touching any files

### RAF Cleaner

When shooting in RAW+JPEG on a Fujifilm camera, you may later delete some JPEGs in Lightroom and want to remove the corresponding RAFs (or vice versa). This tab handles that cleanup.

Point it at a JPG folder (e.g. `March_jpg`) and it will locate the sibling RAF folder (`March_raf`) automatically. You can then:

- **Preview orphaned RAFs** — lists RAF files that have no matching JPEG
- **Clean RAF files** — deletes those orphaned RAFs
- **Preview orphaned JPGs** — lists JPEGs that have no matching RAF
- **Clean JPG files** — deletes those orphaned JPEGs

Both preview and clean operations support a **Dry Run** mode. A confirmation dialog is shown before any real deletion.

**Folder naming convention required:** the JPG folder must end in `_jpg` or ` JPG`. The RAF folder is expected to be a sibling with the same base name ending in `_raf` or ` RAF`.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

## Setup

```bash
uv sync
```

## Running

```bash
uv run python main.py
```

## Project structure

```
app/
  core/
    transfer_core.py   # file discovery and copy/move logic
    raf_core.py        # orphaned file detection and deletion
  tabs/
    transfer_tab.py    # Transfer Photos UI
    raf_cleaner_tab.py # RAF Cleaner UI
  workers/
    transfer_worker.py # QThread wrapper for transfer operations
  main_window.py       # top-level window with tab container
  settings.py          # persistent settings (recent paths)
main.py                # entry point
```

Settings are written to `app_settings.json` alongside `main.py`. The five most recently used paths are remembered per field.

## Running tests

```bash
uv run pytest
```
