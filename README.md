# HealthAI Coach — Backend

Backend data platform pour HealthAI Coach : ingestion et qualité des données nutrition / exercices / biométrie, API REST, dashboard de pilotage et interface d'administration.

## Contexte

Ce dépôt héberge la plateforme data du projet HealthAI Coach : pipelines ETL (extraction, transformation, chargement), orchestration Airflow, base PostgreSQL, API FastAPI et outils de suivi de la qualité des données (dashboard Metabase, interface d'administration Gradio).

Le détail des sprints et règles d'engagement est documenté dans [docs/directives_claude_code.md](docs/directives_claude_code.md).

## Stack technique

| Composant | Technologie |
|---|---|
| Base de données | PostgreSQL |
| Migrations | Alembic |
| Orchestration | Apache Airflow |
| API | FastAPI (SQLAlchemy, Pydantic, JWT) |
| Dashboard | Metabase |
| Interface admin | Gradio |
| Conteneurisation | Docker / Docker Compose |
| CI | GitHub Actions |

## Arborescence

```
healthai_coach_backend/
├── docker-compose.yml
├── .env.example
├── docs/
├── airflow/{dags,plugins,config}/
├── etl/{extract,transform,load,logs}/
├── database/{migrations,schema,seed}/
├── api/{routers,models,schemas,security,openapi}/
├── dashboard/{metabase_config,kpi_queries}/
├── admin_interface/{components,export}/
└── tests/{etl,api,data_quality}/
```

## Quickstart

```bash
# 1. Cloner le dépôt
git clone https://github.com/SIMPLON-DIST-DATA-P2-192997/healthai_coach_backend.git
cd healthai_coach_backend

# 2. Copier et compléter les variables d'environnement
cp .env.example .env

# 3. Lancer l'environnement (disponible à partir du Sprint 6)
docker compose up
```

## Workflow de contribution

- Branche par défaut : `main` (protégée, PR obligatoire, 1 review minimum)
- Branche d'intégration : `dev`
- Une branche par module : `feature/<module>`
- Chaque étape = une Pull Request distincte, avec tests unitaires a minima
- Voir [docs/directives_claude_code.md](docs/directives_claude_code.md) pour les règles complètes et le plan de sprints
