# Biblio : gestion de bibliothèque

API de gestion d'une bibliothèque de quartier : livres, lecteurs et réservations.
Projet réalisé pour le kata de stage Développeur Full Stack (Kainaa).

> Ce README est volontairement minimal : il décrit l'état réel du dépôt et sera complété au fil des cycles de développement. Les éléments marqués **À compléter** ne sont pas encore décidés ou réalisés.

## État d'avancement

| Élément | État |
|---|---|
| Django, Django REST Framework et drf-spectacular configurés | fait |
| Docker Compose (application + PostgreSQL 17) | fait |
| Schéma OpenAPI (`/api/schema/`) et interface Swagger (`/api/docs/`) | fait, testé |
| Couche domaine (entités, règles métier) | à venir |
| Couche application (services, interfaces de dépôt, horloge) | à venir |
| Couche infrastructure (modèles Django, dépôts, migrations) | à venir |
| Endpoints livres, lecteurs, réservations | à venir |
| Correction du bug de double réservation et test de concurrence | à venir |

## Choix de stack

- **Python 3.12 et Django 5.2** : la stack que je maîtrise le mieux, avec un ORM et des migrations intégrés.
- **Django REST Framework et drf-spectacular** : API REST et documentation OpenAPI générée à partir du code.
- **PostgreSQL** : il supporte les index d'unicité partiels, dont dépend la garantie « une seule réservation active par livre » (voir la section sur le bug).
- **Docker Compose** : lancement identique sur toutes les machines, sans installer Python ni PostgreSQL.
- **pytest et pytest-django** : tests lisibles, qui décrivent le comportement métier.

## Installation et lancement

Prérequis : Docker et Docker Compose.

```powershell
# 1. Créer le fichier d'environnement à partir du modèle, puis ajuster les valeurs
Copy-Item .env.example .env

# 2. Construire et démarrer l'application et la base
docker compose up --build
```

L'API écoute sur le port 8000 (voir « Liens » en fin de document).

**À compléter** : commande de création des tables (migrations) et du compte bibliothécaire, quand ils existeront.

## Tests

```powershell
docker compose run --rm web pytest
```

Les tests sont rangés par couche dans `tests/` : `web/` existe aujourd'hui ; `domaine/`, `application/` et `infrastructure/` viendront avec chaque couche.

## Architecture

Quatre couches, avec des dépendances qui vont toujours vers le domaine :

| Couche | Rôle | Connaît Django ? |
|---|---|---|
| `src/domaine/` (à venir) | entités et règles propres à chaque objet (validité, transitions d'état) | non |
| `src/application/` (à venir) | services (cas d'utilisation, règles entre plusieurs objets), interfaces de dépôt, interface d'horloge | non |
| `src/infrastructure/` (à venir) | modèles Django, dépôts Django, horloge réelle | oui |
| `src/web/` | vues et sérialisation : valident la forme de la requête, appellent les services, traduisent les erreurs en codes HTTP | oui |

Les règles métier ne sont donc ni dans la couche HTTP ni dans la base de données. Les dépôts sont la seule frontière entre les entités du domaine et les modèles Django.

## Décisions et compromis

**Décisions prises**

- Une réservation est **active** quand elle est `RESERVEE` ou `EMPRUNTEE`. Un livre est **disponible** quand il n'a aucune réservation active : cette information est déduite, jamais stockée.
- Cycle de vie : `RESERVEE` vers `EMPRUNTEE`, `ANNULEE` ou `EXPIREE` ; `EMPRUNTEE` vers `RETOURNEE`. Toute autre transition est refusée. `RETOURNEE`, `ANNULEE` et `EXPIREE` sont terminaux.
- Un lecteur a au plus 3 réservations actives, vérifié à la création d'une réservation.
- Un livre a au plus une réservation active, garanti par une contrainte d'unicité partielle en base.
- Suppression d'un livre ou d'un lecteur : refusée s'il a une réservation active, sinon **suppression logique** (`dateSuppression`), pour conserver l'historique.
- L'horloge est injectée via une interface, pour tester l'expiration à 48 h sans attendre.
- Le lecteur n'utilise pas le système : le bibliothécaire saisit réservations, annulations, emprunts et retours.

**Limites assumées**

- Pas de gestion des exemplaires : un livre correspond à un seul exemplaire.
- Pas d'état « perdu » : un livre emprunté et perdu reste emprunté, et ne peut donc pas être supprimé.
- Un emprunt passe toujours par une réservation préalable.

## Le bug de la réservation

Le pseudo-code de l'énoncé a trois défauts de conception :

1. **Vérifier puis agir** : entre la lecture de la disponibilité et la création de la réservation, une autre requête peut s'intercaler. Deux demandes simultanées peuvent donc créer deux réservations pour le même livre (condition de concurrence).
2. **Un champ `disponible` dupliqué** : il répète une information déjà portée par les réservations, et peut se désynchroniser (par exemple après une expiration).
3. **Deux écritures non atomiques** : si le programme s'arrête entre l'enregistrement de la réservation et celui du livre, l'état devient incohérent.

**Stratégie retenue** : supprimer le champ `disponible` (la disponibilité se déduit des réservations) et confier la garantie à la base, avec un index d'unicité partiel sur le livre pour les réservations actives. La vérification préalable reste utile pour donner un message clair, mais elle ne garantit rien. L'erreur de la base est traduite en erreur métier explicite (« livre déjà réservé »).

**À compléter** : implémentation et test de concurrence (deux demandes simultanées sur le même livre, sur une vraie base PostgreSQL).

## À compléter avant le rendu

- Expiration des réservations : tâche planifiée, ou vérification à chaque opération.
- Code HTTP quand le quota est dépassé : 409 ou 422.
- Unicité de l'e-mail d'un lecteur : index partiel PostgreSQL, ou vérification applicative.
- Authentification du bibliothécaire : périmètre d'implémentation.
- Liste finale de ce qui est fait, et de ce qui ne l'est pas, avec les raisons.

## Liens

- Schéma OpenAPI : http://localhost:8000/api/schema/
- Interface Swagger : http://localhost:8000/api/docs/
