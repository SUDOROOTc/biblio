"""Tests du service de gestion des lecteurs."""

import uuid
from datetime import datetime

import pytest
from src.application.depots_memoire import (
    DepotLecteurMemoire,
    DepotReservationMemoire,
)
from src.application.horloge import HorlogeFictive
from src.application.service_lecteur import ServiceLecteur
from src.domaine.erreurs import ErreurConflit
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation


def un_service_lecteur(depot_lecteur: DepotLecteurMemoire) -> ServiceLecteur:
    """Construit un service de lecteur avec un dépôt de réservations vide."""
    return ServiceLecteur(
        depot_lecteur,
        DepotReservationMemoire(),
        HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0)),
    )


def test_creer_enregistre_un_lecteur_avec_un_uuid() -> None:
    depot_lecteur = DepotLecteurMemoire()
    service_lecteur = un_service_lecteur(depot_lecteur)

    lecteur = service_lecteur.creer("Ada Lovelace", "ada.lovelace@example.com")

    assert isinstance(lecteur.id, uuid.UUID)
    assert depot_lecteur.trouver_par_id(lecteur.id) == lecteur


def test_modifier_met_a_jour_un_lecteur_existant() -> None:
    depot_lecteur = DepotLecteurMemoire()
    service_lecteur = un_service_lecteur(depot_lecteur)
    lecteur = service_lecteur.creer("Ada Lovelace", "ada.lovelace@example.com")

    lecteur_modifie = service_lecteur.modifier(
        lecteur.id, "Grace Hopper", "grace.hopper@example.com"
    )

    assert lecteur_modifie.nom == "Grace Hopper"
    assert lecteur_modifie.email == "grace.hopper@example.com"
    assert depot_lecteur.trouver_par_id(lecteur.id) == lecteur_modifie


def test_consulter_retourne_le_lecteur_et_ses_reservations_actives() -> None:
    depot_lecteur = DepotLecteurMemoire()
    depot_reservation = DepotReservationMemoire()
    service_lecteur = ServiceLecteur(
        depot_lecteur,
        depot_reservation,
        HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0)),
    )
    lecteur = service_lecteur.creer("Ada Lovelace", "ada.lovelace@example.com")
    reservation_active = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=lecteur.id,
        statut=StatutReservation.RESERVEE,
        date_reservation=datetime(2026, 10, 31, 10, 0, 0),
    )
    reservation_terminee = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=lecteur.id,
        statut=StatutReservation.ANNULEE,
        date_reservation=datetime(2026, 10, 30, 10, 0, 0),
    )
    depot_reservation.enregistrer(reservation_active)
    depot_reservation.enregistrer(reservation_terminee)

    lecteur_consulte, reservations_actives = service_lecteur.consulter(lecteur.id)

    assert lecteur_consulte == lecteur
    assert reservations_actives == [reservation_active]


def test_supprimer_effectue_une_suppression_logique() -> None:
    depot_lecteur = DepotLecteurMemoire()
    maintenant = datetime(2026, 10, 31, 10, 0, 0)
    service_lecteur = ServiceLecteur(
        depot_lecteur,
        DepotReservationMemoire(),
        HorlogeFictive(maintenant),
    )
    lecteur = service_lecteur.creer("Ada Lovelace", "ada.lovelace@example.com")

    service_lecteur.supprimer(lecteur.id)

    assert lecteur.date_suppression == maintenant
    assert depot_lecteur.trouver_par_id(lecteur.id) == lecteur


def test_supprimer_un_lecteur_avec_reservation_active_leve_erreur_conflit() -> None:
    depot_lecteur = DepotLecteurMemoire()
    depot_reservation = DepotReservationMemoire()
    service_lecteur = ServiceLecteur(
        depot_lecteur,
        depot_reservation,
        HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0)),
    )
    lecteur = service_lecteur.creer("Ada Lovelace", "ada.lovelace@example.com")
    depot_reservation.enregistrer(
        Reservation(
            id=uuid.uuid4(),
            livre_id=uuid.uuid4(),
            lecteur_id=lecteur.id,
            statut=StatutReservation.EMPRUNTEE,
            date_reservation=datetime(2026, 10, 31, 9, 0, 0),
        )
    )

    with pytest.raises(ErreurConflit):
        service_lecteur.supprimer(lecteur.id)

    assert lecteur.date_suppression is None