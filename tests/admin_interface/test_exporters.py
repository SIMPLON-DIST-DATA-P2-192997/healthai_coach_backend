"""Tests admin_interface/export/exporters.py — purs, aucune base nécessaire."""
import csv
import json
from datetime import datetime, timezone

from admin_interface.export.exporters import COLUMNS, to_csv_file, to_json_file

ROW = {
    "dq_log_id": 1,
    "source_table": "food_items",
    "source_record_id": None,
    "dag_id": None,
    "rule_name": "check_range",
    "severity": "warning",
    "message": "valeur négative",
    "detected_at": datetime(2026, 7, 8, 10, 30, tzinfo=timezone.utc),
    "resolved": False,
    "resolved_at": None,
    "resolved_by": None,
}


def test_to_csv_file_writes_header_and_row():
    path = to_csv_file([ROW])
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == COLUMNS
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["source_table"] == "food_items"
    assert rows[0]["detected_at"] == "2026-07-08T10:30:00+00:00"
    assert rows[0]["source_record_id"] == ""


def test_to_csv_file_empty_rows_writes_header_only():
    path = to_csv_file([])
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == COLUMNS
        assert list(reader) == []


def test_to_json_file_serializes_dates_as_isoformat():
    path = to_json_file([ROW])
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["detected_at"] == "2026-07-08T10:30:00+00:00"
    assert data[0]["source_record_id"] is None


def test_to_json_file_empty_rows_writes_empty_array():
    path = to_json_file([])
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data == []


def test_exporters_ignore_extra_keys_not_in_columns():
    row_with_extra = dict(ROW, unexpected_key="should be ignored")
    path = to_json_file([row_with_extra])
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert "unexpected_key" not in data[0]
    assert set(data[0].keys()) == set(COLUMNS)
