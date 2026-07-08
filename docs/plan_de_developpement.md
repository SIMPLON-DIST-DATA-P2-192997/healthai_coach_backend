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

### Convention : `users` créés à partir des datasets

Les datasets Kaggle (diet_recommendations, gym_members...) ne contiennent aucun mot de passe : ce ne sont pas de vrais comptes, seulement des profils de référence pour peupler l'historique nutrition/exercice/biométrie. Ces `users` ne sont **jamais destinés à s'authentifier**. Convention à respecter dans `etl/load/postgres_loader.py`, cohérente avec `database/seed/seed_data.py` :

- `email` : généré à partir de l'identifiant source (ex. `Patient_ID`), avec un suffixe placeholder explicite (`@seed.local` ou équivalent — à garder identique à celui du seed).
- `hashed_password` : chaîne fixe non-fonctionnelle (`"seed-not-a-real-hash"`), jamais un vrai hash bcrypt — il n'y a pas de mot de passe en clair à hasher.
- Si un besoin de « réclamer » un profil existant apparaît un jour (un vrai utilisateur associant son compte à un profil importé), ce sera un flux applicatif dédié côté API, pas une responsabilité de l'ETL.

À l'inverse, les nouveaux utilisateurs créés via le frontend passent toujours par `POST /api/v1/auth/register` (`password` en clair dans la requête, hashé côté API par `hash_password()` — cf. `api/security/security.py`). Personne ne doit jamais écrire directement dans `hashed_password` à la main.

**`first_name`/`last_name`** : les datasets `diet-recommendations` et `gym-members` n'ont jamais eu de champ nom (uniquement `Patient_ID`/âge/genre — anonymisé par construction dans la source, pas une donnée manquante à corriger). Ces deux colonnes sont `NOT NULL` dans le schéma, donc il faut bien produire une valeur. Décision : utiliser la librairie `Faker` (Python) pour générer un nom plausible, **avec une seed déterministe par ligne source** (ex. `Faker.seed(hash(patient_id))` ou équivalent), pas un tirage aléatoire à chaque exécution — sinon un même utilisateur changerait de prénom/nom à chaque ré-exécution de l'ETL, ce qui casse la logique d'idempotence attendue par ailleurs (cf. section suivante). Sans enjeu de véracité ici contrairement à `food_items.name` (qui, lui, existe bien dans la source et ne doit jamais être fabriqué) : ces `users` sont déjà des profils de référence non-authentifiants, un nom Faker stable ne fait qu'améliorer le réalisme d'affichage sans rien casser en aval.

### Convention : idempotence et déduplication au chargement

Les datasets Kaggle n'ont pas de clé primaire stable, et les DAG Airflow prévus au Sprint 3 impliquent des ré-exécutions (une architecture d'orchestration planifiée n'a pas de sens pour un chargement en un coup unique). Il faut donc traiter chaque ingestion comme potentiellement rejouable, pas comme un one-shot. Quatre règles :

**A. Figer l'extraction brute (landing zone immuable)**
Ne pas retélécharger le dataset Kaggle à chaque run du DAG. Télécharger une fois, archiver le fichier brut tel quel (ex. `etl/data/raw/<source>_<date_extraction>.csv`), et faire tourner `transform`/`load` sur cette copie figée à chaque ré-exécution — pas sur un nouveau téléchargement. Ça rend un `external_id` basé sur l'index de ligne stable indéfiniment, sans logique de hash. Si le dataset Kaggle change un jour, c'est une nouvelle vague d'ingestion consciente, pas un run automatique qui casse tout silencieusement.

**B. Upsert SQL dans `etl/load/postgres_loader.py`**
Remplacer tout `INSERT` brut par `INSERT ... ON CONFLICT ... DO UPDATE`, en s'appuyant sur les `UNIQUE` déjà présents dans le schéma (`food_items` et `exercises` ont `UNIQUE(source, external_id)`, conçu explicitement pour ça — cf. les commentaires de colonne dans `ddl_postgres.sql`) :

```python
cur.execute(
    """
    INSERT INTO food_items
        (external_id, source, name, calories_kcal, protein_g, carbs_g, ...)
    VALUES (%s, %s, %s, %s, %s, %s, ...)
    ON CONFLICT (source, external_id) DO UPDATE SET
        name           = EXCLUDED.name,
        calories_kcal  = EXCLUDED.calories_kcal,
        protein_g      = EXCLUDED.protein_g,
        carbs_g        = EXCLUDED.carbs_g
    """,
    (external_id, source, name, calories_kcal, protein_g, carbs_g, ...),
)
```

Même pattern pour `exercises`. Pour de gros volumes, `psycopg2.extras.execute_values` supporte aussi une clause `ON CONFLICT` dans son template — à privilégier plutôt qu'une boucle `execute()` ligne par ligne.

**C. Filtrer *avant* d'insérer, pas laisser la DB être le seul filet**
Dans `quality_rules.py` : valider chaque ligne transformée avant le insert (champs requis présents, valeurs dans une plage plausible). Ligne invalide → ne pas l'insérer, logguer dans `data_quality_log` (`source_table`, `source_record_id=external_id`, `rule_name`, `severity`, `message`), et continuer avec les lignes suivantes. Les contraintes `NOT NULL`/`CHECK` de la DB restent un filet de sécurité en dernier recours, pas le mécanisme principal — sinon une seule ligne pourrie fait échouer tout le batch d'un coup.

**D. Point de vigilance spécifique à `biometric_measurements`**
Sa contrainte est `UNIQUE(user_id, measured_at)`, pas `UNIQUE(user_id, source)`. Si le chargement fixe `measured_at = now()` au moment de l'ingestion (comme le fait `database/seed/seed_data.py`, qui reste un seed dev/test, pas une référence à copier pour le vrai `load`), chaque ré-exécution génère un nouveau `measured_at` et la contrainte ne détecte **aucun** doublon : on empile des relevés identiques à l'infini à chaque run. Décision à prendre avec Rôle A avant d'écrire `load` pour ce module : soit chaque ré-ingestion est un « nouveau relevé » légitime (peu probable, ce ne sont pas de vraies séries temporelles), soit il faut une vraie clé d'idempotence (dater `measured_at` à partir d'un champ du dataset source si disponible, ou n'insérer qu'un seul relevé par `(user_id, source)`).

**Point d'attention transverse** : `database/seed/seed_data.py` reste une référence valable pour le *mapping colonnes → tables*, mais son `TRUNCATE ... CASCADE` en tout début de script est strictement réservé au seed dev/test (cf. son propre docstring). Le vrai `load` ne doit jamais faire de `TRUNCATE` : il doit toujours upserter contre les données existantes, y compris les vraies données utilisateur produites par l'usage réel de l'application.

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
