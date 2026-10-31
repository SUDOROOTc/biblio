"""Factory pour instancier les services avec les dépôts Django."""

from src.application.service_lecteur import ServiceLecteur
from src.application.service_livre import ServiceLivre
from src.application.service_reservation import ServiceReservation
from src.infrastructure.depots_django import (
    DepotLecteurDjango,
    DepotLivreDjango,
    DepotReservationDjango,
)
from src.infrastructure.horloge import HorlogeSysteme


def get_service_livre() -> ServiceLivre:
    return ServiceLivre(DepotLivreDjango(), DepotReservationDjango(), HorlogeSysteme())


def get_service_lecteur() -> ServiceLecteur:
    return ServiceLecteur(DepotLecteurDjango(), DepotReservationDjango(), HorlogeSysteme())


def get_service_reservation() -> ServiceReservation:
    return ServiceReservation(
        DepotReservationDjango(),
        DepotLivreDjango(),
        DepotLecteurDjango(),
        HorlogeSysteme(),
    )
