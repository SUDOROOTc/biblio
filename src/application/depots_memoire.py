"""Dépôts en mémoire pour les tests des services.

Couche application. Implémentation simple des dépôts en mémoire (dictionnaires)
pour les tests des services. Ces faux dépôts respectent les contrats des
interfaces `DepotLivre`, `DepotReservation` et `DepotLecteur`.

Remarque : en production, les dépôts Django (couche infrastructure) remplacent
ces faux dépôts ; les services n'utilisent que l'interface `DepotReservation`
et ne connaissent pas l'implémentation concrète.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from src.application.depots import DepotLecteur, DepotLivre, DepotReservation
from src.domaine.lecteur import Lecteur
from src.domaine.livre import Livre
from src.domaine.reservation import Reservation


class DepotLivreMemoire(DepotLivre):
    """Dépôt en mémoire pour les livres.

    Stocke les livres dans un dictionnaire (UUID → livre). Il sert aux tests
    des services sans dépendre d'une base de données.
    """

    def __init__(self) -> None:
        self._livres: dict[uuid.UUID, Livre] = {}

    def enregistrer(self, livre: Livre) -> None:
        """Enregistre un livre ou remplace sa version déjà enregistrée.

        Args:
            livre: Livre à conserver en mémoire.
        """
        self._livres[livre.id] = livre

    def trouver_par_id(self, id: uuid.UUID) -> Livre | None:
        """Retourne le livre correspondant à son identifiant.

        Args:
            id: Identifiant UUID du livre.

        Returns:
            Le livre trouvé, ou None lorsqu'il est absent.
        """
        return self._livres.get(id)

    def rechercher(self, texte: str) -> list[Livre]:
        """Recherche les livres par titre ou auteur, sans tenir compte de la casse.

        Args:
            texte: Texte à rechercher dans le titre ou l'auteur.

        Returns:
            Les livres dont le titre ou l'auteur correspond au texte.
        """
        texte_normalise = texte.casefold()
        return [
            livre
            for livre in self._livres.values()
            if texte_normalise in livre.titre.casefold()
            or texte_normalise in livre.auteur.casefold()
        ]


class DepotLecteurMemoire(DepotLecteur):
    """Dépôt en mémoire pour les lecteurs.

    Stocke les lecteurs dans un dictionnaire (UUID → lecteur). Il sert aux
    tests des services sans dépendre d'une base de données.
    """

    def __init__(self) -> None:
        self._lecteurs: dict[uuid.UUID, Lecteur] = {}

    def enregistrer(self, lecteur: Lecteur) -> None:
        """Enregistre un lecteur ou remplace sa version déjà enregistrée.

        Args:
            lecteur: Lecteur à conserver en mémoire.
        """
        self._lecteurs[lecteur.id] = lecteur

    def trouver_par_id(self, id: uuid.UUID) -> Lecteur | None:
        """Retourne le lecteur correspondant à son identifiant.

        Args:
            id: Identifiant UUID du lecteur.

        Returns:
            Le lecteur trouvé, ou None lorsqu'il est absent.
        """
        return self._lecteurs.get(id)

    def lister(self) -> list[Lecteur]:
        """Retourne tous les lecteurs présents dans le dépôt.

        Returns:
            La liste des lecteurs enregistrés.
        """
        return list(self._lecteurs.values())


class DepotReservationMemoire(DepotReservation):
    """Dépôt en mémoire pour les réservations.

    Stocke les réservations dans un dictionnaire (UUID → réservation).
    Utilisé pour les tests des services sans base de données.
    """

    def __init__(self) -> None:
        self._reservations: dict[uuid.UUID, Reservation] = {}

    def enregistrer(self, reservation: Reservation) -> None:
        """Enregistre une réservation.

        Args:
            reservation: La réservation à enregistrer.
        """
        self._reservations[reservation.id] = reservation

    def trouver_par_id(self, id: uuid.UUID) -> Reservation | None:
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

    def lister_actives_du_lecteur(
        self, lecteur_id: uuid.UUID
    ) -> list[Reservation]:
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

    def existe_active_pour_livre(self, livre_id: uuid.UUID) -> bool:
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

    def trouver_a_expirer(self, limite: datetime) -> list[Reservation]:
        """Retourne les réservations réservées avant la limite d'expiration.

        Args:
            limite: Date et heure à comparer à la date de réservation.

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
