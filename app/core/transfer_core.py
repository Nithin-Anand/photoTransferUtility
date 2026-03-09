import os
import shutil
from typing import Callable


def discover_extensions(src: str) -> list[str]:
    """Return sorted unique uppercase extensions of non-hidden files in src.

    Hidden files (names starting with '.') are skipped so that macOS
    metadata files like .DS_Store never become transfer candidates.
    """
    exts: set[str] = set()
    for f in os.listdir(src):
        if f.startswith("."):
            continue
        _, ext = os.path.splitext(f)
        if ext:
            exts.add(ext.lstrip(".").upper())
    return sorted(exts)


def run_transfer(
    src: str,
    dst: str,
    move: bool,
    dry_run: bool,
    on_start: Callable[[str, int], None] | None = None,
    on_file_done: Callable[[str, int, str], None] | None = None,
    on_ext_complete: Callable[[str, int], None] | None = None,
) -> dict[str, int]:
    """Copy or move files from src to dst, organised by extension into subfolders.

    Extensions are discovered from src at runtime — no hard-coded list.
    Subfolder naming: {basename(dst)}_{ext.lower()}  e.g. March_jpg

    Returns a dict mapping each discovered extension to the number of files processed.
    """
    summary: dict[str, int] = {}

    for ext in discover_extensions(src):
        full_ext = f".{ext}"
        desired = [
            f for f in os.listdir(src)
            if not f.startswith(".") and os.path.splitext(f)[1].upper() == full_ext
        ]

        if not desired:
            summary[ext] = 0
            continue

        dst_subfolder = f"{os.path.basename(dst)}_{ext.lower()}"
        dst_path = os.path.join(dst, dst_subfolder)

        if on_start:
            on_start(ext, len(desired))

        if not dry_run:
            os.makedirs(dst_path, exist_ok=True)

        for i, filename in enumerate(desired, start=1):
            src_file = os.path.join(src, filename)
            dst_file = os.path.join(dst_path, filename)
            if not dry_run:
                if move:
                    shutil.move(src_file, dst_file)
                else:
                    shutil.copy2(src_file, dst_file)
            if on_file_done:
                on_file_done(ext, i, filename)

        summary[ext] = len(desired)
        if on_ext_complete:
            on_ext_complete(ext, len(desired))

    return summary
