"""Tests de l'horloge de la couche application."""

from datetime import datetime, timedelta

from src.application.horloge import HorlogeFictive


def test_horloge_fictive_avance_l_heure_controlee() -> None:
    maintenant_initial = datetime(2026, 10, 31, 10, 0, 0)
    horloge = HorlogeFictive(maintenant_initial)

    horloge.avancer(timedelta(hours=48))

    assert horloge.maintenant() == datetime(2026, 11, 2, 10, 0, 0)