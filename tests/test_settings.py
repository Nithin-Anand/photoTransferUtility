"""Tests for app/settings.py (SettingsManager).

Focus: prepend/dedup/cap semantics, persistence across reloads,
and graceful handling of corrupt or missing files.
"""
import json
import pytest
from pathlib import Path

from app.settings import SettingsManager


# ------------------------------------------------------------------ #
# Fresh state                                                         #
# ------------------------------------------------------------------ #

def test_fresh_settings_has_empty_lists(tmp_path):
    sm = SettingsManager(tmp_path / "settings.json")
    assert sm.recent_sources == []
    assert sm.recent_destinations == []
    assert sm.recent_raf_folders == []


def test_missing_file_does_not_raise(tmp_path):
    """SettingsManager must not raise when the file doesn't exist yet."""
    SettingsManager(tmp_path / "nonexistent.json")  # should not raise


# ------------------------------------------------------------------ #
# Prepend semantics                                                   #
# ------------------------------------------------------------------ #

def test_add_recent_source_prepends(tmp_path):
    sm = SettingsManager(tmp_path / "s.json")
    sm.add_recent_source("/a")
    sm.add_recent_source("/b")
    assert sm.recent_sources == ["/b", "/a"]


def test_add_recent_destination_prepends(tmp_path):
    sm = SettingsManager(tmp_path / "s.json")
    sm.add_recent_destination("/x")
    sm.add_recent_destination("/y")
    assert sm.recent_destinations == ["/y", "/x"]


def test_add_recent_raf_folder_prepends(tmp_path):
    sm = SettingsManager(tmp_path / "s.json")
    sm.add_recent_raf_folder("/r1")
    sm.add_recent_raf_folder("/r2")
    assert sm.recent_raf_folders == ["/r2", "/r1"]


# ------------------------------------------------------------------ #
# Deduplication                                                       #
# ------------------------------------------------------------------ #

def test_duplicate_moves_to_front(tmp_path):
    sm = SettingsManager(tmp_path / "s.json")
    sm.add_recent_source("/a")
    sm.add_recent_source("/b")
    sm.add_recent_source("/a")   # re-adding /a
    assert sm.recent_sources == ["/a", "/b"]
    assert sm.recent_sources.count("/a") == 1


# ------------------------------------------------------------------ #
# Cap at 5                                                            #
# ------------------------------------------------------------------ #

def test_recent_list_capped_at_five(tmp_path):
    sm = SettingsManager(tmp_path / "s.json")
    for i in range(8):
        sm.add_recent_source(f"/path{i}")
    assert len(sm.recent_sources) == 5


def test_cap_keeps_most_recent(tmp_path):
    sm = SettingsManager(tmp_path / "s.json")
    for i in range(7):
        sm.add_recent_source(f"/path{i}")
    # Most recently added is /path6
    assert sm.recent_sources[0] == "/path6"
    # /path0 and /path1 should have been evicted
    assert "/path0" not in sm.recent_sources
    assert "/path1" not in sm.recent_sources


# ------------------------------------------------------------------ #
# Persistence                                                         #
# ------------------------------------------------------------------ #

def test_settings_survive_reload(tmp_path):
    path = tmp_path / "s.json"
    sm = SettingsManager(path)
    sm.add_recent_source("/src1")
    sm.add_recent_destination("/dst1")
    sm.add_recent_raf_folder("/raf1")

    sm2 = SettingsManager(path)
    assert sm2.recent_sources == ["/src1"]
    assert sm2.recent_destinations == ["/dst1"]
    assert sm2.recent_raf_folders == ["/raf1"]


def test_settings_written_to_disk_immediately(tmp_path):
    path = tmp_path / "s.json"
    sm = SettingsManager(path)
    sm.add_recent_source("/immediate")
    assert path.exists()
    data = json.loads(path.read_text())
    assert "/immediate" in data["transfer"]["recent_sources"]


# ------------------------------------------------------------------ #
# Robustness                                                          #
# ------------------------------------------------------------------ #

def test_corrupt_file_falls_back_to_empty(tmp_path):
    path = tmp_path / "s.json"
    path.write_text("not valid json {{{")
    sm = SettingsManager(path)
    assert sm.recent_sources == []


def test_partial_file_fills_missing_keys_with_defaults(tmp_path):
    path = tmp_path / "s.json"
    path.write_text(json.dumps({"transfer": {"recent_sources": ["/existing"]}}))
    sm = SettingsManager(path)
    assert sm.recent_sources == ["/existing"]
    assert sm.recent_destinations == []   # missing key → default


# ------------------------------------------------------------------ #
# Independence of lists                                               #
# ------------------------------------------------------------------ #

def test_three_lists_are_independent(tmp_path):
    sm = SettingsManager(tmp_path / "s.json")
    sm.add_recent_source("/src")
    sm.add_recent_destination("/dst")
    sm.add_recent_raf_folder("/raf")

    assert sm.recent_sources == ["/src"]
    assert sm.recent_destinations == ["/dst"]
    assert sm.recent_raf_folders == ["/raf"]
