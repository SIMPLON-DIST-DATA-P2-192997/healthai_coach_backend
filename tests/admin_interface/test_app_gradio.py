"""Tests admin_interface/app_gradio.py — fonctions pures et logique de glue.

La couche DB (admin_interface.db) est mockée via monkeypatch : pas besoin de
Postgres pour ces tests, contrairement à tests/admin_interface/test_db.py.
Note : importer ce module ne lance rien (build_app()/launch() sont sous
`if __name__ == "__main__":`), donc aucun accès DB n'est déclenché à l'import.
"""
from datetime import datetime, timezone

import admin_interface.app_gradio as app_gradio
from admin_interface.export.exporters import COLUMNS


def test_format_datetime_none_returns_none():
    assert app_gradio._format_datetime(None) is None


def test_format_datetime_formats_datetime_short():
    value = datetime(2026, 7, 8, 14, 5, 30, tzinfo=timezone.utc)
    assert app_gradio._format_datetime(value) == "2026-07-08 14:05"


def test_format_datetime_passthrough_for_non_datetime():
    assert app_gradio._format_datetime("already a string") == "already a string"


def test_rows_to_table_formats_only_date_columns():
    row = {c: f"val-{c}" for c in COLUMNS}
    row["detected_at"] = datetime(2026, 7, 8, 9, 0, tzinfo=timezone.utc)
    row["resolved_at"] = None
    table = app_gradio._rows_to_table([row])
    line = dict(zip(COLUMNS, table[0]))
    assert line["detected_at"] == "2026-07-08 09:00"
    assert line["resolved_at"] is None
    assert line["source_table"] == "val-source_table"


def test_rows_to_table_preserves_column_order():
    row = {c: c for c in COLUMNS}
    table = app_gradio._rows_to_table([row])
    assert table[0][COLUMNS.index("rule_name")] == "rule_name"
    assert table[0][COLUMNS.index("severity")] == "severity"


FAKE_ROWS = [
    {"dq_log_id": 1, "source_table": "food_items", "severity": "warning", "resolved": False},
]


def test_refresh_translates_toutes_and_non_resolues(monkeypatch):
    captured = {}

    def fake_list(severity=None, resolved=None, source_table=None):
        captured["severity"] = severity
        captured["resolved"] = resolved
        captured["source_table"] = source_table
        return FAKE_ROWS

    monkeypatch.setattr(app_gradio, "list_data_quality_log", fake_list)

    table, rows = app_gradio.refresh("Toutes", "Non résolues", "food")

    assert captured["severity"] is None
    assert captured["resolved"] is False
    assert captured["source_table"] == "food"
    assert rows == FAKE_ROWS


def test_refresh_translates_specific_severity_and_resolues(monkeypatch):
    captured = {}

    def fake_list(severity=None, resolved=None, source_table=None):
        captured["severity"] = severity
        captured["resolved"] = resolved
        return []

    monkeypatch.setattr(app_gradio, "list_data_quality_log", fake_list)

    app_gradio.refresh("error", "Résolues", "")

    assert captured["severity"] == "error"
    assert captured["resolved"] is True


def test_do_resolve_without_id_returns_prompt_message(monkeypatch):
    monkeypatch.setattr(app_gradio, "list_data_quality_log", lambda **kwargs: FAKE_ROWS)

    message, table, rows = app_gradio.do_resolve(None, None, "Toutes", "Non résolues", "")

    assert "identifiant" in message.lower()
    assert rows == FAKE_ROWS


def test_do_resolve_success_message(monkeypatch):
    monkeypatch.setattr(app_gradio, "resolve_entry", lambda dq_log_id, resolved_by=None: True)
    monkeypatch.setattr(app_gradio, "list_data_quality_log", lambda **kwargs: FAKE_ROWS)

    message, table, rows = app_gradio.do_resolve(42, None, "Toutes", "Non résolues", "")

    assert message == "Anomalie #42 marquée comme résolue."


def test_do_resolve_not_found_message(monkeypatch):
    monkeypatch.setattr(app_gradio, "resolve_entry", lambda dq_log_id, resolved_by=None: False)
    monkeypatch.setattr(app_gradio, "list_data_quality_log", lambda **kwargs: [])

    message, table, rows = app_gradio.do_resolve(999, None, "Toutes", "Non résolues", "")

    assert message == "Aucune anomalie trouvée avec l'identifiant 999."


def test_do_resolve_passes_admin_user_id_as_int(monkeypatch):
    captured = {}

    def fake_resolve(dq_log_id, resolved_by=None):
        captured["dq_log_id"] = dq_log_id
        captured["resolved_by"] = resolved_by
        return True

    monkeypatch.setattr(app_gradio, "resolve_entry", fake_resolve)
    monkeypatch.setattr(app_gradio, "list_data_quality_log", lambda **kwargs: [])

    app_gradio.do_resolve(7, "3", "Toutes", "Non résolues", "")

    assert captured["dq_log_id"] == 7
    assert captured["resolved_by"] == 3
