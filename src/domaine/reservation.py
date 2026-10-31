"""Entité Reservation du domaine Biblio.

Couche domaine. Porte les données et les règles métier d'une réservation :
cycle de vie, disponibilité active, expiration à 48 h.

Les réservations référencent le livre et le lecteur par identifiant
(livre_id, lecteur_id), pas par objet. Les règles qui dépassent l'entité
(quota de 3, unicité d'une réservation active par livre) sont gérées par le
service, pas par cette entité.
"""

import uuid
from datetime import datetime

from src.domaine.erreurs import ErreurTransitionInvalide
from src.domaine.statut_reservation import StatutReservation


class Reservation:
    """Représente une réservation de livre.

    Attributs:
        id: Identifiant unique de la réservation.
        livre_id: Identifiant du livre réservé.
        lecteur_id: Identifiant du lecteur qui a réservé.
        statut: Statut courant de la réservation.
        date_reservation: Date de création de la réservation.
        date_emprunt: Date de l'emprunt, None tant qu'il n'a pas eu lieu.
        date_retour: Date du retour, None tant que la réservation n'a pas été retournée.
    """

    def __init__(
        self,
        id: uuid.UUID,
        livre_id: uuid.UUID,
        lecteur_id: uuid.UUID,
        statut: StatutReservation,
        date_reservation: datetime,
        date_emprunt: datetime | None = None,
        date_retour: datetime | None = None,
    ) -> None:
        self.id = id
        self.livre_id = livre_id
        self.lecteur_id = lecteur_id
        self.statut = statut
        self.date_reservation = date_reservation
        self.date_emprunt = date_emprunt
        self.date_retour = date_retour

    def est_active(self) -> bool:
        """Indique si la réservation est active.

        Une réservation est active quand son statut est RESERVEE ou EMPRUNTEE.

        Returns:
            True si la réservation est en cours, False sinon.
        """
        return self.statut in (StatutReservation.RESERVEE, StatutReservation.EMPRUNTEE)

    def emprunter(self, maintenant: datetime) -> None:
        """Passe la réservation de RESERVEE à EMPRUNTEE.

        Args:
            maintenant: Heure courante fournie par le service via Horloge.

        Raises:
            ErreurTransitionInvalide: Si la réservation n'est pas en statut RESERVEE.
        """
        if self.statut is not StatutReservation.RESERVEE:
            raise ErreurTransitionInvalide(
                "Impossible d'emprunter : la réservation n'est pas en cours."
            )
        self.statut = StatutReservation.EMPRUNTEE
        self.date_emprunt = maintenant

    def retourner(self, maintenant: datetime) -> None:
        """Passe la réservation de EMPRUNTEE à RETOURNEE.

        Args:
            maintenant: Heure courante fournie par le service via Horloge.

        Raises:
            ErreurTransitionInvalide: Si la réservation n'est pas en statut EMPRUNTEE.
        """
        if self.statut is not StatutReservation.EMPRUNTEE:
            raise ErreurTransitionInvalide(
                "Impossible de retourner : la réservation n'est pas empruntée."
            )
        self.statut = StatutReservation.RETOURNEE
        self.date_retour = maintenant

    def annuler(self) -> None:
        """Passe la réservation de RESERVEE à ANNULEE.

        Raises:
            ErreurTransitionInvalide: Si la réservation n'est pas en statut RESERVEE.
        """
        if self.statut is not StatutReservation.RESERVEE:
            raise ErreurTransitionInvalide(
                "Impossible d'annuler : la réservation n'est pas en cours."
            )
        self.statut = StatutReservation.ANNULEE

    def expirer(self) -> None:
        """Passe la réservation de RESERVEE à EXPIREE.

        Raises:
            ErreurTransitionInvalide: Si la réservation n'est pas en statut RESERVEE.
        """
        if self.statut is not StatutReservation.RESERVEE:
            raise ErreurTransitionInvalide(
                "Impossible d'expirer : la réservation n'est pas en cours."
            )
        self.statut = StatutReservation.EXPIREE
