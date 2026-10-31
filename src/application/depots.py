"""Interfaces de dépôt pour la couche application.

Couche application. Contrats sans code pour les dépôts : ils doivent être
réalisés par l'infrastructure (dépôts Django) ou des faux dépôts en mémoire
pour les tests.

Les services ne connaissent que ces interfaces et échangent des entités
pures du domaine, jamais des modèles Django.
"""

import uuid
from datetime import datetime
from typing import Protocol


class DepotReservation(Protocol):
    """Interface pour le dépôt des réservations.

    Les méthodes suivantes doivent être implémentées par les dépôts Django
    (infrastructure) ou les dépôts en mémoire (tests).
    """

    def enregistrer(self, reservation: "Reservation") -> None:
        """Enregistre une réservation.

        Args:
            reservation: La réservation à enregistrer.
        """

    def trouver_par_id(self, id: uuid.UUID) -> "Reservation | None":
        """Retourne la réservation avec cet identifiant.

        Args:
            id: Identifiant de la réservation.

        Returns:
            La réservation, ou None si elle n'existe pas.
        """

    def lister(self) -> list["Reservation"]:
        """Retourne toutes les réservations enregistrées.

        Returns:
            La liste des réservations.
        """

    def lister_actives_du_lecteur(
        self, lecteur_id: uuid.UUID
    ) -> list["Reservation"]:
        """Retourne les réservations actives d'un lecteur.

        Args:
            lecteur_id: Identifiant du lecteur.

        Returns:
            La liste des réservations actives de ce lecteur.
        """

    def existe_active_pour_livre(self, livre_id: uuid.UUID) -> bool:
        """Indique si un livre a une réservation active.

        Args:
            livre_id: Identifiant du livre.

        Returns:
            True si une réservation active existe pour ce livre, False sinon.
        """

    def trouver_a_expirer(self, limite: datetime) -> list["Reservation"]:
        """Retourne les réservations qui doivent expirer avant la limite.

        Args:
            limite: Date et heure à partir de laquelle la réservation expire.

        Returns:
            La liste des réservations à expirer.
        """


class DepotLivre(Protocol):
    """Interface pour le dépôt des livres."""

    def enregistrer(self, livre: "Livre") -> None:
        """Enregistre un livre."""

    def trouver_par_id(self, id: uuid.UUID) -> "Livre | None":
        """Retourne le livre avec cet identifiant."""

    def rechercher(self, texte: str) -> list["Livre"]:
        """Retourne les livres correspondant au texte de recherche."""


class DepotLecteur(Protocol):
    """Interface pour le dépôt des lecteurs."""

    def enregistrer(self, lecteur: "Lecteur") -> None:
        """Enregistre un lecteur."""

    def trouver_par_id(self, id: uuid.UUID) -> "Lecteur | None":
        """Retourne le lecteur avec cet identifiant."""

    def lister(self) -> list["Lecteur"]:
        """Retourne tous les lecteurs enregistrés."""
