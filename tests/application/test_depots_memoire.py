"""Tests des dépôts en mémoire pour les services.

Couche application. Sans Django : seuls des faux dépôts en mémoire simples.
"""

import uuid
from datetime import datetime

from src.application.depots import DepotReservation
from src.application.depots_memoire import (
    DepotLecteurMemoire,
    DepotLivreMemoire,
    DepotReservationMemoire,
)
from src.domaine.lecteur import Lecteur
from src.domaine.livre import Livre
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation


def test_depot_reservation_s_interface_doit_exister() -> None:
    assert isinstance(DepotReservation, type)


def test_depot_reservation_memoire_cree_et_trouve_reservation() -> None:
    depot = DepotReservationMemoire()
    date_reservation = datetime(2026, 10, 31, 10, 0, 0)
    reservation = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.RESERVEE,
        date_reservation=date_reservation,
    )
    depot.enregistrer(reservation)

    trouve = depot.trouver_par_id(reservation.id)

    assert trouve is not None
    assert trouve.id == reservation.id


def test_depot_reservation_memoire_trouve_les_reservations_a_expirer() -> None:
    depot = DepotReservationMemoire()
    reservation_expiree = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.RESERVEE,
        date_reservation=datetime(2026, 10, 29, 10, 0, 0),
    )
    reservation_recente = Reservation(
        id=uuid.uuid4(),
        livre_id=uuid.uuid4(),
        lecteur_id=uuid.uuid4(),
        statut=StatutReservation.RESERVEE,
        date_reservation=datetime(2026, 10, 30, 11, 0, 0),
    )
    depot.enregistrer(reservation_expiree)
    depot.enregistrer(reservation_recente)

    reservations = depot.trouver_a_expirer(datetime(2026, 10, 30, 10, 0, 0))

    assert reservations == [reservation_expiree]


def test_depot_livre_memoire_enregistre_et_trouve_un_livre() -> None:
    depot = DepotLivreMemoire()
    livre = Livre(
        id=uuid.uuid4(),
        titre="Dune",
        auteur="Frank Herbert",
        annee_publication=1965,
    )
    depot.enregistrer(livre)

    trouve = depot.trouver_par_id(livre.id)

    assert trouve == livre


def test_depot_lecteur_memoire_enregistre_et_trouve_un_lecteur() -> None:
    depot = DepotLecteurMemoire()
    lecteur = Lecteur(
        id=uuid.uuid4(),
        nom="Ada Lovelace",
        email="ada.lovelace@example.com",
    )
    depot.enregistrer(lecteur)

    trouve = depot.trouver_par_id(lecteur.id)

    assert trouve == lecteur

