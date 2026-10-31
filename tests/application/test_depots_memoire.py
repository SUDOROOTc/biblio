"""Tests des dépôts en mémoire pour les services.

Couche application. Sans Django : seuls des faux dépôts en mémoire simples.
"""

from src.application.depots import DepotReservation
from src.application.depots_memoire import DepotReservationMemoire
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation


def test_depot_reservation_s_interface_doit_exister() -> None:
    assert isinstance(DepotReservation, type)


def test_depot_reservation_memoire_cree_et_trouve_reservation() -> None:
    depot = DepotReservationMemoire()
    reservation = Reservation(
        id=1,
        livre_id=1,
        lecteur_id=1,
        statut=StatutReservation.RESERVEE,
        date_reservation=None,
    )
    depot.enregistrer(reservation)

    trouve = depot.trouver_par_id(1)

    assert trouve is not None
    assert trouve.id == 1

