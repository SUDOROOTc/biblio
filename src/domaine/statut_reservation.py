"""Énumération des statuts possibles d'une réservation.

Couche domaine. Utilisée par Reservation et ReservationModel (via conversion).
"""
from enum import StrEnum


class StatutReservation(StrEnum):
    """Cycle de vie d'une réservation.

    RESERVEE et EMPRUNTEE sont actives. RETOURNEE, ANNULEE et EXPIREE sont terminales.
    """

    RESERVEE = "RESERVEE"
    EMPRUNTEE = "EMPRUNTEE"
    RETOURNEE = "RETOURNEE"
    ANNULEE = "ANNULEE"
    EXPIREE = "EXPIREE"

    def est_actif(self) -> bool:
        """Indique si ce statut correspond à une réservation active.

        Returns:
            True si RESERVEE ou EMPRUNTEE, False sinon.
        """
        return self in (StatutReservation.RESERVEE, StatutReservation.EMPRUNTEE)
