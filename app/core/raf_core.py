import os


def derive_raf_folder(jpg_folder: str) -> str:
    """Derive the sibling RAF folder path from a JPG folder path.

    Raises ValueError if the folder name doesn't end in '_jpg' or ' JPG'.
    """
    if jpg_folder.endswith("_jpg"):
        return jpg_folder[:-4] + "_raf"
    elif jpg_folder.endswith(" JPG"):
        return jpg_folder[:-4] + " RAF"
    else:
        raise ValueError(
            f"Cannot derive RAF folder from '{jpg_folder}'. "
            "Folder name must end in '_jpg' or ' JPG'."
        )


def _stem(filename: str) -> str:
    """Return uppercase stem of a filename, without extension."""
    return os.path.splitext(filename)[0].upper()


# ------------------------------------------------------------------ #
# RAF cleaning (delete RAFs that have no matching JPG)               #
# ------------------------------------------------------------------ #

def preview_raf_deletion(jpg_folder: str) -> dict:
    """Return info about which RAF files would be deleted (no side effects).

    Orphaned RAFs are those in the sibling RAF folder with no matching JPG
    in jpg_folder.

    Returns:
        {
            "raf_folder": str,
            "files_to_delete": list[str],
            "error": str | None,
        }
    """
    try:
        raf_folder = derive_raf_folder(jpg_folder)
    except ValueError as e:
        return {"raf_folder": "", "files_to_delete": [], "error": str(e)}

    if not os.path.exists(raf_folder):
        return {
            "raf_folder": raf_folder,
            "files_to_delete": [],
            "error": f"RAF folder not found: {raf_folder}",
        }

    jpg_stems = {_stem(f) for f in os.listdir(jpg_folder)}
    raf_files = [f for f in os.listdir(raf_folder) if os.path.splitext(f)[1].upper() == ".RAF"]
    files_to_delete = sorted(f for f in raf_files if _stem(f) not in jpg_stems)

    return {"raf_folder": raf_folder, "files_to_delete": files_to_delete, "error": None}


def execute_raf_deletion(jpg_folder: str, dry_run: bool) -> dict:
    """Delete orphaned RAF files (those without a matching JPG).

    Returns:
        {
            "raf_folder": str,
            "deleted": list[str],
            "dry_run": bool,
            "error": str | None,
        }
    """
    preview = preview_raf_deletion(jpg_folder)
    if preview["error"]:
        return {
            "raf_folder": preview["raf_folder"],
            "deleted": [],
            "dry_run": dry_run,
            "error": preview["error"],
        }

    raf_folder = preview["raf_folder"]
    files_to_delete = preview["files_to_delete"]
    deleted = []

    if not dry_run:
        for filename in files_to_delete:
            os.remove(os.path.join(raf_folder, filename))
            deleted.append(filename)
    else:
        deleted = list(files_to_delete)

    return {"raf_folder": raf_folder, "deleted": deleted, "dry_run": dry_run, "error": None}


# ------------------------------------------------------------------ #
# JPG cleaning (delete JPGs that have no matching RAF)               #
# ------------------------------------------------------------------ #

def preview_jpg_deletion(jpg_folder: str) -> dict:
    """Return info about which JPG files would be deleted (no side effects).

    Orphaned JPGs are those in jpg_folder with no matching RAF in the
    sibling RAF folder.

    Returns:
        {
            "jpg_folder": str,
            "files_to_delete": list[str],
            "error": str | None,
        }
    """
    try:
        raf_folder = derive_raf_folder(jpg_folder)
    except ValueError as e:
        return {"jpg_folder": jpg_folder, "files_to_delete": [], "error": str(e)}

    if not os.path.exists(raf_folder):
        return {
            "jpg_folder": jpg_folder,
            "files_to_delete": [],
            "error": f"RAF folder not found: {raf_folder}",
        }

    raf_stems = {
        _stem(f) for f in os.listdir(raf_folder)
        if os.path.splitext(f)[1].upper() == ".RAF"
    }
    jpg_files = [f for f in os.listdir(jpg_folder) if os.path.splitext(f)[1].upper() == ".JPG"]
    files_to_delete = sorted(f for f in jpg_files if _stem(f) not in raf_stems)

    return {"jpg_folder": jpg_folder, "files_to_delete": files_to_delete, "error": None}


def execute_jpg_deletion(jpg_folder: str, dry_run: bool) -> dict:
    """Delete orphaned JPG files (those without a matching RAF).

    Returns:
        {
            "jpg_folder": str,
            "deleted": list[str],
            "dry_run": bool,
            "error": str | None,
        }
    """
    preview = preview_jpg_deletion(jpg_folder)
    if preview["error"]:
        return {
            "jpg_folder": preview["jpg_folder"],
            "deleted": [],
            "dry_run": dry_run,
            "error": preview["error"],
        }

    files_to_delete = preview["files_to_delete"]
    deleted = []

    if not dry_run:
        for filename in files_to_delete:
            os.remove(os.path.join(jpg_folder, filename))
            deleted.append(filename)
    else:
        deleted = list(files_to_delete)

    return {"jpg_folder": jpg_folder, "deleted": deleted, "dry_run": dry_run, "error": None}
