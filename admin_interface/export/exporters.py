"""Export des résultats de consultation qualité en CSV/JSON."""

import csv
import json
import tempfile
from pathlib import Path

COLUMNS = [
    "dq_log_id", "source_table", "source_record_id", "dag_id", "rule_name",
    "severity", "message", "detected_at", "resolved", "resolved_at", "resolved_by",
]


def _serialize(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def to_csv_file(rows):
    """Écrit les lignes dans un fichier CSV temporaire et retourne son chemin."""
    path = Path(tempfile.mkstemp(suffix=".csv", prefix="data_quality_log_")[1])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _serialize(row.get(k)) for k in COLUMNS})
    return str(path)


def to_json_file(rows):
    """Écrit les lignes dans un fichier JSON temporaire et retourne son chemin."""
    path = Path(tempfile.mkstemp(suffix=".json", prefix="data_quality_log_")[1])
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            [{k: _serialize(row.get(k)) for k in COLUMNS} for row in rows],
            f,
            indent=2,
            ensure_ascii=False,
        )
    return str(path)
