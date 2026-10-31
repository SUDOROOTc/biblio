"""Dépôts en mémoire pour les tests des services.

Couche application. Implémentation simple des dépôts en mémoire (dictionnaires)
pour les tests des services. Ces faux dépôts respectent les contrats des
interfaces `DepotLivre`, `DepotReservation` et `DepotLecteur`.

Remarque : en production, les dépôts Django (couche infrastructure) remplacent
ces faux dépôts ; les services n'utilisent que l'interface `DepotReservation`
et ne connaissent pas l'implémentation concrète.
"""

from __future__ import annotations

from src.application.depots import DepotReservation
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation


class DepotReservationMemoire(DepotReservation):
    """Dépôt en mémoire pour les réservations.

    Stocke les réservations dans un dictionnaire (id → réservation).
    Utilisé pour les tests des services sans base de données.
    """

    def __init__(self) -> None:
        self._reservations: dict[int, Reservation] = {}

    def enregistrer(self, reservation: Reservation) -> None:
        """Enregistre une réservation.

        Args:
            reservation: La réservation à enregistrer.
        """
        self._reservations[reservation.id] = reservation

    def trouver_par_id(self, id: int) -> Reservation | None:
        """Retourne la réservation avec cet identifiant, ou None si absente.

        Args:
            id: Identifiant de la réservation.

        Returns:
            La réservation, ou None si elle n'existe pas.
        """
        return self._reservations.get(id)

    def lister(self) -> list[Reservation]:
        """Retourne toutes les réservations enregistrées.

        Returns:
            La liste des réservations.
        """
        return list(self._reservations.values())

    def lister_actives_du_lecteur(self, lecteur_id: int) -> list[Reservation]:
        """Retourne les réservations actives d'un lecteur.

        Args:
            lecteur_id: Identifiant du lecteur.

        Returns:
            La liste des réservations actives de ce lecteur.
        """
        return [
            reservation
            for reservation in self._reservations.values()
            if reservation.est_active() and reservation.lecteur_id == lecteur_id
        ]

    def existe_active_pour_livre(self, livre_id: int) -> bool:
        """Indique si un livre a une réservation active.

        Args:
            livre_id: Identifiant du livre.

        Returns:
            True si une réservation active existe pour ce livre, False sinon.
        """
        return any(
            reservation.est_active() and reservation.livre_id == livre_id
            for reservation in self._reservations.values()
        )

    def trouver_a_expirer(self, limite: int) -> list[Reservation]:
        """Retourne les réservations dont la date de reservation est plus
        ancienne que la limite.

        Args:
            limite: Timestamp de la limite d'expiration.

        Returns:
            La liste des réservations à expirer.
        """
        return [
            reservation
            for reservation in self._reservations.values()
            if reservation.est_active()
            and reservation.date_reservation is not None
            and reservation.date_reservation < limite
        ]
