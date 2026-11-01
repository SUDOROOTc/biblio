# Contrat API Biblio

## Accès

- Base URL locale : `http://localhost:8000`
- Toutes les routes métier commencent par `/api/`.
- Les routes métier nécessitent un bibliothécaire authentifié.
- Format des requêtes et réponses : `application/json`.
- Les identifiants sont des UUID.
- Les dates sont des chaînes ISO 8601, par exemple `2026-11-01T10:00:00+00:00`.

Le frontend peut utiliser l'authentification de session Django :

```http
POST /api/auth/login/
Content-Type: application/x-www-form-urlencoded
```

Champs : `username`, `password`. Pour les requêtes suivantes, conserver le cookie de session.

## Livres

### Créer un livre

```http
POST /api/livres
```

```json
{
  "titre": "Dune",
  "auteur": "Frank Herbert",
  "annee_publication": 1965
}
```

Réponse `201` :

```json
{
  "id": "uuid",
  "titre": "Dune",
  "auteur": "Frank Herbert",
  "annee_publication": 1965,
  "date_suppression": null
}
```

### Modifier un livre

```http
PUT /api/livres/{livre_id}
```

Le corps contient les trois champs : `titre`, `auteur`, `annee_publication`.

Réponse : `200` avec le livre modifié.

### Supprimer logiquement un livre

```http
DELETE /api/livres/{livre_id}
```

Réponse : `204` sans contenu.

### Rechercher des livres

```http
GET /api/livres/recherche?q=dune&annee_publication=1965&page=1&page_size=10
```

Tous les paramètres sont optionnels. La recherche porte sur le titre ou l'auteur.

Réponse `200` :

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": []
}
```

`next` et `previous` contiennent le numéro de page ou `null`.

## Lecteurs

### Créer un lecteur

```http
POST /api/lecteurs
```

```json
{
  "nom": "Ada Lovelace",
  "email": "ada.lovelace@example.com"
}
```

Réponse `201` : lecteur contenant `id`, `nom`, `email` et `date_suppression`.

### Modifier un lecteur

```http
PUT /api/lecteurs/{lecteur_id}
```

Le corps contient `nom` et `email`.

Réponse : `200` avec le lecteur modifié.

### Supprimer logiquement un lecteur

```http
DELETE /api/lecteurs/{lecteur_id}
```

Réponse : `204` sans contenu.

### Consulter un lecteur et ses réservations actives

```http
GET /api/lecteurs/{lecteur_id}/reservations
```

Réponse `200` :

```json
{
  "lecteur": {},
  "reservations_actives": []
}
```

## Réservations

### Lister les réservations

```http
GET /api/reservations
```

Réponse `200` : tableau de réservations.

### Créer une réservation

```http
POST /api/reservations
```

```json
{
  "livre_id": "uuid-du-livre",
  "lecteur_id": "uuid-du-lecteur"
}
```

Réponse `201` :

```json
{
  "id": "uuid",
  "livre_id": "uuid",
  "lecteur_id": "uuid",
  "statut": "RESERVEE",
  "date_reservation": "2026-11-01T10:00:00+00:00",
  "date_emprunt": null,
  "date_retour": null
}
```

Statuts possibles : `RESERVEE`, `EMPRUNTEE`, `RETOURNEE`, `ANNULEE`, `EXPIREE`.

### Annuler une réservation

```http
POST /api/reservations/{reservation_id}/annuler
```

Réponse : `200` sans contenu.

### Enregistrer un emprunt

```http
POST /api/reservations/{reservation_id}/emprunter
```

Réponse : `200` sans contenu. Transition : `RESERVEE` → `EMPRUNTEE`.

### Enregistrer un retour

```http
POST /api/reservations/{reservation_id}/retourner
```

Réponse attendue : `200` sans contenu. Transition métier : `EMPRUNTEE` → `RETOURNEE`.

> Point à corriger côté backend : la route `/retourner` est actuellement reliée à la vue d'emprunt. Le frontend ne doit pas considérer cette route comme fiable tant que le backend n'a pas corrigé ce branchement.

## Erreurs

Erreur métier :

```json
{
  "detail": "Message explicite"
}
```

| Code | Signification |
|---|---|
| `201` | Ressource créée |
| `200` | Opération réussie |
| `204` | Suppression réussie, aucun contenu |
| `400` | Autre erreur métier |
| `401` | Authentification absente ou invalide |
| `404` | Ressource introuvable |
| `409` | Conflit métier : livre déjà réservé, quota dépassé, suppression bloquée |
| `422` | Données invalides ou transition de réservation impossible |

Les erreurs de validation de forme de Django REST Framework peuvent utiliser un format par champ :

```json
{
  "email": [
    "Saisissez une adresse e-mail valide."
  ]
}
```

## Documentation interactive

- Schéma OpenAPI : `/api/schema/`
- Swagger UI : `/api/docs/`
