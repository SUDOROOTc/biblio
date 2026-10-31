"""Tests du service de gestion des réservations."""

import uuid
from datetime import datetime, timedelta

import pytest
from src.application.depots_memoire import (
    DepotLecteurMemoire,
    DepotLivreMemoire,
    DepotReservationMemoire,
)
from src.application.horloge import HorlogeFictive
from src.application.service_reservation import ServiceReservation
from src.domaine.erreurs import ErreurConflit, ErreurIntrouvable
from src.domaine.livre import Livre
from src.domaine.lecteur import Lecteur
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation


def un_service_reservation(
    depot_reservation: DepotReservationMemoire,
    depot_livre: DepotLivreMemoire | None = None,
    depot_lecteur: DepotLecteurMemoire | None = None,
) -> ServiceReservation:
    """Construit un service de réservation avec des collaborateurs contrôlés."""
    if depot_livre is None:
        depot_livre = DepotLivreMemoire()
    if depot_lecteur is None:
        depot_lecteur = DepotLecteurMemoire()
    return ServiceReservation(
        depot_reservation,
        depot_livre,
        depot_lecteur,
        HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0)),
    )


def test_lister_retourne_toutes_les_reservations():
    depot_reservation = DepotReservationMemoire()
    service_reservation = un_service_reservation(depot_reservation)
    reservation = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.RESERVEE,
        date_reservation=datetime(2026, 10, 31, 10, 0, 0),
    )
    depot_reservation.enregistrer(reservation)

    reservations = service_reservation.lister()

    assert reservations == [reservation]


def test_reserver_cree_une_reservation_en_statut_reservee():
    depot_livre = DepotLivreMemoire()
    depot_lecteur = DepotLecteurMemoire()
    depot_reservation = DepotReservationMemoire()
    maintenant = datetime(2026, 10, 31, 10, 0, 0)
    service_reservation = ServiceReservation(
        depot_reservation,
        depot_livre,
        depot_lecteur,
        HorlogeFictive(maintenant),
    )
    livre = Livre(uuid.uuid4(), "Dune", "Frank Herbert", 1965)
    lecteur = Lecteur(uuid.uuid4(), "Ada Lovelace", "ada.lovelace@example.com")
    depot_livre.enregistrer(livre)
    depot_lecteur.enregistrer(lecteur)

    reservation = service_reservation.reserver(livre.id, lecteur.id)

    assert reservation.livre_id == livre.id
    assert reservation.lecteur_id == lecteur.id
    assert reservation.statut == StatutReservation.RESERVEE
    assert reservation.date_reservation == maintenant
    assert reservation.date_emprunt is None
    assert reservation.date_retour is None
    assert depot_reservation.trouver_par_id(reservation.id) == reservation


def test_reserver_un_livre_deja_reserve_leve_erreur_conflit():
    depot_livre = DepotLivreMemoire()
    depot_lecteur = DepotLecteurMemoire()
    depot_reservation = DepotReservationMemoire()
    service_reservation = ServiceReservation(
        depot_reservation,
        depot_livre,
        depot_lecteur,
        HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0)),
    )
    livre = Livre(uuid.uuid4(), "Dune", "Frank Herbert", 1965)
    lecteur1 = Lecteur(uuid.uuid4(), "Ada Lovelace", "ada.lovelace@example.com")
    lecteur2 = Lecteur(uuid.uuid4(), "Grace Hopper", "grace.hopper@example.com")
    depot_livre.enregistrer(livre)
    depot_lecteur.enregistrer(lecteur1)
    depot_lecteur.enregistrer(lecteur2)
    depot_reservation.enregistrer(
        Reservation(
            id=uuid.uuid4(),
            livre_id=livre.id,
            lecteur_id=lecteur1.id,
            statut=StatutReservation.RESERVEE,
            date_reservation=datetime(2026, 10, 31, 9, 0, 0),
        )
    )

    with pytest.raises(ErreurConflit):
        service_reservation.reserver(livre.id, lecteur2.id)


def test_reserver_un_lecteur_ayant_deja_trois_reservations_actives_leve_erreur_conflit():
    depot_livre = DepotLivreMemoire()
    depot_lecteur = DepotLecteurMemoire()
    depot_reservation = DepotReservationMemoire()
    service_reservation = ServiceReservation(
        depot_reservation,
        depot_livre,
        depot_lecteur,
        HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0)),
    )
    lecteur = Lecteur(uuid.uuid4(), "Ada Lovelace", "ada.lovelace@example.com")
    depot_lecteur.enregistrer(lecteur)
    for i in range(3):
        livre = Livre(uuid.uuid4(), f"Livre{i}", "Auteur", 2020)
        depot_livre.enregistrer(livre)
        depot_reservation.enregistrer(
            Reservation(
                id=uuid.uuid4(),
                livre_id=livre.id,
                lecteur_id=lecteur.id,
                statut=StatutReservation.RESERVEE,
                date_reservation=datetime(2026, 10, 31, 9, i),
            )
        )
    livre_quatrieme = Livre(uuid.uuid4(), "Quatrieme", "Auteur", 2021)
    depot_livre.enregistrer(livre_quatrieme)

    with pytest.raises(ErreurConflit):
        service_reservation.reserver(livre_quatrieme.id, lecteur.id)


def test_annuler_passe_la_reservation_en_annulee():
    depot_reservation = DepotReservationMemoire()
    service_reservation = un_service_reservation(depot_reservation)
    reservation = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.RESERVEE,
        date_reservation=datetime(2026, 10, 31, 9, 0, 0),
    )
    depot_reservation.enregistrer(reservation)

    service_reservation.annuler(reservation.id)

    assert reservation.statut == StatutReservation.ANNULEE
    assert depot_reservation.trouver_par_id(reservation.id).statut == StatutReservation.ANNULEE


def test_annuler_une_reservation_inexistante_leve_erreur_introuvable():
    depot_reservation = DepotReservationMemoire()
    service_reservation = un_service_reservation(depot_reservation)

    with pytest.raises(ErreurIntrouvable):
        service_reservation.annuler(uuid.uuid4())


def test_enregistrer_emprunt_passe_la_reservation_en_empruntee():
    depot_reservation = DepotReservationMemoire()
    maintenant = datetime(2026, 10, 31, 10, 0, 0)
    service_reservation = ServiceReservation(
        depot_reservation,
        DepotLivreMemoire(),
        DepotLecteurMemoire(),
        HorlogeFictive(maintenant),
    )
    reservation = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.RESERVEE,
        date_reservation=datetime(2026, 10, 31, 9, 0, 0),
    )
    depot_reservation.enregistrer(reservation)

    service_reservation.enregistrer_emprunt(reservation.id)

    assert reservation.statut == StatutReservation.EMPRUNTEE
    assert reservation.date_emprunt == maintenant


def test_enregistrer_retour_passe_la_reservation_en_retournee():
    depot_reservation = DepotReservationMemoire()
    maintenant = datetime(2026, 10, 31, 12, 0, 0)
    service_reservation = ServiceReservation(
        depot_reservation,
        DepotLivreMemoire(),
        DepotLecteurMemoire(),
        HorlogeFictive(maintenant),
    )
    reservation = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.EMPRUNTEE,
        date_reservation=datetime(2026, 10, 31, 9, 0, 0),
        date_emprunt=datetime(2026, 10, 31, 10, 0, 0),
    )
    depot_reservation.enregistrer(reservation)

    service_reservation.enregistrer_retour(reservation.id)

    assert reservation.statut == StatutReservation.RETOURNEE
    assert reservation.date_retour == maintenant


def test_expirer_reservations_passe_en_expiree_celles_depassees():
    depot_reservation = DepotReservationMemoire()
    maintenant = datetime(2026, 10, 31, 10, 0, 0)
    horloge = HorlogeFictive(maintenant)
    service_reservation = ServiceReservation(
        depot_reservation,
        DepotLivreMemoire(),
        DepotLecteurMemoire(),
        horloge,
    )
    reservation_expiree = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.RESERVEE,
        date_reservation=maintenant - timedelta(hours=49),
    )
    reservation_encore_valide = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.RESERVEE,
        date_reservation=maintenant - timedelta(hours=47),
    )
    depot_reservation.enregistrer(reservation_expiree)
    depot_reservation.enregistrer(reservation_encore_valide)

    service_reservation.expirer_reservations()

    assert reservation_expiree.statut == StatutReservation.EXPIREE
    assert reservation_encore_valide.statut == StatutReservation.RESERVEE





