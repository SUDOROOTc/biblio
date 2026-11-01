# Biblio : gestion de bibliothèque

API de gestion d'une bibliothèque de quartier : livres, lecteurs et réservations.

Projet réalisé dans le cadre du kata de stage Développeur Full Stack (Kainaa).

## Objectif

L'objectif n'est pas de tout faire, mais de montrer la façon de construire un logiciel : modélisation, tests, lisibilité et décisions assumées. Ce dépôt illustre une approche TDD avec une architecture en couches stricte.

## État d'avancement

| Élément | État | Détails |
| --- | --- | --- |
| Django 5.2, DRF, drf-spectacular | Fait | API REST + documentation OpenAPI/Swagger |
| Docker Compose (application + PostgreSQL) | Fait | Lancement identique sans installation locale |
| Schéma OpenAPI (`/api/schema/`) et interface Swagger (`/api/docs/`) | Fait | Configuré, testé et fonctionnel |
| Couche domaine (entités, règles métier, erreurs) | Fait | `Livre`, `Lecteur`, `Reservation`, `StatutReservation`, hiérarchie d'erreurs |
| Couche application (services, interfaces de dépôt, horloge) | Fait | `ServiceLivre`, `ServiceLecteur`, `ServiceReservation`, `Horloge`/`HorlogeFictive`, dépôts mémoire |
| Couche infrastructure (modèles Django, dépôts Django, migrations) | Fait | Modèles + dépôts Django, migration initiale, contrainte d'unicité partielle |
| API REST (livres, lecteurs, réservations) | Fait | Endpoints avec traduction des erreurs domaine -> codes HTTP |
| Test d'architecture | Fait | Vérifie la pureté de `domaine/` et `application/` |
| Test de concurrence (bug réservation) | Fait | Prouve la correction sur vraie base PostgreSQL |
| Expiration automatique des réservations (48h) | Partiel | `ServiceReservation.expirer_reservations()` implémenté, déclenchement non automatisé |
| Authentification du bibliothécaire | Non fait | Hors périmètre minimal choisi |

## Choix de stack

J'ai choisi **Python 3.12 et Django 5.2** car je les maîtrise le mieux. **Django REST Framework** permet de créer des API REST robustes et fiables, avec une sérialisation puissante et des contrôleurs bien structurés. **drf-spectacular** génère automatiquement la documentation OpenAPI et propose une interface de test interactive dans le navigateur pour tester directement les endpoints. **PostgreSQL** supporte les contraintes d'unicité partielles, indispensables pour garantir « une seule réservation active par livre ». **Docker Compose** assure un lancement identique sans installation locale, et **pytest**/**pytest-django** facilitent des tests lisibles décrivant le comportement métier.

## Architecture

Quatre couches avec dépendances vers l'intérieur :

```text
web → infrastructure → application → domaine
```

| Couche | Rôle | Connaît Django ? |
| --- | --- | --- |
| `src/domaine/` | Entités et règles métier pures (validations, transitions, suppression logique). | Non |
| `src/application/` | Services (cas d'usage), interfaces de dépôt, interface `Horloge`. | Non |
| `src/infrastructure/` | Modèles Django, dépôts Django, `HorlogeSysteme`, migrations. Seul à voir les modèles Django. | Oui |
| `src/web/` | Vues DRF, sérialiseurs (validation de forme uniquement), traduction erreurs domaine -> HTTP, URLs. | Oui |

Les services et dépôts échangent uniquement des **entités pures** du domaine. Les modèles Django ne contiennent aucune règle métier.

## Description du bug et stratégie de correction

### Problème dans le pseudo-code de l'énoncé

Le pseudo-code proposait un schéma « vérifier puis agir » :

```text
si livre.disponible:  # lecture
  creer_reservation(...)  # écriture
  livre.disponible = faux
  enregistrer(livre)
sinon lever_erreur("Livre déjà réservé")
```

Trois défauts majeurs :
1. **Condition de concurrence** : entre la vérification et l'écriture, une autre requête peut s'intercaler. Deux demandes simultanées peuvent créer deux réservations pour le même livre.
2. **Donnée dupliquée** : le champ `disponible` duplique l'information déjà portée par les réservations actives et risque la désynchronisation.
3. **Non-atomicité** : deux écritures distinctes ne forment pas une opération atomique.

### Stratégie retenue

- **Suppression du champ `disponible`** : la disponibilité d'un livre se déduit des réservations actives (`RESERVEE` ou `EMPRUNTEE`). Aucune donnée stockée redondante.
- **Garantie par la base** : ajout d'une **contrainte d'unicité partielle** dans PostgreSQL sur `reservation(livre_id)` lorsque le statut est `RESERVEE` ou `EMPRUNTEE` (`unique_reservation_active_par_livre`).
- **Vérification applicative conservée** : le `ServiceReservation` vérifie explicitement (`existe_active_pour_livre`, quota du lecteur) pour fournir des messages d'erreur clairs et explicites.
- **Traduction de l'erreur** : le `DepotReservationDjango` intercepte l'`IntegrityError` levée par la contrainte et la traduit en `ErreurConflit("Livre déjà réservé.")`, cohérente avec le reste de la hiérarchie d'erreurs.
- **Preuve par le test** : `tests/infrastructure/test_concurrence_reservation.py` lance **deux threads en parallèle** sur le **même livre** avec **deux lecteurs différents** sur une **vraie base PostgreSQL**. Résultat : **1 seul succès, 1 seul échec avec `ErreurConflit`**.

## Règles métier implémentées

- **Cycle de vie** : `RESERVEE → EMPRUNTEE → RETOURNEE`, avec `ANNULEE` ou `EXPIREE` comme issues. Toute transition invalide est refusée par l'entité (`ErreurTransitionInvalide`).
- **RG1** : au plus **une réservation active par livre**. Garanti par la **contrainte d'unicité partielle en base** (renforcé par une vérification applicative).
- **RG2** : au plus **3 réservations actives par lecteur**, vérifié par le service.
- **Expiration** : une réservation `RESERVEE` non retirée sous **48 heures** expire (`ServiceReservation.expirer_reservations()`). L'horloge est injectée (`HorlogeSysteme` en production, `HorlogeFictive` en tests).
- **Suppression logique** : `Livre` et `Lecteur` utilisent `date_suppression` au lieu d'une suppression physique. Un livre/lecteur avec une réservation active ne peut pas être supprimé logiquement.
- **Unicité de l'email** : contrainte d'unicité partielle sur `LecteurModel.email` pour les lecteurs non supprimés.
- **Horloge injectée** : toutes les règles dépendant du temps reçoivent l'heure en paramètre (dans les entités) ou passent par `Horloge`. Aucun `datetime.now()`/`timezone.now()` dans `domaine/` ou `application/` (garanti par le test d'architecture).

## API REST

Routes principales sous `/api/` :

| Méthode | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/livres` | Créer un livre |
| `PUT` | `/api/livres/<uuid>` | Modifier un livre |
| `DELETE` | `/api/livres/<uuid>` | Supprimer logiquement un livre |
| `GET` | `/api/livres/recherche?q=...` | Rechercher par titre/auteur |
| `POST` | `/api/lecteurs` | Créer un lecteur |
| `PUT` | `/api/lecteurs/<uuid>` | Modifier un lecteur |
| `DELETE` | `/api/lecteurs/<uuid>` | Supprimer logiquement un lecteur |
| `GET` | `/api/lecteurs/<uuid>/reservations` | Consulter un lecteur et ses réservations actives |
| `GET` | `/api/reservations` | Lister les réservations |
| `POST` | `/api/reservations` | Créer une réservation (`livre_id`, `lecteur_id`) |
| `POST` | `/api/reservations/<uuid>/annuler` | Annuler une réservation (`RESERVEE` uniquement) |
| `POST` | `/api/reservations/<uuid>/emprunter` | Enregistrer un emprunt (`RESERVEE` → `EMPRUNTEE`) |
| `POST` | `/api/reservations/<uuid>/retourner` | Enregistrer un retour (`EMPRUNTEE` → `RETOURNEE`) |

**Traduction des erreurs domaine → HTTP** (centralisée dans `src/web/exceptions.py`) :
- `ErreurIntrouvable` → `404 Not Found`
- `ErreurConflit` (RG1, RG2, suppression bloquée) → `409 Conflict`
- `ErreurValidation`, `ErreurTransitionInvalide` → `422 Unprocessable Entity`

Le code HTTP pour le dépassement de quota (RG2) a été choisi comme **409 Conflict** (conflit d'état/règle métier), cohérent avec les autres cas de conflit.

## Installation et lancement

Prérequis : Docker et Docker Compose.

```powershell
# 1. Créer le fichier d'environnement
Copy-Item .env.example .env

# 2. Construire et démarrer
docker compose up --build
```

L'API écoute sur le port 8000.
- Schéma OpenAPI : [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
- Interface Swagger : [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

## Tests

```powershell
docker compose run --rm web pytest
```

Tests rangés par couche : `tests/domaine/`, `tests/application/`, `tests/infrastructure/`, `tests/web/`, `tests/architecture/`. Le test d'architecture garantit la pureté des couches `domaine/` et `application/`. Le test de concurrence valide la correction du bug sur vraie base PostgreSQL.

## Décisions et compromis

### Décisions prises
- **"Disponible" déduit** : aucun booléen stocké, calculé à partir des réservations actives.
- **Garantie atomique en base** : contrainte d'unicité partielle pour RG1, traduite en erreur métier explicite.
- **"Vérifier puis écrire" durci** : conservé dans le service pour des messages clairs, mais rendu sûr par la contrainte PostgreSQL + test de concurrence.
- **Horloge injectée** : `HorlogeSysteme` / `HorlogeFictive` pour rendre l'expiration testable sans attendre.
- **Suppression logique** : conservation de l'historique via `dateSuppression`.
- **Entités pures** : règles dans les entités quand elles ne dépassent pas leur périmètre, règles inter-objets (RG1/RG2) dans les services.
- **Dépôts Django isolés** : seuls les dépôts infrastructure voient les modèles Django, conversion entité ↔ modèle systématique.
- **API REST** : contrôleurs minces, traduction centralisée des erreurs domaine → HTTP.
- **TDD** : test rouge → vert → refactor à chaque cycle significatif.

### Limites assumées / non fait
- **Authentification** : non implémentée. Le contexte indique que le bibliothécaire saisit les actions (non un lecteur se connectant). Signalé comme non fait.
- **Tâche planifiée pour l'expiration** : `expirer_reservations()` existe et est testée, mais aucun cron/worker n'est configuré. L'expiration peut être appelée à l'opération ou via une tâche planifiée ultérieurement.
- **Pagination / filtres avancés** : non implémentés (hors périmètre essentiel/important prioritaire).
- **Historique des réservations passées** : non implémenté (bonus).
- **Vue mobile / PWA** : non implémenté (bonus).
- **CI** : non configuré.

## Liens

- Schéma OpenAPI : [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
- Interface Swagger : [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
