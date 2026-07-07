"""Interface admin — consultation qualité, correction manuelle, export.

Sprint 5. Nécessite un accès à la base PostgreSQL (DATABASE_URL) déjà
peuplée (cf. database/seed/ ou l'ETL réel).

Accessibilité RGAA AA : chaque champ porte un label explicite, aucune
information n'est portée par la seule couleur (la sévérité est affichée en
texte dans le tableau), navigation clavier native de Gradio (pas de JS/souris
obligatoire, thème intégré `Soft` — pas de CSS personnalisé qui risquerait de
casser le contraste déjà validé par Gradio pour ses propres thèmes).

Usage :
    pip install -r admin_interface/requirements.txt
    DATABASE_URL=postgresql://user:pass@host:5432/db python -m admin_interface.app_gradio
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr

from admin_interface.db import SEVERITIES, list_admin_users, list_data_quality_log, resolve_entry
from admin_interface.export.exporters import COLUMNS, to_csv_file, to_json_file

RESOLVED_LABELS = {"Toutes": None, "Résolues": True, "Non résolues": False}

# Largeurs explicites alignées sur COLUMNS : sans ça, les colonnes vides/
# étroites (source_record_id, dag_id) se compressent et leur en-tête
# s'affiche empilé caractère par caractère (illisible, cf. capture de test).
COLUMN_WIDTHS = [
    "90px",   # dq_log_id
    "170px",  # source_table
    "180px",  # source_record_id
    "160px",  # dag_id
    "210px",  # rule_name
    "100px",  # severity
    "320px",  # message
    "150px",  # detected_at (date formatée, cf. _format_datetime)
    "90px",   # resolved
    "150px",  # resolved_at (date formatée)
    "110px",  # resolved_by
]


def _format_datetime(value):
    """Format court et lisible pour l'affichage (l'export CSV/JSON garde la
    précision complète via exporters._serialize, indépendant de cette fonction)."""
    if value is None:
        return None
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M")
    return value


def _rows_to_table(rows):
    return [
        [
            _format_datetime(row.get(c)) if c in ("detected_at", "resolved_at") else row.get(c)
            for c in COLUMNS
        ]
        for row in rows
    ]


def refresh(severity, resolved_filter, source_table):
    rows = list_data_quality_log(
        severity=None if severity == "Toutes" else severity,
        resolved=RESOLVED_LABELS[resolved_filter],
        source_table=source_table or None,
    )
    return _rows_to_table(rows), rows


def do_resolve(dq_log_id, admin_user_id, severity, resolved_filter, source_table):
    if not dq_log_id:
        rows = list_data_quality_log(
            severity=None if severity == "Toutes" else severity,
            resolved=RESOLVED_LABELS[resolved_filter],
            source_table=source_table or None,
        )
        return "Merci de saisir l'identifiant d'une anomalie (dq_log_id).", _rows_to_table(rows), rows

    ok = resolve_entry(int(dq_log_id), resolved_by=int(admin_user_id) if admin_user_id else None)
    message = (
        f"Anomalie #{int(dq_log_id)} marquée comme résolue."
        if ok
        else f"Aucune anomalie trouvée avec l'identifiant {int(dq_log_id)}."
    )
    rows = list_data_quality_log(
        severity=None if severity == "Toutes" else severity,
        resolved=RESOLVED_LABELS[resolved_filter],
        source_table=source_table or None,
    )
    return message, _rows_to_table(rows), rows


def export_csv(current_rows):
    return to_csv_file(current_rows)


def export_json(current_rows):
    return to_json_file(current_rows)


def build_app():
    admins = list_admin_users()
    admin_choices = [("Non renseigné", None)] + [
        (f"{u['email']} (#{u['user_id']})", u["user_id"]) for u in admins
    ]

    with gr.Blocks(title="HealthAI Coach — Qualité des données") as demo:
        gr.Markdown(
            "# 🩺 Qualité des données\n"
            "Consultation, correction manuelle et export des anomalies détectées par l'ETL."
        )

        current_rows = gr.State([])

        with gr.Group():
            gr.Markdown("### Filtres")
            with gr.Row():
                severity_filter = gr.Dropdown(
                    choices=["Toutes"] + SEVERITIES,
                    value="Toutes",
                    label="Sévérité",
                )
                resolved_filter = gr.Dropdown(
                    choices=list(RESOLVED_LABELS.keys()),
                    value="Non résolues",
                    label="Statut de résolution",
                )
                source_table_filter = gr.Textbox(
                    label="Table source (filtre partiel)",
                    placeholder="ex. food_items",
                )
                refresh_btn = gr.Button("🔄 Rafraîchir", variant="secondary")

            table = gr.Dataframe(
                headers=COLUMNS,
                label="Anomalies détectées",
                interactive=False,
                wrap=False,
                column_widths=COLUMN_WIDTHS,
                max_chars=80,
                pinned_columns=1,
                buttons=["fullscreen", "copy"],
            )

        with gr.Group():
            gr.Markdown("### ✏️ Correction manuelle")
            with gr.Row():
                resolve_id = gr.Number(label="Identifiant de l'anomalie (dq_log_id)", precision=0)
                admin_dropdown = gr.Dropdown(
                    choices=admin_choices,
                    value=None,
                    label="Résolu par (administrateur)",
                )
                resolve_btn = gr.Button("Marquer comme résolu", variant="primary")
            resolve_status = gr.Markdown()

        with gr.Group():
            gr.Markdown("### ⬇️ Export")
            with gr.Row():
                export_csv_btn = gr.Button("Exporter en CSV", variant="secondary")
                export_json_btn = gr.Button("Exporter en JSON", variant="secondary")
            export_file = gr.File(label="Fichier exporté", height=100)

        filter_inputs = [severity_filter, resolved_filter, source_table_filter]

        refresh_btn.click(refresh, inputs=filter_inputs, outputs=[table, current_rows])
        resolve_btn.click(
            do_resolve,
            inputs=[resolve_id, admin_dropdown, *filter_inputs],
            outputs=[resolve_status, table, current_rows],
        )
        export_csv_btn.click(export_csv, inputs=[current_rows], outputs=[export_file])
        export_json_btn.click(export_json, inputs=[current_rows], outputs=[export_file])

        demo.load(refresh, inputs=filter_inputs, outputs=[table, current_rows])

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(theme=gr.themes.Soft())
