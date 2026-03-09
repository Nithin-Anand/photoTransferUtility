"""Tests for app/core/raf_core.py.

Focus: pairing correctness, mutation safety (dry-run truly no-ops),
extension-case robustness, and the bug-fixed folder derivation.
"""
import os
import pytest

from app.core.raf_core import (
    derive_raf_folder,
    preview_raf_deletion,
    execute_raf_deletion,
    preview_jpg_deletion,
    execute_jpg_deletion,
)


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _touch(path: str) -> None:
    open(path, "w").close()


def _make_paired_set(jpg_dir: str, raf_dir: str, stems: list[str]) -> None:
    """Create matching JPG+RAF pairs."""
    for stem in stems:
        _touch(os.path.join(jpg_dir, f"{stem}.JPG"))
        _touch(os.path.join(raf_dir, f"{stem}.RAF"))


# ------------------------------------------------------------------ #
# derive_raf_folder                                                   #
# ------------------------------------------------------------------ #

def test_derive_raf_folder_underscore():
    assert derive_raf_folder("/photos/March_jpg") == "/photos/March_raf"


def test_derive_raf_folder_space():
    assert derive_raf_folder("/photos/March JPG") == "/photos/March RAF"


def test_derive_raf_folder_invalid_raises():
    with pytest.raises(ValueError, match="bad_name"):
        derive_raf_folder("/photos/bad_name")


def test_derive_raf_folder_does_not_match_partial_suffix():
    # "_jpg" only valid at the END
    with pytest.raises(ValueError):
        derive_raf_folder("/photos/_jpg_extra")


# ------------------------------------------------------------------ #
# RAF deletion – preview                                              #
# ------------------------------------------------------------------ #

def test_preview_raf_deletion_invalid_folder_name_returns_error(tmp_path):
    result = preview_raf_deletion(str(tmp_path / "bad_name"))
    assert result["error"] is not None
    assert result["files_to_delete"] == []


def test_preview_raf_deletion_missing_raf_folder(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    jpg_dir.mkdir()
    result = preview_raf_deletion(str(jpg_dir))
    assert "not found" in result["error"]
    assert result["files_to_delete"] == []


def test_preview_raf_deletion_all_paired_returns_empty(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()
    _make_paired_set(str(jpg_dir), str(raf_dir), ["DSCF0001", "DSCF0002"])

    result = preview_raf_deletion(str(jpg_dir))
    assert result["error"] is None
    assert result["files_to_delete"] == []


def test_preview_raf_deletion_identifies_orphaned_rafs(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()

    # Paired
    _make_paired_set(str(jpg_dir), str(raf_dir), ["DSCF0001"])
    # Orphaned RAFs (no JPG counterpart)
    _touch(str(raf_dir / "DSCF0002.RAF"))
    _touch(str(raf_dir / "DSCF0003.RAF"))

    result = preview_raf_deletion(str(jpg_dir))
    assert result["error"] is None
    assert sorted(result["files_to_delete"]) == ["DSCF0002.RAF", "DSCF0003.RAF"]


def test_preview_raf_deletion_lowercase_raf_extension(tmp_path):
    """Cameras sometimes write .raf; pairing should still work."""
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()

    _touch(str(jpg_dir / "DSCF0001.JPG"))
    _touch(str(raf_dir / "DSCF0001.raf"))   # lowercase ext
    _touch(str(raf_dir / "DSCF0002.raf"))   # orphan, lowercase ext

    result = preview_raf_deletion(str(jpg_dir))
    assert result["error"] is None
    assert result["files_to_delete"] == ["DSCF0002.raf"]


# ------------------------------------------------------------------ #
# RAF deletion – execute                                              #
# ------------------------------------------------------------------ #

def test_execute_raf_deletion_dry_run_leaves_files_intact(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()
    _touch(str(raf_dir / "DSCF0001.RAF"))   # orphan

    result = execute_raf_deletion(str(jpg_dir), dry_run=True)
    assert result["dry_run"] is True
    assert "DSCF0001.RAF" in result["deleted"]
    assert (raf_dir / "DSCF0001.RAF").exists(), "dry_run must not delete files"


def test_execute_raf_deletion_real_run_removes_only_orphans(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()
    _make_paired_set(str(jpg_dir), str(raf_dir), ["DSCF0001"])
    _touch(str(raf_dir / "DSCF0002.RAF"))   # orphan

    result = execute_raf_deletion(str(jpg_dir), dry_run=False)
    assert result["error"] is None
    assert result["deleted"] == ["DSCF0002.RAF"]
    assert (raf_dir / "DSCF0001.RAF").exists(), "paired RAF must be kept"
    assert not (raf_dir / "DSCF0002.RAF").exists(), "orphan RAF must be deleted"


def test_execute_raf_deletion_propagates_error(tmp_path):
    result = execute_raf_deletion(str(tmp_path / "bad_name"), dry_run=False)
    assert result["error"] is not None
    assert result["deleted"] == []


# ------------------------------------------------------------------ #
# JPG deletion – preview                                              #
# ------------------------------------------------------------------ #

def test_preview_jpg_deletion_invalid_folder_name_returns_error(tmp_path):
    result = preview_jpg_deletion(str(tmp_path / "bad_name"))
    assert result["error"] is not None
    assert result["files_to_delete"] == []


def test_preview_jpg_deletion_missing_raf_folder(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    jpg_dir.mkdir()
    result = preview_jpg_deletion(str(jpg_dir))
    assert "not found" in result["error"]


def test_preview_jpg_deletion_all_paired_returns_empty(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()
    _make_paired_set(str(jpg_dir), str(raf_dir), ["DSCF0001", "DSCF0002"])

    result = preview_jpg_deletion(str(jpg_dir))
    assert result["error"] is None
    assert result["files_to_delete"] == []


def test_preview_jpg_deletion_identifies_orphaned_jpgs(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()

    # Paired
    _make_paired_set(str(jpg_dir), str(raf_dir), ["DSCF0001"])
    # Orphaned JPGs (no RAF counterpart)
    _touch(str(jpg_dir / "DSCF0002.JPG"))
    _touch(str(jpg_dir / "DSCF0003.JPG"))

    result = preview_jpg_deletion(str(jpg_dir))
    assert result["error"] is None
    assert sorted(result["files_to_delete"]) == ["DSCF0002.JPG", "DSCF0003.JPG"]


def test_preview_jpg_deletion_ignores_non_jpg_files(tmp_path):
    """Non-JPG files in the folder (e.g. .xmp sidecars) are never candidates."""
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()

    _touch(str(jpg_dir / "DSCF0001.JPG"))   # orphan JPG
    _touch(str(jpg_dir / "DSCF0001.xmp"))   # sidecar, should be ignored
    _touch(str(raf_dir / "DSCF0099.RAF"))   # unrelated RAF

    result = preview_jpg_deletion(str(jpg_dir))
    assert result["files_to_delete"] == ["DSCF0001.JPG"]


# ------------------------------------------------------------------ #
# JPG deletion – execute                                              #
# ------------------------------------------------------------------ #

def test_execute_jpg_deletion_dry_run_leaves_files_intact(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()
    _touch(str(jpg_dir / "DSCF0001.JPG"))   # orphan

    result = execute_jpg_deletion(str(jpg_dir), dry_run=True)
    assert result["dry_run"] is True
    assert "DSCF0001.JPG" in result["deleted"]
    assert (jpg_dir / "DSCF0001.JPG").exists(), "dry_run must not delete files"


def test_execute_jpg_deletion_real_run_removes_only_orphans(tmp_path):
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()
    _make_paired_set(str(jpg_dir), str(raf_dir), ["DSCF0001"])
    _touch(str(jpg_dir / "DSCF0002.JPG"))   # orphan

    result = execute_jpg_deletion(str(jpg_dir), dry_run=False)
    assert result["error"] is None
    assert result["deleted"] == ["DSCF0002.JPG"]
    assert (jpg_dir / "DSCF0001.JPG").exists(), "paired JPG must be kept"
    assert not (jpg_dir / "DSCF0002.JPG").exists(), "orphan JPG must be deleted"


# ------------------------------------------------------------------ #
# Symmetry: paired files are NEVER touched by either direction        #
# ------------------------------------------------------------------ #

def test_paired_files_survive_both_cleaners(tmp_path):
    """Running both RAF and JPG cleaners on a fully-paired set deletes nothing."""
    jpg_dir = tmp_path / "March_jpg"
    raf_dir = tmp_path / "March_raf"
    jpg_dir.mkdir(); raf_dir.mkdir()
    stems = ["DSCF0001", "DSCF0002", "DSCF0003"]
    _make_paired_set(str(jpg_dir), str(raf_dir), stems)

    execute_raf_deletion(str(jpg_dir), dry_run=False)
    execute_jpg_deletion(str(jpg_dir), dry_run=False)

    for stem in stems:
        assert (jpg_dir / f"{stem}.JPG").exists()
        assert (raf_dir / f"{stem}.RAF").exists()
