# Discours oral — HealthAI Coach

Script complet, slide par slide, rédigé en phrases à dire à voix haute (pas des puces). Sert de base personnelle pour Alexandre et de filet de sécurité si un collègue est empêché — les parties portant sur l'API (Rôle B, Florian) et l'ETL (Rôle C, Johane/William) sont rédigées avec le même niveau de détail que les parties Rôle A, pour être présentables par n'importe qui en cas de besoin.

Ce fichier n'est ni dans les slides ni dans les speaker notes Slidev — il vit à part, en complément.

---

## 1. Titre

Bonjour à tous. Nous allons vous présenter HealthAI Coach, le backend data engineering d'une plateforme de coaching santé, développé en équipe de quatre dans le cadre de cette formation Simplon. Je m'appelle Alexandre Laugier, avec moi Florian Abgrall, Johane Decamps et William Mibelli. On va dérouler le contexte, l'architecture, ce qu'on a construit concrètement, une démonstration live, puis un bilan honnête — obstacles compris.

## 2. Sommaire

Le fil conducteur est simple : d'abord le pourquoi — le contexte et les objectifs — puis le comment, à travers l'architecture, le modèle de données, le pipeline ETL et l'API. Ensuite vient la preuve : une démonstration live où on va montrer le système tourner réellement, avec de vraies données remplaçant les données de démonstration sous vos yeux. On terminera par un bilan.

## 3. Section — 01 · Contexte & objectifs

Avant de rentrer dans le technique, posons le décor : qui, pourquoi, pour qui.

## 4. HealthAI Coach, c'est quoi ?

HealthAI Coach est une plateforme de coaching santé : suivi nutritionnel, suivi de l'activité physique, relevés biométriques, et un profil médical déclaratif pour chaque utilisateur. L'objectif à terme est de générer des recommandations personnalisées — diététiques dès aujourd'hui, et bientôt des plans d'entraînement et de nutrition via un microservice IA. Je précise tout de suite le périmètre de ce qu'on présente : ce dépôt couvre exclusivement le backend data — la base de données, le pipeline ETL, l'API REST, la supervision de la qualité des données, et la conteneurisation. Il n'y a pas de frontend utilisateur final, c'est hors périmètre de cette formation. Les captures qu'on va montrer sont des outils internes — l'interface d'administration, Metabase — pas l'application finale destinée au grand public.

## 5. Modèle économique

Le projet repose sur deux offres, et ce n'est pas un détail cosmétique : ça a façonné des choix techniques concrets. D'un côté, un modèle freemium avec trois paliers — free, premium, premium_plus — où les fonctionnalités IA sont réservées aux paliers payants, avec un contrôle d'accès géré côté API. De l'autre, une offre B2B en marque blanche, pour des organisations partenaires comme des salles de sport, des mutuelles ou des entreprises — ce palier est provisionné par un administrateur, il n'y a pas de self-service. Ce modèle économique a directement façonné le schéma de base de données, avec la table subscriptions, les dépendances FastAPI comme CurrentPremiumUser, et les règles d'accès qu'on détaillera plus loin.

## 6. Répartition des rôles

Le travail a été réparti en trois rôles. Rôle A, le mien : architecture, base de données, interface d'administration, dashboard Metabase et dockerisation. Rôle B, Florian : l'API REST en FastAPI. Rôle C, Johane et William : le pipeline ETL et l'orchestration Airflow. On a adopté un flux de travail strict dès le départ : chaque étape correspond à une Pull Request, avec des tests obligatoires et une revue avant fusion. Ce workflow a payé — plusieurs bugs réels ont été attrapés en revue avant d'être fusionnés. Je précise aussi qu'en fin de projet, j'ai repris une partie de l'orchestration Airflow, l'équipe ETL n'ayant pas eu le temps matériel de la finaliser dans le calendrier de la formation.

## 7. Section — 02 · Architecture du système

Maintenant qu'on sait pourquoi, voyons comment le système est structuré globalement.

## 8. Vue d'ensemble

Voici le schéma d'ensemble. Des sources externes — des datasets Kaggle et l'API publique ExerciseDB — alimentent un pipeline ETL, orchestré par Airflow. Ce pipeline charge les données dans PostgreSQL, qui héberge seize tables. En aval, trois consommateurs indépendants viennent lire cette base : l'API REST pour les utilisateurs finaux, l'interface d'administration pour la qualité des données, et Metabase pour le pilotage et les tableaux de bord. Ces trois consommateurs ne communiquent jamais entre eux — ils sont chacun indépendamment connectés à PostgreSQL, qui reste la source de vérité unique. Tout ceci est conteneurisé via docker compose, sept services, démarrage en une seule commande. On reverra ce schéma en vrai pendant la démonstration.

## 9. Choix technologiques

Quelques choix méritent d'être justifiés. PostgreSQL plutôt qu'un SGBD NoSQL : notre domaine — utilisateurs, journaux nutrition et exercice historisés, contraintes d'intégrité inter-tables — est structurellement relationnel. Les nombreuses contraintes CHECK et FOREIGN KEY qui portent une partie significative des règles métier auraient dû être réimplémentées côté application dans un magasin sans schéma. Ce n'est pas un choix par défaut, c'est un choix motivé. Pour les migrations, Alembic : chaque évolution du schéma — par exemple l'ajout des tables organizations et subscriptions, puis plus tard workout_plans et nutrition_plans — devient un script Python versionné et rejouable, avec l'historique suivi en base via une table alembic_version, plutôt que des ALTER TABLE manuels non tracés. Pour l'interface d'administration, Gradio plutôt qu'un framework front complet comme React ou Streamlit : c'est un outil interne à faible surface, un seul écran avec quelques formulaires, où la rapidité de mise en œuvre prime sur la personnalisation visuelle — au prix de limitations d'accessibilité qu'on détaillera plus loin.

## 10. Section — 03 · Modélisation des données

C'est le cœur du projet : tout le reste — ETL, API, interface d'administration — s'organise autour de ce schéma.

## 11. Le schéma en un coup d'œil

Le schéma compte seize tables, organisées en cinq domaines fonctionnels autour de la table centrale USERS : nutrition, activité physique, suivi de santé déclaratif, abonnements, et contenu généré par IA. Un point sur lequel j'insiste : le schéma est auto-documenté. Chaque table et chaque colonne porte un commentaire directement en base, via COMMENT ON TABLE et COMMENT ON COLUMN. Ça veut dire que les conventions non triviales survivent dans la base elle-même, et pas seulement dans une documentation externe qui peut diverger avec le temps.

## 12. Modèle Conceptuel de Données

Voici le modèle conceptuel de données, au format Merise avec des cardinalités minimum-maximum. USERS est au centre, rattaché à huit domaines : nutrition, activité, biométrie, médical, alimentaire, forme physique, recommandations, et plans générés par IA. Sur ce schéma, un trait plein représente une clé étrangère obligatoire, un trait pointillé une clé étrangère optionnelle — par exemple le champ resolved_by de la table de qualité des données, qui est nullable tant que l'anomalie n'a pas été traitée.

## 13. Conventions d'intégrité

Deux conventions structurent tout le chargement de données. D'abord l'idempotence au chargement : les tables food_items et exercises portent une contrainte UNIQUE sur la paire source et external_id, ce qui permet un upsert via ON CONFLICT DO UPDATE — les DAG Airflow peuvent être rejoués sans jamais dupliquer de données. Ensuite, la génération de données manquantes : on utilise Faker avec une seed déterministe par ligne source, ce qui garantit qu'un même utilisateur ne change pas de nom à chaque ré-exécution du pipeline. Je vais vous raconter un bug réel qu'on a rencontré, capturé par une contrainte plutôt que par nos tests. On a une contrainte CHECK sur la colonne sex qui n'autorise que les valeurs F, M ou other, en minuscule. Or le code de l'ETL produisait à un moment 'Other' avec une majuscule au lieu de 'other'. PostgreSQL a rejeté cette valeur avec une CheckViolation — mais les quatre tests unitaires du module, eux, passaient sans problème, parce qu'ils travaillaient sur des entrées mockées et ne touchaient jamais la vraie contrainte. C'est cet incident précis qui a motivé notre discipline : toujours retester contre un vrai PostgreSQL, jamais seulement contre des mocks.

## 14. Conventions d'intégrité (suite)

Deuxième exemple de cohérence métier portée directement par la base plutôt que par le code applicatif : une contrainte CHECK sur la table subscriptions garantit qu'une organisation n'est renseignée que pour les abonnements de type B2B, et jamais pour les autres. Cette règle est impossible à contourner en écrivant directement en base — contrairement à une validation qui ne serait faite que côté API, et qu'on pourrait donc oublier ou contourner par erreur.

## 15. Section — 04 · Pipeline ETL & orchestration Airflow

C'est la section la plus riche en obstacles réels rencontrés dans ce projet.

## 16. Structure du pipeline

Le pipeline ETL se décompose en quatre étapes. Extract télécharge les quatre datasets Kaggle et pagine l'API ExerciseDB. Transform renomme les colonnes, type les données, et remplit les colonnes obligatoires manquantes de façon déterministe. Load fait un upsert idempotent — via une table de staging suivie d'un ON CONFLICT pour les catalogues food_items et exercises, et via un INSERT ON CONFLICT RETURNING pour la table users. Enfin, quality_check applique des règles réelles de qualité et journalise les anomalies détectées dans la table data_quality_log.

## 17. Extraction multi-sources (E)

Sur l'extraction, deux sources bien différentes. L'API ExerciseDB utilise une pagination par curseur, via un champ nextCursor, pour récupérer l'intégralité du catalogue d'exercices — cette pagination n'était pas clairement documentée côté API, elle a été découverte par tâtonnement par l'équipe ETL. Côté Kaggle, quatre datasets sont téléchargés automatiquement : nutrition, régimes alimentaires, utilisateurs de salle de sport, et suivi d'activité. Pour respecter les quotas d'API et éviter les blocages, des décorateurs de rate limiting — limits et sleep_and_retry — encadrent les appels. Enfin, toutes les données sont d'abord stockées brutes, en CSV et JSON, avant toute transformation : ça sert de filet de sécurité, en cas d'échec plus loin dans le pipeline, pas besoin de retélécharger.

## 18. Nettoyage & anonymisation (T)

L'étape de transformation gère trois choses. L'anonymisation d'abord, via la librairie Faker avec une seed fixée à 42 : ça génère de faux noms et emails cohérents, mais surtout reproductibles d'un run à l'autre, ce qui est précieux pour les tests et le débogage — et c'est justement ce caractère déterministe qui a permis de repérer le bug 'Other' contre 'other' évoqué plus tôt : avec un tirage aléatoire à chaque exécution, ce bug aurait été masqué de façon imprévisible selon les données tirées. Ensuite la normalisation : les valeurs Male et Female sont converties en M et F, les valeurs manquantes deviennent 'other'. Enfin la dérivation de champs : la date de naissance est calculée à partir de l'âge fourni par la source, et l'horodatage de fin de séance d'entraînement est calculé à partir de sa durée, puisque la source ne fournit que cette durée, pas l'heure de fin.

## 19. Chargement PostgreSQL (L)

Pour le chargement, trois choix techniques. D'abord des tables de staging : les données sont injectées rapidement via to_sql dans des tables temporaires, avant bascule vers les tables finales — ça évite de verrouiller la table finale pendant tout le chargement, ce qui devient important une fois qu'Airflow orchestre cette tâche en arrière-plan quotidiennement. Ensuite la stratégie UPSERT, déjà évoquée : ON CONFLICT DO UPDATE pour les catalogues food_items et exercises, garantissant l'idempotence. Enfin une historisation différenciée selon la nature de la donnée : les séries temporelles biométriques sont ajoutées en continu — on veut garder l'historique complet — tandis que les dimensions comme les profils utilisateurs sont synchronisées, on ne garde que l'état courant.

## 20. Orchestration Airflow

L'orchestration repose sur un DAG unique plutôt qu'un DAG par source — le volume de données de ce projet ne justifie pas une granularité plus fine. Trois tâches s'enchaînent séquentiellement, quotidiennement : extract, puis transform_and_load, puis quality_check. On a rencontré un problème réel ici : Airflow exige en interne une version de SQLAlchemy inférieure à 2.0, incompatible avec la version 2.0.51 utilisée partout ailleurs dans le projet. La solution a été d'isoler les dépendances ETL dans un venv Python dédié à l'intérieur de l'image Airflow, et de faire de chaque tâche du DAG un BashOperator qui invoque ce venv en sous-processus, plutôt qu'un PythonOperator qui importerait le code ETL directement dans le process Airflow. Ce conflit de dépendances, si on l'avait raté, aurait cassé le webserver et le scheduler — il a été détecté via les avertissements pip au moment du build de l'image, avant tout déploiement. Ce DAG a été testé de bout en bout avec de vraies données : deux mille huit cent cinquante et un utilisateurs, six cent quarante-cinq aliments, quatre cent quatre exercices chargés réellement.

## 21. Tableau de bord Airflow

Voici la page d'accueil d'Airflow, avec le DAG healthai_etl_pipeline enregistré, sa planification quotidienne, et son historique de runs — deux réussis, un échoué. Je n'ai pas nettoyé cet historique volontairement : ça reste cohérent avec l'esprit de cette présentation, on assume les obstacles réels plutôt que de les cacher. Cet échec précis vient d'un problème de permissions sur le dossier de logs d'Airflow, qui empêchait le processus de traitement des DAG d'écrire correctement — corrigé, et documenté dans notre guide de déploiement pour que ça ne bloque personne d'autre. On va déclencher un nouveau run en direct dans quelques instants, pendant la démonstration.

## 22. Section — 05 · API REST

Les données sont en base, voyons maintenant comment elles sont exposées. C'est le rôle B, celui de Florian.

## 23. Structure

L'API est construite avec FastAPI, toutes les routes sont préfixées /api/v1. L'architecture est en couches : les routers gèrent la couche HTTP, ils délèguent au module crud pour l'accès à la base de données, qui lui-même s'appuie sur les models — l'ORM SQLAlchemy — et les schemas — les modèles Pydantic de requête et réponse. Cette séparation entre models et schemas n'est pas cosmétique : elle évite d'exposer par accident une colonne sensible, comme un mot de passe haché, dans une réponse API. L'authentification repose sur des JWT, via un flow OAuth2 mot de passe, avec l'endpoint POST /auth/login. Trois dépendances réutilisables structurent le contrôle d'accès : CurrentUser, CurrentAdmin, et CurrentPremiumUser — déclarées une fois, réutilisées comme simple type d'argument dans n'importe quelle route, sans dupliquer de code de vérification. Enfin, une documentation interactive est générée automatiquement, accessible sur /docs pour Swagger et /redoc pour ReDoc.

## 24. Endpoints principaux

Les endpoints se regroupent en six familles. Auth, users et admin pour l'inscription, la connexion, le profil et la gestion administrateur. Food-items et exercises pour les catalogues alimentés par l'ETL — en lecture libre pour tout le monde, mais en écriture réservée aux administrateurs, puisque ce sont des données alimentées par le pipeline, pas par les utilisateurs. Nutrition-logs, workouts, biometrics et health-profiles pour les données propres à chaque utilisateur. Data-quality, qui offre une vue admin sur les anomalies — c'est une alternative programmatique à l'interface Gradio, utile pour intégrer d'autres outils comme des scripts ou du monitoring, pas seulement pour un humain derrière l'écran. Subscriptions et organizations pour les abonnements self-service et le provisionnement B2B. Et enfin ai, pour la génération de contenu, réservée aux paliers payants.

## 25. Documentation interactive (Swagger UI)

Voici un aperçu de la documentation Swagger, générée automatiquement par FastAPI à partir des schémas Pydantic — il n'y a aucune documentation à maintenir à la main, elle reste toujours synchronisée avec le code réel. Elle est testable en direct depuis le navigateur, via le bouton Authorize pour coller un token JWT. C'est exactement ce qu'on va montrer en action pendant la démonstration live plutôt que de rester sur cette simple capture d'écran.

## 26. Abonnements & microservice IA

Les endpoints de contenu IA — diet-recommendations, workout-plans, nutrition-plans — renvoient une erreur 403 pour un utilisateur en palier free, et 401 sans authentification du tout. Tout ce contrôle d'accès repose sur une seule dépendance FastAPI réutilisable, get_current_premium_user, qui vérifie l'abonnement actif de l'utilisateur et son palier avant de laisser passer la requête. Le microservice IA lui-même n'est pas encore déployé — on a mis en place un client stub qui reproduit fidèlement la signature du futur appel HTTP réel. Ça veut dire que brancher le vrai microservice, le jour où il sera prêt, ne changera qu'un seul fichier, sans toucher au reste de l'API. Je précise que c'est un pattern de préparation, pas une fonctionnalité IA livrée — on est honnête là-dessus. Tout ce mécanisme de gating est vérifié par des tests réels contre PostgreSQL, pas seulement des mocks.

## 27. Section — 06 · Interface admin & qualité des données

On revient ici sur mon périmètre, le rôle A : l'outil de pilotage de la qualité des données, pas l'application utilisateur.

## 28. Interface admin (Gradio)

Voici l'interface d'administration, construite avec Gradio, réservée aux comptes administrateurs. Elle centralise le tableau des anomalies de qualité de données détectées par l'ETL, avec des filtres, la possibilité de résoudre une anomalie manuellement, et un export en CSV ou JSON — tout sur un seul écran.

## 29. Accessibilité RGAA — démarche

Sur l'accessibilité, on a mené un audit automatisé plutôt qu'une simple relecture visuelle, pour objectiver le niveau de conformité réellement atteint, pas juste l'estimer à l'œil. Deux catégories de résultats. D'abord des choses corrigées : un contraste de texte insuffisant — les labels de champ étaient à 4,34 pour 1, le texte d'aide à seulement 2,56 pour 1, alors que le seuil requis est de 4,5 pour 1 — corrigé en fixant des couleurs plus foncées explicitement ; une hiérarchie de titres invalide, qui sautait de h1 à h3 sans passer par h2, corrigée aussi. Ensuite, une limitation non corrigible depuis notre propre code : le composant Dataframe de Gradio génère lui-même des violations ARIA internes, avec des éléments interactifs imbriqués et des noms accessibles manquants sur les cellules du tableau — c'est documenté comme une limitation connue du composant, pas contournée artificiellement. Je vais être transparent sur un point : ma propre vérification manuelle initiale était incomplète, j'avais raté les couleurs de texte d'aide réellement utilisées par le thème. C'est l'audit automatisé qui a révélé cette erreur. La leçon que j'en retiens : l'automatisation prime sur la relecture manuelle pour ce type de vérification.

## 30. Section — 07 · Dashboard Metabase

Ce dashboard est complémentaire à l'interface d'administration : une vue d'ensemble et de tendances, plutôt qu'une résolution au cas par cas.

## 31. Metabase

Metabase est connecté en lecture à PostgreSQL, avec accès aux quatorze tables et plusieurs vues KPI déjà construites, comme la répartition des repas par type ou les tendances biométriques. Une limitation qu'on assume : la personnalisation visuelle est restreinte par le plan gratuit self-hosted — on ne peut pas retirer le branding Metabase, les palettes de couleurs de graphiques sont limitées. Les vues apparaissent d'abord en table brute, comme dans n'importe quel outil de BI sans modèle pré-configuré ; il faut construire des Questions par-dessus pour obtenir des graphiques, ce qu'on a fait pour la démonstration.

## 32. Section — 08 · Dockerisation

Voyons maintenant comment tout ce qu'on vient de voir se lance en une seule commande.

## 33. Sept services, une commande

Une seule commande, docker compose up, orchestre tout l'environnement. Postgres démarre, puis db-init applique les migrations, le seed de données et les vues KPI, puis admin_interface, metabase et airflow-init démarrent, suivis d'airflow-webserver et airflow-scheduler. Pour Airflow, on a choisi un LocalExecutor avec une base partagée sur le postgres du projet, plutôt que le stack CeleryExecutor plus Redis complet vu en formation — un DAG unique ne justifie pas plusieurs workers, et la RAM de la machine de démo ne suit de toute façon pas sept services Airflow en plus du reste de la stack applicative. C'est un choix assumé de s'écarter du patron du TP, pour une raison concrète et mesurable : la mémoire disponible.

## 34. Point de vigilance — confirmé en conditions réelles

Un point de vigilance important : db-init, pensé pour la démo, fait un TRUNCATE avant de repeupler la base ; le vrai pipeline ETL, lui, ne tronque jamais. On a testé ça en pratique, pas seulement en théorie : après avoir chargé de vraies données via le DAG Airflow, un simple redémarrage du service admin_interface a redéclenché db-init, qui a immédiatement tout effacé pour revenir aux données de démonstration. Ce n'est donc pas un risque théorique, c'est un incident reproductible, qu'on a documenté. Et je peux ajouter, puisque c'est résolu depuis : on a mis en place une variable d'environnement, SEED_DEMO_DATA, qui conditionne ce comportement — une fois le vrai pipeline ETL en production, on la passe à false, et db-init n'applique plus que les migrations et les vues KPI, sans jamais toucher aux données réelles.

## 35. Section — 09 · Tests & CI/CD

Voici ce qui donne confiance que tout ce qu'on vient de montrer fonctionne vraiment, pas juste sur ma machine.

## 36. Suite de tests

Cent quarante et un tests au total, répartis en quatre modules, exécutés par GitHub Actions sur chaque Pull Request — migrations puis suite complète contre un Postgres éphémère. Je vais détailler les deux modules qui relèvent de mon rôle, le rôle A. D'abord tests/data_quality, qui vérifie le schéma lui-même contre un vrai PostgreSQL, pas un mock : il confirme que les seize tables sont bien créées, que les clés étrangères invalides sont rejetées, qu'un DELETE sur la table users cascade correctement vers nutrition_logs, et que la contrainte de cohérence sur data_quality_log tient — une anomalie ne peut pas être à la fois non résolue et porter une date de résolution. Cette suite fait un DROP puis un CREATE des tables à chaque exécution, donc elle tourne toujours contre une instance Postgres jetable, jamais contre une base contenant de vraies données. Ensuite tests/admin_interface, qui couvre la logique Python au-dessus du schéma : le filtrage et le tri des anomalies par sévérité ou par statut de résolution, le marquage d'une anomalie comme résolue avec l'identifiant de l'administrateur qui l'a traitée, et les exports CSV et JSON — en-têtes corrects, dates au format ISO, gestion propre des listes vides. La majorité de ces tests sont mockés, sauf test_db.py qui va contre une vraie base seedée pour vérifier les requêtes réelles. Cette différence entre les deux modules illustre bien la discipline du projet : on teste le schéma contre du vrai PostgreSQL parce que les contraintes CHECK et FOREIGN KEY portent une partie des règles métier, et un mock ne les vérifierait jamais — c'est exactement ce qui a concrètement attrapé le bug 'Other' contre 'other' qu'on a raconté plus tôt.

## 37. Section — 10 · Démonstration live

On quitte les slides pour quelques minutes, place à la démonstration en direct.

## 38. Ce qu'on va montrer

Quatre temps. D'abord l'interface d'administration : consultation, résolution et export des anomalies. Ensuite Metabase : le schéma et les KPI. Puis l'API : Swagger, l'authentification, et le gating premium en direct. Enfin Airflow : on va déclencher le DAG en direct, et montrer les vraies données remplacer les données de démonstration sous vos yeux.

*(Bascule vers le navigateur / terminal pour la démonstration live — se référer au guide de déploiement, section "Déroulé de démo bout-en-bout", et au parcours Swagger détaillé pour l'étape API.)*

## 39. Section — 11 · Bilan & conclusion

Retour sur les slides après la démonstration, pour prendre du recul sur ce qu'on vient de montrer.

## 40. Obstacles techniques rencontrés

Quatre obstacles réels, qu'on assume plutôt que de les cacher. Premièrement, les tests mockés ne remplacent pas une vraie base : le bug 'Other' contre 'other' passait les tests unitaires mais violait une contrainte réelle, détecté seulement contre un vrai PostgreSQL. Deuxièmement, ma propre vérification d'accessibilité RGAA manuelle était incomplète — l'audit automatisé a trouvé ce que j'avais raté à l'œil. Troisièmement, un problème de reproduction fidèle de la CI : un échec qui n'était pas reproductible en local, parce que l'environnement de test local avait plus de dépendances installées que l'environnement réel de la CI, ce qui masquait de vraies dépendances manquantes. Et quatrièmement, deux points d'architecture détectés et documentés avant qu'ils ne deviennent des incidents : le conflit de version SQLAlchemy entre Airflow et le reste du projet, et le comportement de db-init vis-à-vis du vrai pipeline ETL. Le fil rouge de tous ces obstacles : à chaque fois, c'est une vérification automatisée ou réelle qui a trouvé ce qu'une vérification manuelle ou mockée avait raté. C'est la leçon principale qu'on retient de ce projet.

## 41. Points positifs

Quatre points forts, qui ne sont pas juste "ça a marché" mais des choix d'architecture délibérés pris tôt, dès le Sprint 1, et qui ont payé plus tard dans le projet. Les contraintes d'intégrité sont portées par PostgreSQL, pas par le code applicatif — elles survivent à n'importe quel point d'entrée dans la base, qu'il vienne de l'API, de l'ETL, ou d'un accès direct. Le schéma est auto-documenté, les conventions restent lisibles depuis la base elle-même. La convention d'idempotence a été définie une seule fois, puis reprise à l'identique sur chaque nouvelle source de données ajoutée au fil du projet. Et une discipline de revue systématique — checkout isolé, tests toujours rejoués contre un Postgres frais, jamais de confiance aveugle dans un résultat non vérifié — a concrètement empêché plusieurs bugs, comme celui sur la contrainte sex, d'arriver jusqu'en production.

## 42. Conclusion

Pour conclure : on livre un schéma PostgreSQL complet, une API authentifiée, un pipeline ETL orchestré et testé en conditions réelles, une interface d'administration auditée RGAA, un dashboard Metabase, et une dockerisation qui démarre tout en une seule commande. Le facteur limitant de ce projet a été le temps disponible dans le cadre de cette formation, pas un blocage technique : le microservice IA n'est qu'esquissé sous forme de stub, le comportement de db-init vis-à-vis du vrai pipeline Airflow est documenté et résolu en cours de route. Le choix qu'on a fait, collectivement, a été de prioriser la robustesse de ce qui est livré plutôt que l'exhaustivité du périmètre imaginé au tout début du projet — un compromis assumé, pas un oubli.

## 43. Merci / Questions

Merci de votre attention, on est disponibles pour vos questions. *(Garder sous la main les chiffres clés : seize tables, cent quarante et un tests, deux mille huit cent cinquante et un utilisateurs chargés en démonstration réelle.)*
