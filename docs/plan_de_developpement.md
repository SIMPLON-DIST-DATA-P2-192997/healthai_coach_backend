# HealthAI Coach — Plan de développement
**Rédigé par :** Rôle A — Architecte / Lead Data Engineer
**Destinataires :** Équipe de développement
**Statut :** Architecture validée par Alexandre — GO développement

---

## Règles d'engagement (à respecter sur tout le sprint)

1. **Diff/patch uniquement** — jamais de réécriture globale d'un fichier existant.
2. **Une étape = une PR** — chaque module fermé par une Pull Request distincte.
3. **Tests obligatoires** avant de passer à l'étape suivante (unitaires a minima).
4. **Pas de merge sur `main`** sans validation explicite du Rôle A.
5. **Respect strict de l'arborescence** définie dans l'architecture (voir section 3 ci-dessous).
6. Si ambiguïté sur le besoin métier → ouvrir une question dans la PR, ne pas improviser.

---

## SPRINT 0 — URGENT : Bootstrap repo GitHub (org Simplon)

### Objectif
Créer le dépôt sous l'organisation GitHub **Simplon**, prêt à recevoir le code.

### Actions attendues

| # | Action | Détail |
|---|---|---|
| 1 | Créer repo | Nom : `healthai-coach-backend` (à confirmer), visibilité **privée**, org **Simplon** |
| 2 | Branche par défaut | `main` protégée : PR obligatoire, 1 review minimum (Rôle A), pas de push direct |
| 3 | Branches de travail | `develop` (intégration), `feature/<module>` par module (ex. `feature/etl-nutrition`) |
| 4 | Structure de dossiers | Créer l'arborescence complète (squelette vide + `.gitkeep`) selon l'architecture validée — voir ci-dessous |
| 5 | Fichiers racine | `README.md` (contexte projet + stack + quickstart), `.gitignore` (Python, Docker, Airflow, .env), `LICENSE` (à confirmer avec Alexandre, MIT par défaut), `.env.example` |
| 6 | Gouvernance | `CODEOWNERS` (Rôle A = owner sur `/database`, `/airflow/dags`, `/docs`), template de PR (`.github/pull_request_template.md`), template d'issue |
| 7 | CI minimale | GitHub Actions : job `lint + tests` déclenché sur chaque PR (squelette, pas de logique encore) |

### Arborescence à instancier (squelette vide)

```
healthai-coach-backend/
├── docker-compose.yml
├── .env.example
├── README.md
├── docs/
├── airflow/{dags,plugins,config}/
├── etl/{extract,transform,load,logs}/
├── database/{migrations,schema,seed}/
├── api/{routers,models,schemas,security,openapi}/
├── dashboard/{metabase_config,kpi_queries}/
├── admin_interface/{components,export}/
└── tests/{etl,api,data_quality}/
```

### Livrable Sprint 0
PR unique `chore/bootstrap-repo` → review Rôle A → merge sur `main`.

---

## SPRINT 1 — Base de données (bloquant pour tout le reste)

1. Traduire le MCD (fourni par Rôle A) en MLD/DDL PostgreSQL dans `database/schema/ddl_postgres.sql`.
2. Mettre en place Alembic dans `database/migrations/`.
3. Script de seed minimal (`database/seed/`) pour peupler des données de test.
4. Tests : vérifier la création des tables + contraintes FK (`tests/data_quality/test_schema.py`).

**Point de blocage** : ne pas démarrer l'API tant que ce sprint n'est pas validé (schéma = contrat).

---

## SPRINT 2 — ETL (extract → transform → load), un module à la fois

Ordre strict : **nutrition → exercises → biometrics**

Pour chaque module :
1. `etl/extract/<module>_loader.py` (ou `_client.py` pour ExerciseDB)
2. `etl/transform/clean_<module>.py` + règles qualité communes dans `quality_rules.py`
3. `etl/load/postgres_loader.py` (générique, réutilisé par les 3 modules)
4. Tests unitaires `tests/etl/test_<module>.py` (jeu de données factice, pas les vraies sources)
5. PR distincte par module

**Note ExerciseDB** : forker `https://github.com/ExerciseDB/exercisedb-api` sous l'org Simplon avant de coder le client.

---

## SPRINT 3 — Orchestration Airflow

- 1 DAG par source (`dag_ingestion_nutrition.py`, etc.) + 1 DAG `dag_quality_check.py`
- Dépendance stricte : DAG ne s'active qu'une fois le module ETL correspondant testé et mergé
- Log des anomalies → table `DATA_QUALITY_LOG`

---

## SPRINT 4 — API REST (FastAPI)

Ordre : `models/` (SQLAlchemy) → `schemas/` (Pydantic) → `routers/` → `security/` (JWT)

- Tests après chaque router (`tests/api/`)
- OpenAPI généré automatiquement, exposé sur `/docs`
- Ne pas exposer d'endpoint sans schéma Pydantic validé

---

## SPRINT 5 — Interface admin (Gradio) + Dashboard (Metabase)

- `admin_interface/app_gradio.py` : consultation qualité, correction manuelle, export JSON/CSV
- `dashboard/kpi_queries/` : vues SQL pour Metabase (pas de logique dans Metabase lui-même)
- Vérifier accessibilité RGAA AA sur l'interface Gradio (contraste, labels, navigation clavier)

---

## SPRINT 6 — Dockerisation complète

- `docker-compose.yml` : postgres, airflow (webserver+scheduler), api, metabase, admin
- Objectif : `docker compose up` → environnement fonctionnel en **< 30 min**
- Documenter dans `docs/guide_deploiement.md`

---

## Checkpoints de validation (Rôle A)

Chaque sprint se termine par une revue de PR avec :
- ✅ Tests passants
- ✅ Respect de l'arborescence
- ✅ Documentation à jour (`docs/`)
- ✅ Pas de régression sur les sprints précédents

Aucun sprint ne démarre sans validation explicite du sprint précédent.
