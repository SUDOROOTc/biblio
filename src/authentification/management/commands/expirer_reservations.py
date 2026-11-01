"""Commande pour expirer les réservations non retirées depuis plus de 48 heures."""

from src.application.depots import DepotLecteur, DepotLivre, DepotReservation
from src.application.service_reservation import ServiceReservation
from django.core.management.base import BaseCommand
from src.infrastructure.depots_django import (
    DepotLecteurDjango,
    DepotLivreDjango,
    DepotReservationDjango,
)
from src.infrastructure.horloge import HorlogeSysteme


class Command(BaseCommand):
    help = "Expire les réservations non retirées depuis plus de 48 heures."

    def handle(self, *args, **options):
        depot_reservation = DepotReservationDjango()
        depot_livre = DepotLivreDjango()
        depot_lecteur = DepotLecteurDjango()
        horloge = HorlogeSysteme()

        service_reservation = ServiceReservation(
            depot_reservation,
            depot_livre,
            depot_lecteur,
            horloge,
        )

        service_reservation.expirer_reservations()
        self.stdout.write(
            self.style.SUCCESS("Réservations expirées traitées avec succès.")
        )
