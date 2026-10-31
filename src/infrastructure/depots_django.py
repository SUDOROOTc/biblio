"""Dépôts Django pour la couche infrastructure.

Ces dépôts réalisent les interfaces de la couche application. Ils sont les
seuls à manipuler les modèles Django et à faire la conversion modèle <-> entité.
"""

import uuid
from datetime import datetime

from django.db import IntegrityError, models

from src.application.depots import DepotLecteur, DepotLivre, DepotReservation
from src.domaine.erreurs import ErreurConflit
from src.domaine.lecteur import Lecteur
from src.domaine.livre import Livre
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation
from src.infrastructure.models import LecteurModel, LivreModel, ReservationModel


def _livre_vers_entite(livre_model: LivreModel) -> Livre:
    return Livre(
        id=livre_model.id,
        titre=livre_model.titre,
        auteur=livre_model.auteur,
        annee_publication=livre_model.annee_publication,
        date_suppression=livre_model.date_suppression,
    )


def _lecteur_vers_entite(lecteur_model: LecteurModel) -> Lecteur:
    return Lecteur(
        id=lecteur_model.id,
        nom=lecteur_model.nom,
        email=lecteur_model.email,
        date_suppression=lecteur_model.date_suppression,
    )


def _reservation_vers_entite(reservation_model: ReservationModel) -> Reservation:
    return Reservation(
        id=reservation_model.id,
        livre_id=reservation_model.livre_id,
        lecteur_id=reservation_model.lecteur_id,
        statut=StatutReservation(reservation_model.statut),
        date_reservation=reservation_model.date_reservation,
        date_emprunt=reservation_model.date_emprunt,
        date_retour=reservation_model.date_retour,
    )


class DepotLivreDjango(DepotLivre):
    """Dépôt Django pour les livres."""

    def enregistrer(self, livre: Livre) -> None:
        LivreModel.objects.update_or_create(
            id=livre.id,
            defaults={
                "titre": livre.titre,
                "auteur": livre.auteur,
                "annee_publication": livre.annee_publication,
                "date_suppression": livre.date_suppression,
            },
        )

    def trouver_par_id(self, id: uuid.UUID) -> Livre | None:
        try:
            livre_model = LivreModel.objects.get(id=id)
        except LivreModel.DoesNotExist:
            return None
        return _livre_vers_entite(livre_model)

    def rechercher(self, texte: str) -> list[Livre]:
        texte_normalise = texte.lower()
        livres = LivreModel.objects.filter(
            models.Q(titre__icontains=texte) | models.Q(auteur__icontains=texte)
        )
        # Simple filter to match case-insensitive behavior
        resultats = []
        for livre_model in livres:
            if (
                texte_normalise in livre_model.titre.lower()
                or texte_normalise in livre_model.auteur.lower()
            ):
                resultats.append(_livre_vers_entite(livre_model))
        return resultats


class DepotLecteurDjango(DepotLecteur):
    """Dépôt Django pour les lecteurs."""

    def enregistrer(self, lecteur: Lecteur) -> None:
        LecteurModel.objects.update_or_create(
            id=lecteur.id,
            defaults={
                "nom": lecteur.nom,
                "email": lecteur.email,
                "date_suppression": lecteur.date_suppression,
            },
        )

    def trouver_par_id(self, id: uuid.UUID) -> Lecteur | None:
        try:
            lecteur_model = LecteurModel.objects.get(id=id)
        except LecteurModel.DoesNotExist:
            return None
        return _lecteur_vers_entite(lecteur_model)

    def lister(self) -> list[Lecteur]:
        return [_lecteur_vers_entite(l) for l in LecteurModel.objects.all()]


class DepotReservationDjango(DepotReservation):
    """Dépôt Django pour les réservations."""

    def enregistrer(self, reservation: Reservation) -> None:
        try:
            ReservationModel.objects.update_or_create(
                id=reservation.id,
                defaults={
                    "livre_id": reservation.livre_id,
                    "lecteur_id": reservation.lecteur_id,
                    "statut": reservation.statut.value,
                    "date_reservation": reservation.date_reservation,
                    "date_emprunt": reservation.date_emprunt,
                    "date_retour": reservation.date_retour,
                },
            )
        except IntegrityError as exc:
            message = str(exc).lower()
            if "unique_reservation_active_par_livre" in message or "livre" in message:
                raise ErreurConflit("Livre déjà réservé.") from exc
            raise

    def trouver_par_id(self, id: uuid.UUID) -> Reservation | None:
        try:
            reservation_model = ReservationModel.objects.get(id=id)
        except ReservationModel.DoesNotExist:
            return None
        return _reservation_vers_entite(reservation_model)

    def lister(self) -> list[Reservation]:
        return [_reservation_vers_entite(r) for r in ReservationModel.objects.all()]

    def lister_actives_du_lecteur(self, lecteur_id: uuid.UUID) -> list[Reservation]:
        reservations = ReservationModel.objects.filter(
            lecteur_id=lecteur_id,
            statut__in=[StatutReservation.RESERVEE, StatutReservation.EMPRUNTEE],
        )
        return [_reservation_vers_entite(r) for r in reservations]

    def existe_active_pour_livre(self, livre_id: uuid.UUID) -> bool:
        return ReservationModel.objects.filter(
            livre_id=livre_id,
            statut__in=[StatutReservation.RESERVEE, StatutReservation.EMPRUNTEE],
        ).exists()

    def trouver_a_expirer(self, limite: datetime) -> list[Reservation]:
        reservations = ReservationModel.objects.filter(
            statut=StatutReservation.RESERVEE,
            date_reservation__lt=limite,
        )
        return [_reservation_vers_entite(r) for r in reservations]
