---
theme: seriph
highlighter: shiki
lineNumbers: false
transition: slide-left
title: HealthAI Coach — Soutenance de projet
controls: false
---

# HealthAI Coach
## Backend Data Engineering

Nutrition, activité physique, qualité des données — de l'ingestion à l'orchestration

<br>

Alexandre Laugier · Florian Abgrall · Johane Decamps · William Mibelli

Juillet 2026

<!--
- Bonsoir, je présente le backend data de HealthAI Coach, une plateforme de coaching santé
- Équipe de 4 : répartition en 3 rôles (architecture/data, API, ETL)
- Plan : contexte -> architecture -> ce qui a été construit -> démo live -> bilan
- Durée cible ~50 min avec la démo
-->

---

# Sommaire

1. Contexte & objectifs
2. Architecture du système
3. Modélisation des données
4. Pipeline ETL & orchestration Airflow
5. API REST
6. Interface admin & qualité des données
7. Dockerisation
8. Tests & CI/CD
9. Démonstration live
10. Bilan & conclusion

<!--
- Progression : POURQUOI (contexte) -> COMMENT (architecture, modèle, pipeline, API) -> PREUVE (démo live) -> BILAN
- La démo live est le moment fort : on y verra les données réelles remplacer les données de démo en direct
-->

---
layout: section
---

# 01 · Contexte & objectifs

---

# HealthAI Coach, c'est quoi ?

- Plateforme de **coaching santé** : suivi nutritionnel, activité physique, relevés biométriques, profil médical déclaratif
- Génération de recommandations personnalisées (diététiques aujourd'hui, plans d'entraînement/nutrition via microservice IA à venir)
- Ce dépôt = le **backend data** uniquement : base de données, pipeline ETL, API REST, supervision qualité, conteneurisation
- Pas de frontend utilisateur final — hors périmètre de cette formation

<!--
- Insister sur le périmètre : c'est un projet backend/data, pas une appli complète
- Les captures qu'on montrera sont des outils internes (admin, Metabase), pas l'app finale
-->

---

# Modèle économique

Deux offres, qui conditionnent des choix techniques concrets :

- **Freemium** — `free` / `premium` / `premium_plus`
  → fonctionnalités IA réservées aux paliers payants (gating côté API)
- **B2B en marque blanche** — organisations partenaires (salles de sport, mutuelles, entreprises)
  → provisionné par un admin, pas de self-service pour ce palier

<!--
- Le modèle économique n'est pas cosmétique : il a façonné le schéma (table subscriptions),
  les dépendances FastAPI (CurrentPremiumUser), et les règles d'accès
-->

---

# Répartition des rôles

| Rôle | Périmètre | Qui |
|---|---|---|
| **A** | Architecture, base de données, interface admin, Metabase, dockerisation | Alexandre |
| **B** | API REST (FastAPI) | Florian Abgrall |
| **C** | Pipeline ETL, orchestration Airflow | Johane, William |

Flux de travail : une étape = une Pull Request, tests obligatoires, revue avant fusion

<!--
- Workflow Git strict dès le départ : ça a payé, plusieurs bugs réels attrapés en revue avant fusion
- Le rôle A a repris une partie de l'orchestration Airflow en fin de projet, faute de temps côté équipe ETL
-->

---
layout: section
---

# 02 · Architecture du système

---

# Vue d'ensemble

```
Sources externes (Kaggle, API ExerciseDB)
        │
        ▼
   ETL (extract/transform/load) ◄── Airflow (orchestration)
        │
        ▼
     PostgreSQL (16 tables)
      │        │        │
      ▼        ▼        ▼
  API REST  Interface  Metabase
  (FastAPI)  admin      (dashboard KPI)
             (Gradio)
```

Tout conteneurisé via `docker compose` (sept services), une seule commande

<!--
- L'ETL alimente Postgres, orchestré par Airflow
- Trois consommateurs en aval : API pour les utilisateurs finaux, interface admin pour la qualité, Metabase pour le pilotage
- On reverra ce schéma en vrai pendant la démo
-->

---

# Choix technologiques

<div class="text-sm">

| Composant | Techno | Pourquoi |
|---|---|---|
| Base de données | PostgreSQL | Domaine relationnel — contraintes CHECK/FK portent les règles métier |
| Migrations | Alembic | |
| Orchestration | Apache Airflow | |
| API | FastAPI | SQLAlchemy, Pydantic, JWT |
| Dashboard | Metabase | |
| Interface admin | Gradio | Outil interne à faible surface, rapidité prime sur personnalisation |
| Conteneurisation | Docker Compose | |

</div>

<!--
- PostgreSQL plutôt que NoSQL : les contraintes d'intégrité (CHECK, FK) auraient dû être
  réimplémentées côté application dans un magasin sans schéma — pas un choix par défaut, un choix motivé
- Gradio : compromis assumé, au prix de limitations d'accessibilité qu'on détaillera
-->

---
layout: section
---

# 03 · Modélisation des données

---

# Le schéma en un coup d'œil

- **16 tables**, 5 domaines fonctionnels autour de `USERS` :
  nutrition · activité physique · suivi de santé déclaratif · abonnements · contenu généré par IA
- Schéma **auto-documenté** : `COMMENT ON TABLE/COLUMN` directement en base
  → les conventions non triviales survivent, pas seulement dans un doc externe qui peut diverger

<!--
- Le choix d'auto-documenter en SQL est un point fort qu'on assumera dans le bilan
-->

---

# Modèle Conceptuel de Données

<img src="./img/mcd_core.png" class="mx-auto h-105" />

<!--
- Cardinalités au format Merise (min,max)
- USERS au centre, rattaché à 8 domaines : nutrition, activité, biométrie, médical, alimentaire,
  forme, recommandations, plans IA
- Trait plein = FK obligatoire, pointillé = FK optionnelle (ex. resolved_by, nullable)
-->

---

# Conventions d'intégrité

- **Idempotence au chargement** : `UNIQUE(source, external_id)` sur `food_items`/`exercises`
  → upsert (`ON CONFLICT DO UPDATE`), les DAG Airflow peuvent être rejoués sans dupliquer
- **Génération de données manquantes** : `Faker.seed()` déterministe par ligne source
  → un même utilisateur ne change pas de nom à chaque ré-exécution du pipeline
- **Cohérence métier en base**, pas dans le code : ex. `chk_subscriptions_b2b_organization`
  garantit qu'une organisation n'est renseignée que pour les abonnements B2B

<!--
- Point à raconter : un bug réel où l'ETL produisait 'Other' (majuscule) au lieu de 'other',
  rejeté par PostgreSQL mais indétecté par les tests unitaires mockés — on y revient dans le bilan
-->

---
layout: section
---

# 04 · Pipeline ETL & orchestration Airflow

---

# Structure du pipeline

<img src="./img/etl_flow.png" class="mx-auto w-full" />

<!--
- extract : télécharge les 4 datasets Kaggle + pagine l'API ExerciseDB
- transform : renommage colonnes, typage, remplissage déterministe
- load : upsert idempotent (staging + ON CONFLICT pour food_items/exercises,
  INSERT...ON CONFLICT...RETURNING pour users)
- quality_check : règles réelles, journalise dans data_quality_log
-->

---

# Orchestration Airflow

- **Un DAG unique** plutôt qu'un DAG par source : le volume ne justifie pas plus de granularité
- `extract` → `transform_and_load` → `quality_check`, séquentiel, `@daily`
- **Problème réel rencontré** : Airflow exige `SQLAlchemy<2.0` en interne, incompatible avec le
  `2.0.51` utilisé partout ailleurs dans le projet
  → **venv Python isolé** (`/opt/etl-venv`) à l'intérieur de l'image Airflow, tâches en `BashOperator`
- Testé de bout en bout avec de **vraies données** : 2851 users, 645 food_items, 404 exercises chargés

<!--
- Ce conflit de dépendances aurait cassé le webserver/scheduler si on l'avait raté —
  détecté via les warnings pip au build de l'image, avant tout déploiement
- Repris par le rôle A en fin de projet, l'équipe ETL n'ayant pas le temps matériel de le finir
-->

---
layout: section
---

# 05 · API REST

---

# Structure

- FastAPI, toutes les routes préfixées `/api/v1`
- Architecture en couches : `routers/` (HTTP) → `crud/` (accès DB) → `models/` (ORM) + `schemas/` (Pydantic)
- Authentification **JWT** (OAuth2 password flow) : `POST /auth/login`
- Trois dépendances réutilisables : `CurrentUser`, `CurrentAdmin`, `CurrentPremiumUser`
- Documentation interactive auto-générée : `/docs` (Swagger), `/redoc`

---

# Endpoints principaux

- **auth / users / admin** — inscription, connexion, profil, gestion admin
- **food-items / exercises** — catalogues ETL, lecture libre, écriture admin
- **nutrition-logs / workouts / biometrics / health-profiles** — données propres à l'utilisateur
- **data-quality** — vue admin sur les anomalies, alternative programmatique à l'interface Gradio
- **subscriptions / organizations** — abonnements self-service + provisionnement B2B
- **ai** — génération de contenu, réservée aux paliers payants

---

# Abonnements & microservice IA

- Contenu IA (`/ai/diet-recommendations`, `/ai/workout-plans`, `/ai/nutrition-plans`) : 403 en `free`, 401 sans auth
- Microservice pas encore déployé → **client stub** (`api/services/ai_client.py`) reproduisant
  la signature du futur appel HTTP réel
- Objectif : brancher le vrai microservice ne changera que ce fichier, pas les routers ni le contrat exposé
- Vérifié par des tests réels contre PostgreSQL (gating, persistance, isolation par utilisateur)

<!--
- C'est un pattern de préparation, pas une fonctionnalité IA livrée — être honnête là-dessus à l'oral
-->

---
layout: section
---

# 06 · Interface admin & qualité des données

---

# Interface admin (Gradio)

<img src="./img/admin_interface_consultation.png" class="mx-auto h-90 rounded shadow" />

<!--
- Filtres, tableau des anomalies, correction manuelle, export CSV/JSON — tout sur un écran
-->

---

# Accessibilité RGAA — démarche

- Audit **automatisé** (pas seulement une relecture visuelle) pour objectiver la conformité réelle
- **Corrigé** : contraste insuffisant (labels 4,34:1, texte d'aide 2,56:1, seuil requis 4,5:1) →
  couleurs foncées explicitement ; hiérarchie de titres invalide (h1 → h3 sans h2) → corrigée
- **Non corrigible depuis notre code** : le composant `Dataframe` de Gradio génère des violations
  ARIA internes (éléments imbriqués, noms accessibles manquants) — documenté comme limitation connue

<!--
- Ma propre première vérification manuelle était incomplète : j'avais raté les couleurs de texte
  info=/labels réellement utilisées — l'audit automatisé a révélé l'erreur, corrigé depuis
- Leçon retenue : l'automatisation prime sur la relecture manuelle pour ce type de vérification
-->

---
layout: section
---

# 07 · Dashboard Metabase

---

# Metabase

<img src="./img/metabase_dashboard_db.png" class="mx-auto h-70 rounded shadow" />

- 14 tables + plusieurs vues KPI pré-construites (`vw_nutrition_meal_type_breakdown`, `vw_biometric_trend`...)
- Limitation assumée : personnalisation visuelle restreinte au plan gratuit (pas de retrait du branding, palettes limitées)

<!--
- Les vues apparaissent en table brute par défaut (comme n'importe quel outil BI sans modèle
  pré-configuré) — il faut construire des Questions dessus pour avoir des graphiques, fait pour la démo
-->

---
layout: section
---

# 08 · Dockerisation

---

# Sept services, une commande

```bash
docker compose up -d --build
```

- **postgres** → **db-init** (migrations + seed + vues KPI) → **admin_interface** / **metabase** / **airflow-init** → **airflow-webserver** / **airflow-scheduler**
- Airflow en `LocalExecutor` + base partagée sur le postgres du projet, pas le stack Celery+Redis complet vu en formation
  → un DAG unique ne justifie pas plusieurs workers, et la RAM de la machine de démo ne suit pas

<!--
- Choix assumé de s'écarter du patron du TP (CeleryExecutor) pour une raison concrète : mémoire
-->

---

# Point de vigilance — confirmé en conditions réelles

- `db-init` (démo) fait un `TRUNCATE` avant repeuplement ; le vrai pipeline ETL ne tronque jamais
- **Testé en pratique** : après avoir chargé de vraies données via le DAG Airflow, un simple
  redémarrage d'`admin_interface` a **redéclenché `db-init`** et tout effacé
- Pas un risque théorique — un incident reproductible, documenté, décision encore à trancher

<!--
- Ce point illustre bien la démarche du projet : documenter le risque avant qu'il n'arrive,
  puis le confirmer/corriger avec des données réelles plutôt que de le laisser hypothétique
-->

---
layout: section
---

# 09 · Tests & CI/CD

---

# Suite de tests

| Module | Périmètre | Fichiers |
|---|---|---|
| `tests/data_quality/` | Schéma SQL : FK, CHECK, cascades | 1 |
| `tests/admin_interface/` | Logique pure + DB réelle | 3 |
| `tests/api/` | Auth, users, organizations, subscriptions | 7 |
| `tests/etl/` | Transform (mockées) + quality (DB réelle) | 3 |

**141 tests**, GitHub Actions sur chaque PR (migrations + suite complète contre Postgres éphémère)

<!--
- Les tests contre une vraie base (pas des mocks) sont un choix délibéré : les contraintes
  CHECK/FK portent une partie des règles métier, un mock ne les vérifie pas
- Ça a concrètement attrapé un bug qu'on racontera dans le bilan
-->

---
layout: section
---

# 10 · Démonstration live

---

# Ce qu'on va montrer

1. **Interface admin** — consultation, résolution, export des anomalies
2. **Metabase** — schéma et KPI
3. **API** — Swagger, authentification, gating premium
4. **Airflow** — déclenchement du DAG en direct, vraies données remplaçant les données de démo

<!--
- Basculer sur le terminal / navigateur maintenant
- Rappel pour moi : ne pas relancer docker compose une fois le DAG déclenché (risque TRUNCATE)
-->

---
layout: section
---

# 11 · Bilan & conclusion

---

# Obstacles techniques rencontrés

- **Les tests mockés ne remplacent pas une vraie base** — un bug de valeur (`'Other'` au lieu de `'other'`)
  passait les tests unitaires mais violait une contrainte réelle, détecté seulement contre Postgres
- **Ma vérification RGAA manuelle était incomplète** — l'audit automatisé a trouvé ce que j'avais raté
- **Reproduction fidèle de la CI** — un échec non reproductible en local car l'environnement de test
  avait plus de dépendances que la CI réelle
- **Conflit SQLAlchemy avec Airflow**, **`db-init` vs pipeline réel** — détectés et documentés avant incident

<!--
- Le fil rouge : chaque fois, la vérification automatisée/réelle a trouvé ce qu'une vérification
  manuelle ou mockée avait raté — c'est la leçon principale du projet
-->

---

# Points positifs

- Contraintes d'intégrité portées par PostgreSQL, pas le code applicatif — survivent à n'importe quel point d'entrée
- Schéma auto-documenté, conventions lisibles depuis la base elle-même
- Convention d'idempotence définie une fois, reprise à l'identique sur chaque nouvelle source
- Discipline de revue systématique : checkout isolé, tests rejoués contre Postgres frais, jamais de confiance aveugle

---

# Conclusion

- Schéma PostgreSQL complet, API authentifiée, **pipeline ETL orchestré et testé en conditions réelles**,
  interface admin auditée RGAA, dashboard Metabase, dockerisation en une commande
- Facteur limitant : le **temps** de la formation, pas un blocage technique
  → microservice IA esquissé (stub), conflit `db-init`/Airflow documenté mais pas tranché
- Choix assumé : prioriser la **robustesse** de ce qui est livré plutôt que l'exhaustivité du périmètre imaginé au départ

<!--
- Message de clôture : compromis assumé, pas un oubli
-->

---
layout: center
class: text-center
---

# Merci

## Questions ?

<!--
- Ouvrir les questions
- Garder sous la main : les chiffres clés (16 tables, 141 tests, 2851 users chargés en démo)
-->
