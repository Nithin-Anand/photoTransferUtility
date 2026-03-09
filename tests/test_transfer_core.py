"""Tests for app/core/transfer_core.py.

Focus: correct subfolder naming, extension filtering, callback contract,
copy vs move semantics, and dry-run no-op guarantee.
"""
import os
import pytest

from app.core.transfer_core import run_transfer, discover_extensions


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _touch(path: str) -> None:
    open(path, "w").close()


def _make_src(src_dir, files: list[str]) -> None:
    for f in files:
        _touch(os.path.join(str(src_dir), f))


# ------------------------------------------------------------------ #
# discover_extensions                                                 #
# ------------------------------------------------------------------ #

def test_discover_extensions_returns_present_extensions(tmp_path):
    _make_src(tmp_path, ["A.JPG", "B.RAF", "C.DNG"])
    assert discover_extensions(str(tmp_path)) == ["DNG", "JPG", "RAF"]


def test_discover_extensions_skips_hidden_files(tmp_path):
    _make_src(tmp_path, [".DS_Store", "A.JPG"])
    assert discover_extensions(str(tmp_path)) == ["JPG"]


def test_discover_extensions_skips_files_without_extension(tmp_path):
    _make_src(tmp_path, ["README", "A.JPG"])
    assert discover_extensions(str(tmp_path)) == ["JPG"]


def test_discover_extensions_deduplicates(tmp_path):
    _make_src(tmp_path, ["A.JPG", "B.JPG", "C.RAF"])
    result = discover_extensions(str(tmp_path))
    assert result == ["JPG", "RAF"]
    assert len(result) == 2


def test_discover_extensions_returns_uppercase(tmp_path):
    _make_src(tmp_path, ["a.jpg", "b.raf"])
    assert discover_extensions(str(tmp_path)) == ["JPG", "RAF"]


def test_discover_extensions_empty_folder(tmp_path):
    assert discover_extensions(str(tmp_path)) == []


def test_discover_extensions_unknown_camera_format(tmp_path):
    """Any extension gets transferred — no allow-list."""
    _make_src(tmp_path, ["CLIP001.ARW", "CLIP001.JPG"])   # Sony ARW
    assert discover_extensions(str(tmp_path)) == ["ARW", "JPG"]


# ------------------------------------------------------------------ #
# Subfolder naming                                                    #
# ------------------------------------------------------------------ #

def test_subfolder_named_after_dst_basename(tmp_path):
    """Files land in {dst_basename}_{ext.lower()}, e.g. March_jpg."""
    src = tmp_path / "src"
    dst = tmp_path / "March"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["DSCF0001.JPG", "DSCF0001.RAF"])

    run_transfer(str(src), str(dst), move=False, dry_run=False)

    assert (dst / "March_jpg" / "DSCF0001.JPG").exists()
    assert (dst / "March_raf" / "DSCF0001.RAF").exists()


def test_subfolder_uses_lowercase_extension(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "2026-March"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["A.MP4"])

    run_transfer(str(src), str(dst), move=False, dry_run=False)

    assert (dst / "2026-March_mp4").is_dir()


# ------------------------------------------------------------------ #
# Extension filtering                                                 #
# ------------------------------------------------------------------ #

def test_hidden_files_are_never_transferred(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["photo.JPG", ".DS_Store"])

    run_transfer(str(src), str(dst), move=False, dry_run=False)

    dst_files = {f for _, _, files in os.walk(str(dst)) for f in files}
    assert "photo.JPG" in dst_files
    assert ".DS_Store" not in dst_files


def test_extension_matching_is_case_insensitive(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["DSCF0001.jpg", "DSCF0002.JPG"])

    run_transfer(str(src), str(dst), move=False, dry_run=False)

    dst_files = {f for _, _, files in os.walk(str(dst)) for f in files}
    assert "DSCF0001.jpg" in dst_files
    assert "DSCF0002.JPG" in dst_files


def test_transfers_unexpected_extension_without_modification(tmp_path):
    """An unknown extension like ARW is transferred as-is into its own subfolder."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["CLIP.ARW"])

    run_transfer(str(src), str(dst), move=False, dry_run=False)

    assert (dst / "dst_arw" / "CLIP.ARW").exists()


# ------------------------------------------------------------------ #
# Copy vs Move                                                        #
# ------------------------------------------------------------------ #

def test_copy_keeps_source_file(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["DSCF0001.JPG"])

    run_transfer(str(src), str(dst), move=False, dry_run=False)

    assert (src / "DSCF0001.JPG").exists(), "copy should not remove source"


def test_move_removes_source_file(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["DSCF0001.JPG"])

    run_transfer(str(src), str(dst), move=True, dry_run=False)

    assert not (src / "DSCF0001.JPG").exists(), "move must remove source"
    assert (dst / "dst_jpg" / "DSCF0001.JPG").exists()


# ------------------------------------------------------------------ #
# Dry run                                                             #
# ------------------------------------------------------------------ #

def test_dry_run_creates_no_files(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["DSCF0001.JPG", "DSCF0001.RAF"])

    run_transfer(str(src), str(dst), move=False, dry_run=True)

    assert list(dst.iterdir()) == [], "dry_run must not create any files or dirs"


def test_dry_run_still_fires_callbacks(tmp_path):
    """Progress callbacks must fire even in dry_run so the UI can update."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["DSCF0001.JPG", "DSCF0002.JPG"])

    done_calls = []
    run_transfer(
        str(src), str(dst), move=False, dry_run=True,
        on_file_done=lambda ext, i, f: done_calls.append((ext, i, f)),
    )

    assert len(done_calls) == 2
    assert all(ext == "JPG" for ext, _, _ in done_calls)


# ------------------------------------------------------------------ #
# Callback contract                                                   #
# ------------------------------------------------------------------ #

def test_on_start_receives_total_count(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["A.JPG", "B.JPG", "C.JPG"])

    starts = {}
    run_transfer(str(src), str(dst), move=False, dry_run=False,
                 on_start=lambda ext, total: starts.update({ext: total}))

    assert starts["JPG"] == 3


def test_on_start_not_called_for_extensions_with_no_files(tmp_path):
    """on_start fires only for extensions that actually have files."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["A.JPG"])

    started_exts = []
    run_transfer(str(src), str(dst), move=False, dry_run=False,
                 on_start=lambda ext, total: started_exts.append(ext))

    assert started_exts == ["JPG"]


def test_on_file_done_index_is_one_based(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["A.RAF", "B.RAF"])

    indices = []
    run_transfer(str(src), str(dst), move=False, dry_run=False,
                 on_file_done=lambda ext, i, f: indices.append(i))

    assert sorted(indices) == [1, 2]


def test_on_ext_complete_receives_count(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["A.DNG", "B.DNG"])

    completes = {}
    run_transfer(str(src), str(dst), move=False, dry_run=False,
                 on_ext_complete=lambda ext, n: completes.update({ext: n}))

    assert completes["DNG"] == 2


# ------------------------------------------------------------------ #
# Summary return value                                                #
# ------------------------------------------------------------------ #

def test_summary_contains_only_discovered_extensions(tmp_path):
    """Summary keys reflect what was actually in the folder, not a fixed list."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _make_src(src, ["A.JPG", "B.JPG", "C.RAF"])

    summary = run_transfer(str(src), str(dst), move=False, dry_run=False)

    assert set(summary.keys()) == {"JPG", "RAF"}
    assert summary["JPG"] == 2
    assert summary["RAF"] == 1


def test_summary_empty_for_empty_folder(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()

    summary = run_transfer(str(src), str(dst), move=False, dry_run=False)
    assert summary == {}
