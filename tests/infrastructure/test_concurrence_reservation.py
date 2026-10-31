"""Tests de concurrence pour la réservation.

Vérifie que la contrainte d'unicité partielle en base empêche la double
réservation simultanée d'un même livre.
"""

import threading
from datetime import datetime

import pytest
from django.db import connections

from src.application.horloge import HorlogeFictive
from src.application.service_reservation import ServiceReservation
from src.domaine.erreurs import ErreurConflit
from src.infrastructure.depots_django import (
    DepotLecteurDjango,
    DepotLivreDjango,
    DepotReservationDjango,
)
from src.infrastructure.models import LecteurModel, LivreModel


@pytest.mark.django_db(transaction=True)
def test_deux_demandes_simultanees_sur_le_meme_livre_ne_creent_qu_une_reservation():
    livre = LivreModel.objects.create(
        titre="Dune", auteur="Frank Herbert", annee_publication=1965
    )
    lecteur1 = LecteurModel.objects.create(
        nom="Ada Lovelace", email="ada.lovelace@example.com"
    )
    lecteur2 = LecteurModel.objects.create(
        nom="Grace Hopper", email="grace.hopper@example.com"
    )

    erreurs = []
    succes = []

    def tenter_reserver(lecteur_model):
        # Chaque thread doit avoir sa propre connexion pour être vraiment concurrent
        for conn in connections.all():
            conn.close()
        depot_livre = DepotLivreDjango()
        depot_lecteur = DepotLecteurDjango()
        depot_reservation = DepotReservationDjango()
        service = ServiceReservation(
            depot_reservation, depot_livre, depot_lecteur, HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0))
        )
        try:
            reservation = service.reserver(livre.id, lecteur_model.id)
            succes.append(reservation)
        except ErreurConflit as exc:
            erreurs.append(exc)

    thread1 = threading.Thread(target=tenter_reserver, args=(lecteur1,))
    thread2 = threading.Thread(target=tenter_reserver, args=(lecteur2,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    assert len(succes) == 1
    assert len(erreurs) == 1
    assert isinstance(erreurs[0], ErreurConflit)
