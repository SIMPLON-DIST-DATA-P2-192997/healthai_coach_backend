# Guide de déploiement

Sprint 6. Ce document centralise toutes les procédures — automatiques et manuelles — pour faire tourner l'environnement HealthAI Coach en local (dev, démo).

## Démarrage rapide (1 commande)

```bash
cp .env.example .env
docker compose up -d --build
```

C'est tout. `docker compose up` orchestre dans l'ordre :

1. **`postgres`** démarre, attend d'être `healthy` (`pg_isready`).
2. **`db-init`** (une fois `postgres` prêt) applique dans l'ordre : migrations Alembic (`alembic upgrade head`), seed de données de test (`database/seed/seed_data.py`), vues KPI Metabase (`dashboard/kpi_queries/*.sql`) — puis s'arrête (conteneur à usage unique, `exit 0` attendu).
3. **`admin_interface`** et **`metabase`** ne démarrent qu'une fois `db-init` terminé avec succès (`condition: service_completed_successfully`) — la base est déjà peuplée quand ils apparaissent, jamais de démarrage sur un schéma vide.

Vérifier que tout est monté :
```bash
docker compose ps
```
`db-init` doit apparaître `Exited (0)`, les autres `Up`/`healthy`.

## Point de vigilance : `db-init` ne deviendra pas le vrai pipeline ETL

`db-init` lance `database/seed/seed_data.py` — des données fictives/échantillon (50 lignes par source), avec un `TRUNCATE ... CASCADE` avant repeuplement. C'est fait pour le dev local et la démo, pas pour la production.

Le vrai pipeline (`etl/load/postgres_loader.py`, Sprint 2, chez Johane/William) est conçu différemment : upsert idempotent (`ON CONFLICT DO UPDATE`, cf. convention documentée dans `docs/plan_de_developpement.md`), volumes réels, **jamais** de `TRUNCATE` — et sa vocation est de tourner de façon récurrente via des DAG Airflow planifiés (Sprint 3), pas comme conteneur à usage unique déclenché par `docker compose up`.

**Ne jamais laisser `seed_data.py` dans `db-init` une fois que l'ETL réel alimente la base avec de vraies données** — le `TRUNCATE` effacerait tout à chaque `docker compose up`. Décision à prendre le moment venu (pas encore tranchée) :
- soit retirer `seed_data.py` de `db-init` et ne garder que les migrations (schéma), en laissant Airflow peupler les données indépendamment ;
- soit conditionner son exécution à une variable d'environnement dédiée (ex. `SEED_DEMO_DATA=true`), réservée aux environnements de démo/dev qui ne font pas tourner Airflow à côté.

## Accès aux services

| Service | URL | Identifiants |
|---|---|---|
| Interface admin (Gradio) | http://localhost:7860 | — |
| Metabase | http://localhost:3000 | à créer au premier lancement (voir ci-dessous) |
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

## Arrêt / nettoyage

```bash
docker compose down          # arrête et supprime les conteneurs, garde le volume postgres_data
docker compose down -v       # + supprime le volume (repart de zéro au prochain up)
```

## Dépannage

- **`admin_interface` crash au démarrage avec `UndefinedTable`** : ne devrait plus arriver depuis l'ajout de `db-init` (dépendance `service_completed_successfully`) — si ça se produit quand même, vérifier que `db-init` s'est bien terminé en `Exited (0)` (`docker compose logs db-init`) avant de relancer `admin_interface`.
- **Port déjà utilisé** (`5432`, `7860`, `3000`) : un autre conteneur ou service local occupe le port. `docker ps` pour identifier, ou changer le port hôte dans `.env` (`POSTGRES_PORT`, `ADMIN_INTERFACE_PORT`, `METABASE_PORT`).
- **Machine qui sature en mémoire avec plusieurs stacks docker-compose actives en parallèle** (ex. cette stack + une stack Airflow séparée) : arrêter les stacks non utilisées (`docker compose -p <projet> down`) plutôt que de les laisser tourner en continu — `docker ps` liste tous les conteneurs actifs tous projets confondus pour identifier ce qui peut être coupé.
