# Guide de déploiement

Sprint 6. Ce document centralise toutes les procédures — automatiques et manuelles — pour faire tourner l'environnement HealthAI Coach en local (dev, démo).

## Démarrage rapide (1 commande)

```bash
cp .env.example .env
docker compose up -d --build
```

C'est tout. `docker compose up` orchestre dans l'ordre :

1. **`postgres`** démarre, attend d'être `healthy` (`pg_isready`). Le tout premier démarrage (volume vierge) exécute aussi les scripts de `database/init/` : création des bases `metabase` et `airflow`, séparées de `healthai_coach` (cf. `database/init/01_create_metabase_db.sql`, `02_create_airflow_db.sql`).
2. **`db-init`** (une fois `postgres` prêt) applique dans l'ordre : migrations Alembic (`alembic upgrade head`), seed de données de test (`database/seed/seed_data.py`), vues KPI Metabase (`dashboard/kpi_queries/*.sql`) — puis s'arrête (conteneur à usage unique, `exit 0` attendu).
3. **`admin_interface`**, **`metabase`** et **`airflow-init`** ne démarrent qu'une fois `db-init` terminé avec succès (`condition: service_completed_successfully`) — la base est déjà peuplée quand ils apparaissent, jamais de démarrage sur un schéma vide.
4. **`airflow-webserver`** et **`airflow-scheduler`** démarrent une fois `airflow-init` terminé (migration de la base de métadonnées Airflow + création du compte admin).

**Remarque volume existant** : `database/init/*.sql` ne s'exécute qu'au tout premier démarrage d'un volume `postgres_data` vierge (comportement standard de l'image `postgres`). Si tu as déjà une stack qui tournait avant l'ajout d'Airflow, la base `airflow` n'existe pas encore sur ton volume — créer une fois manuellement :
```bash
docker exec healthai_coach_backend-postgres-1 psql -U healthai -d healthai_coach -c "CREATE DATABASE airflow"
```

Vérifier que tout est monté :
```bash
docker compose ps
```
`db-init` doit apparaître `Exited (0)`, les autres `Up`/`healthy`.

## Point de vigilance : `db-init` ne deviendra pas le vrai pipeline ETL

`db-init` lance `database/seed/seed_data.py` — des données fictives/échantillon (50 lignes par source), avec un `TRUNCATE ... CASCADE` avant repeuplement. C'est fait pour le dev local et la démo, pas pour la production.

Le vrai pipeline (`etl/load/postgres_loader.py`, Sprint 2) est conçu différemment : upsert idempotent (`ON CONFLICT DO UPDATE`, cf. convention documentée dans `docs/plan_de_developpement.md`), volumes réels, **jamais** de `TRUNCATE` — et tourne désormais via le DAG Airflow `healthai_etl_pipeline` (Sprint 3, cf. section Airflow ci-dessous), pas comme conteneur à usage unique déclenché par `docker compose up`.

**Confirmé empiriquement, pas juste théorique** : en testant le DAG Airflow (extraction Kaggle/ExerciseDB réelle → 2851 users, 645 food_items, 404 exercises chargés), un simple `docker compose up admin_interface` ultérieur a redéclenché `db-init` (dépendance `service_completed_successfully`) qui a **immédiatement tout effacé** pour revenir aux 101/50/4 lignes de démo. Le risque documenté plus bas n'est donc plus une hypothèse — il se produit dès qu'Airflow et `db-init` coexistent tels quels.

**Ne jamais laisser `seed_data.py` dans `db-init` une fois que l'ETL réel alimente la base avec de vraies données** — le `TRUNCATE` effacerait tout à chaque `docker compose up`. Décision à prendre avec le Rôle A avant la mise en production (toujours pas tranchée à date de rédaction) :
- soit retirer `seed_data.py` de `db-init` et ne garder que les migrations (schéma), en laissant Airflow peupler les données indépendamment ;
- soit conditionner son exécution à une variable d'environnement dédiée (ex. `SEED_DEMO_DATA=true`), réservée aux environnements de démo/dev qui ne font pas tourner Airflow à côté.

En attendant : si tu viens de faire tourner le DAG Airflow et que tu veux garder ces données pour une démo, ne relance pas `docker compose up` (ou toute commande qui redémarre `admin_interface`/`metabase`/`airflow-init`, tous dépendants de `db-init`) sans avoir conscience que ça réinitialise tout.

## Accès aux services

| Service | URL | Identifiants |
|---|---|---|
| Interface admin (Gradio) | http://localhost:7860 | — |
| Metabase | http://localhost:3000 | à créer au premier lancement (voir ci-dessous) |
| Airflow | http://localhost:8080 | `airflow` / `airflow` (`_AIRFLOW_WWW_USER_*` dans `.env`, à changer hors démo locale) |
| PostgreSQL | `localhost:5432` | `healthai` / `changeme` (base `healthai_coach`) |

## Connecter Metabase (étape manuelle, hors automatisation)

Metabase n'expose pas d'API pour pré-configurer une connexion base de données au démarrage — cette étape reste manuelle, une seule fois :

1. Ouvrir http://localhost:3000 — assistant de première configuration.
2. Créer un compte admin Metabase (email/mot de passe, propre à Metabase — aucun rapport avec `users` de l'application).
3. À l'étape *"Add your data"* : choisir **PostgreSQL**, puis :
   - Host : `postgres` (nom du service docker-compose, pas `localhost` — Metabase tourne dans son propre conteneur)
   - Port : `5432`
   - Database name : `healthai_coach`
   - Username / Password : `healthai` / `changeme`
4. Une fois connecté, *Browse data* → base `healthai_coach` : les tables et les vues KPI (`vw_nutrition_meal_type_breakdown`, `vw_biometric_trend`, `vw_workout_sessions_summary`, etc.) apparaissent au même niveau.

Si les vues n'apparaissent pas immédiatement : *Admin* → *Databases* → `healthai_coach` → *Sync database schema now*.

## Airflow — pipeline ETL orchestré

Un seul DAG, `healthai_etl_pipeline` (`airflow/dags/healthai_etl_pipeline.py`) : `extract` → `transform_and_load` → `quality_check`, quotidien (`@daily`), `catchup=False`. Choix documentés dans le rapport (section Pipeline ETL) : un DAG unique plutôt qu'un DAG par source, `LocalExecutor` + base PostgreSQL partagée plutôt que le stack `CeleryExecutor`/Redis complet du TP de formation (empreinte mémoire trop lourde pour la machine de démo).

**Environnement Python isolé** : les dépendances ETL (pandas, SQLAlchemy 2.0) sont installées dans un venv dédié (`/opt/etl-venv`, cf. `airflow/Dockerfile`), pas dans l'environnement Python d'Airflow lui-même — Airflow 2.10.5 exige `SQLAlchemy<2.0` en interne, un conflit direct avec le reste du projet (SQLAlchemy 2.0.51 partout ailleurs). Chaque tâche du DAG est un `BashOperator` qui invoque ce venv en sous-processus, jamais un `PythonOperator` qui importerait `etl/` dans le process Airflow.

Déclencher le DAG manuellement (interface web désactivée par défaut, `AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true`) :
```bash
# Depuis l'UI (http://localhost:8080) : bouton Play sur healthai_etl_pipeline, ou
docker compose exec airflow-scheduler airflow dags trigger healthai_etl_pipeline

# Ou en une commande jetable, sans dépendre du scheduler (pratique pour un test rapide) :
docker compose run --rm airflow-scheduler airflow dags test healthai_etl_pipeline $(date +%F)
```

Logs d'une tâche : UI Airflow → DAG → tâche → *Logs*, ou `docker compose logs airflow-scheduler`.

## Procédures manuelles (cas particuliers)

`db-init` couvre le cas nominal (premier démarrage). Pour rejouer une étape individuellement sans tout relancer :

```bash
# Depuis l'hôte, avec le .venv du projet activé (pip install -r database/migrations/requirements.txt -r database/seed/requirements.txt)
DATABASE_URL=postgresql://healthai:changeme@localhost:5432/healthai_coach alembic upgrade head
DATABASE_URL=postgresql://healthai:changeme@localhost:5432/healthai_coach python database/seed/seed_data.py

# Vues KPI seules (psql disponible dans le conteneur postgres, pas besoin de l'installer sur l'hôte)
docker exec -i healthai_coach_backend-postgres-1 psql -U healthai -d healthai_coach < dashboard/kpi_queries/nutrition_biometrics.sql
docker exec -i healthai_coach_backend-postgres-1 psql -U healthai -d healthai_coach < dashboard/kpi_queries/fitness.sql
```

**Attention** : `seed_data.py` fait un `TRUNCATE ... CASCADE` avant de repeupler — jamais à exécuter sur un environnement contenant de vraies données utilisateur (cf. `database/seed/seed_data.py`, docstring).

Après un reseed manuel, si Metabase doit refléter les nouvelles données : pas d'action nécessaire pour les tables/vues déjà synchronisées, Metabase interroge la base en direct à chaque question/dashboard.

## Lancer l'API en local (hors docker-compose, en attendant le Dockerfile de Florian)

```bash
source .venv/bin/activate
pip install -r api/requirements.txt
DATABASE_URL=postgresql://healthai:changeme@localhost:5432/healthai_coach JWT_SECRET_KEY=dev-secret uvicorn api.main:app --reload --port 8000
```

`http://localhost:8000/` redirige automatiquement vers `/docs` (Swagger UI) ; `/redoc` pour ReDoc.

## Déroulé de démo bout-en-bout (oral)

Checklist pour une démo live sans mauvaise surprise. **Lire l'avertissement à l'étape 5 avant de commencer** — l'ordre compte.

1. **Démarrage propre**
   ```bash
   docker compose up -d --build
   docker compose ps   # tout Up/healthy sauf db-init, airflow-init (Exited (0), normal)
   ```
2. **Interface admin** (http://localhost:7860) — montrer le tableau des anomalies de qualité (données de démo `seed_data.py`), filtrer par sévérité, résoudre une anomalie, exporter en CSV/JSON.
3. **Metabase** (http://localhost:3000) — se connecter si pas déjà fait (section dédiée ci-dessus), montrer le schéma `healthai_coach` et une ou deux vues KPI (`vw_nutrition_meal_type_breakdown`, `vw_biometric_trend`...).
4. **API** (hors docker-compose en attendant le Dockerfile de Florian) :
   ```bash
   source .venv/bin/activate
   DATABASE_URL=postgresql://healthai:changeme@localhost:5432/healthai_coach JWT_SECRET_KEY=dev-secret uvicorn api.main:app --reload --port 8000
   ```
   Ouvrir http://localhost:8000/docs — Swagger UI, montrer l'authentification (`POST /auth/login`), un endpoint self-service (`GET /users/me`), et si pertinent le gating premium sur `/ai/*` (403 en `free`, 201 après `POST /subscriptions`).
5. **Airflow** (http://localhost:8080, `airflow`/`airflow`) — montrer le DAG `healthai_etl_pipeline`, le déclencher (bouton Play), suivre l'exécution des 3 tâches en direct (Graph view), puis retourner sur l'interface admin/Metabase pour montrer les **vraies données ETL** venant de remplacer les données de démo (ex. `SELECT COUNT(*) FROM users` passe de 101 à plusieurs milliers).

   **⚠️ Piège à éviter pendant la démo** : une fois le DAG déclenché avec succès, **ne plus relancer `docker compose up` ni redémarrer `admin_interface`/`metabase`** — cela redéclenche `db-init`, qui `TRUNCATE` tout et revient aux données de démo (confirmé empiriquement, cf. section "Point de vigilance" plus haut, et le rapport section Bilan). Si la démo doit repartir de zéro, c'est le seul moment où le relancer sans risque.

## Arrêt / nettoyage

```bash
docker compose down          # arrête et supprime les conteneurs, garde le volume postgres_data
docker compose down -v       # + supprime le volume (repart de zéro au prochain up)
```

## Dépannage

- **`admin_interface` crash au démarrage avec `UndefinedTable`** : ne devrait plus arriver depuis l'ajout de `db-init` (dépendance `service_completed_successfully`) — si ça se produit quand même, vérifier que `db-init` s'est bien terminé en `Exited (0)` (`docker compose logs db-init`) avant de relancer `admin_interface`.
- **Port déjà utilisé** (`5432`, `7860`, `3000`) : un autre conteneur ou service local occupe le port. `docker ps` pour identifier, ou changer le port hôte dans `.env` (`POSTGRES_PORT`, `ADMIN_INTERFACE_PORT`, `METABASE_PORT`).
- **Machine qui sature en mémoire avec plusieurs stacks docker-compose actives en parallèle** (ex. cette stack + une stack Airflow séparée) : arrêter les stacks non utilisées (`docker compose -p <projet> down`) plutôt que de les laisser tourner en continu — `docker ps` liste tous les conteneurs actifs tous projets confondus pour identifier ce qui peut être coupé. En dernier recours avant de lancer Airflow : `docker compose stop admin_interface metabase` le temps du test, ils se relancent en quelques secondes ensuite.
- **Tâche `extract` du DAG Airflow en échec avec `PermissionError: [Errno 13] Permission denied: './etl/data'`** : le conteneur Airflow tourne avec l'UID non-root `AIRFLOW_UID` (50000 par défaut), qui n'a pas le droit d'écrire dans `etl/data/` monté depuis l'hôte si ce dossier n'existe pas encore ou appartient à un autre utilisateur. Fix : `mkdir -p etl/data && chmod 777 etl/data` sur l'hôte avant de relancer le DAG.
