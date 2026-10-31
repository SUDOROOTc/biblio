"""Service d'application pour les cas d'usage liés aux réservations.

Ce service orchestre les entités Reservation et les dépôts. Il ne dépend ni de
Django ni de modèles de base de données.
"""

import uuid

from src.application.depots import DepotLecteur, DepotLivre, DepotReservation
from src.application.horloge import Horloge
from src.domaine.erreurs import ErreurConflit, ErreurIntrouvable
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation


class ServiceReservation:
    """Orchestre les cas d'usage de gestion des réservations.

    Le service crée des identifiants UUID et persiste les entités via le
    contrat DepotReservation. Les règles propres à une entité restent dans
    l'entité, les règles entre objets (RG1, RG2) sont appliquées ici.
    """

    def __init__(
        self,
        depot_reservation: DepotReservation,
        depot_livre: DepotLivre,
        depot_lecteur: DepotLecteur,
        horloge: Horloge,
    ) -> None:
        """Initialise le service avec ses collaborateurs.

        Args:
            depot_reservation: Dépôt utilisé pour enregistrer et retrouver les réservations.
            depot_livre: Dépôt utilisé pour retrouver les livres.
            depot_lecteur: Dépôt utilisé pour retrouver les lecteurs.
            horloge: Source de l'heure utilisée pour date_reservation et l'expiration.
        """
        self._depot_reservation = depot_reservation
        self._depot_livre = depot_livre
        self._depot_lecteur = depot_lecteur
        self._horloge = horloge

    def lister(self) -> list[Reservation]:
        """Retourne toutes les réservations enregistrées.

        Returns:
            La liste de toutes les réservations présentes dans le dépôt.
        """
        return self._depot_reservation.lister()

    def reserver(self, livre_id: uuid.UUID, lecteur_id: uuid.UUID) -> Reservation:
        """Réserve un livre disponible pour un lecteur.

        Applique RG1 (un livre ne peut avoir qu'une réservation active)
        et RG2 (un lecteur ne peut avoir plus de 3 réservations actives).

        Args:
            livre_id: Identifiant du livre à réserver.
            lecteur_id: Identifiant du lecteur qui réserve.

        Returns:
            La réservation créée en statut RESERVEE.

        Raises:
            ErreurIntrouvable: Si le livre ou le lecteur est introuvable.
            ErreurConflit: Si le livre est déjà réservé ou si le quota est dépassé.
        """
        livre = self._depot_livre.trouver_par_id(livre_id)
        if livre is None:
            raise ErreurIntrouvable("Livre introuvable.")
        lecteur = self._depot_lecteur.trouver_par_id(lecteur_id)
        if lecteur is None:
            raise ErreurIntrouvable("Lecteur introuvable.")

        if self._depot_reservation.existe_active_pour_livre(livre_id):
            raise ErreurConflit("Livre déjà réservé.")
        if len(self._depot_reservation.lister_actives_du_lecteur(lecteur_id)) >= 3:
            raise ErreurConflit("Quota de réservations actives atteint.")

        reservation = Reservation(
            id=uuid.uuid4(),
            livre_id=livre_id,
            lecteur_id=lecteur_id,
            statut=StatutReservation.RESERVEE,
            date_reservation=self._horloge.maintenant(),
            date_emprunt=None,
            date_retour=None,
        )
        self._depot_reservation.enregistrer(reservation)
        return reservation

    def annuler(self, reservation_id: uuid.UUID) -> None:
        """Annule une réservation en statut RESERVEE.

        Args:
            reservation_id: Identifiant de la réservation à annuler.

        Raises:
            ErreurIntrouvable: Si la réservation est introuvable.
            ErreurTransitionInvalide: Si la réservation n'est pas annulable.
        """
        reservation = self._depot_reservation.trouver_par_id(reservation_id)
        if reservation is None:
            raise ErreurIntrouvable("Réservation introuvable.")
        reservation.annuler()
        self._depot_reservation.enregistrer(reservation)

    def enregistrer_emprunt(self, reservation_id: uuid.UUID) -> None:
        """Passe une réservation de RESERVEE à EMPRUNTEE.

        Args:
            reservation_id: Identifiant de la réservation.

        Raises:
            ErreurIntrouvable: Si la réservation est introuvable.
            ErreurTransitionInvalide: Si la transition n'est pas autorisée.
        """
        reservation = self._depot_reservation.trouver_par_id(reservation_id)
        if reservation is None:
            raise ErreurIntrouvable("Réservation introuvable.")
        reservation.emprunter(self._horloge.maintenant())
        self._depot_reservation.enregistrer(reservation)

    def enregistrer_retour(self, reservation_id: uuid.UUID) -> None:
        """Passe une réservation de EMPRUNTEE à RETOURNEE.

        Args:
            reservation_id: Identifiant de la réservation.

        Raises:
            ErreurIntrouvable: Si la réservation est introuvable.
            ErreurTransitionInvalide: Si la transition n'est pas autorisée.
        """
        reservation = self._depot_reservation.trouver_par_id(reservation_id)
        if reservation is None:
            raise ErreurIntrouvable("Réservation introuvable.")
        reservation.retourner(self._horloge.maintenant())
        self._depot_reservation.enregistrer(reservation)

    def expirer_reservations(self) -> None:
        """Expire les réservations non retirées depuis plus de 48 heures.

        Utilise l'horloge injectée pour calculer la limite et demande au dépôt
        les réservations à expirer. Chaque réservation est passée en EXPIREE
        par l'entité elle-même.
        """
        limite = self._horloge.maintenant() - __import__("datetime").timedelta(hours=48)
        for reservation in self._depot_reservation.trouver_a_expirer(limite):
            reservation.expirer()
            self._depot_reservation.enregistrer(reservation)



