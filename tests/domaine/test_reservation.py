"""Tests de l'entité Reservation.

Couche domaine. Sans base de données, sans Django : uniquement des objets pures
et une horloge contrôlée par le test.
"""

import uuid
from datetime import datetime

import pytest
from src.domaine.erreurs import ErreurTransitionInvalide
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation


def un_livre_id() -> uuid.UUID:
    return uuid.uuid4()


def un_lecteur_id() -> uuid.UUID:
    return uuid.uuid4()


def test_reservation_reservee_est_active():
    now = datetime(2026, 1, 1, 10, 0, 0)
    reservation = Reservation(
        id=uuid.uuid4(),
        livre_id=un_livre_id(),
        lecteur_id=un_lecteur_id(),
        statut=StatutReservation.RESERVEE,
        date_reservation=now,
    )

    assert reservation.est_active() is True


def test_reservation_initialise_aux_emprunts_retours_nuls():
    now = datetime(2026, 1, 1, 10, 0, 0)
    reservation = Reservation(
        id=uuid.uuid4(),
        livre_id=un_livre_id(),
        lecteur_id=un_lecteur_id(),
        statut=StatutReservation.RESERVEE,
        date_reservation=now,
    )

    assert reservation.date_emprunt is None
    assert reservation.date_retour is None


def test_emprunter_sur_reservation_non_reservee_legere():
    now = datetime(2026, 1, 1, 10, 0, 0)
    reservation = Reservation(
        id=uuid.uuid4(),
        livre_id=un_livre_id(),
        lecteur_id=un_lecteur_id(),
        statut=StatutReservation.ANNULEE,
        date_reservation=now,
    )

    with pytest.raises(ErreurTransitionInvalide):
        reservation.emprunter(now)

