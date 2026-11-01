"""Commande pour injecter des données d'exemple dans la base de données."""

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from src.infrastructure.models import LecteurModel, LivreModel, ReservationModel
from src.domaine.statut_reservation import StatutReservation


class Command(BaseCommand):
    help = "Injecte des données d'exemple (livres, lecteurs, réservations) dans la base."

    def handle(self, *args, **options):
        self.stdout.write("Création des livres...")
        livres = self._creer_livres()
        self.stdout.write(self.style.SUCCESS(f"{len(livres)} livre(s) créé(s)."))

        self.stdout.write("Création des lecteurs...")
        lecteurs = self._creer_lecteurs()
        self.stdout.write(self.style.SUCCESS(f"{len(lecteurs)} lecteur(s) créé(s)."))

        self.stdout.write("Création des réservations...")
        reservations = self._creer_reservations(livres, lecteurs)
        self.stdout.write(self.style.SUCCESS(f"{len(reservations)} réservation(s) créée(s)."))

        self.stdout.write(self.style.SUCCESS("Seed terminé avec succès."))

    def _creer_livres(self):
        livres_data = [
            {"titre": "Dune", "auteur": "Frank Herbert", "annee_publication": 1965},
            {"titre": "Fondation", "auteur": "Isaac Asimov", "annee_publication": 1951},
            {
                "titre": "Le Seigneur des Anneaux",
                "auteur": "J.R.R. Tolkien",
                "annee_publication": 1954,
            },
            {"titre": "1984", "auteur": "George Orwell", "annee_publication": 1949},
            {
                "titre": "Harry Potter à l'école des sorciers",
                "auteur": "J.K. Rowling",
                "annee_publication": 1997,
            },
        ]
        livres = []
        for data in livres_data:
            livre, _ = LivreModel.objects.update_or_create(
                titre=data["titre"],
                defaults={
                    "auteur": data["auteur"],
                    "annee_publication": data["annee_publication"],
                },
            )
            livres.append(livre)
        return livres

    def _creer_lecteurs(self):
        lecteurs_data = [
            {"nom": "Ada Lovelace", "email": "ada.lovelace@biblio.local"},
            {"nom": "Grace Hopper", "email": "grace.hopper@biblio.local"},
            {"nom": "Alan Turing", "email": "alan.turing@biblio.local"},
        ]
        lecteurs = []
        for data in lecteurs_data:
            lecteur, _ = LecteurModel.objects.update_or_create(
                email=data["email"],
                defaults={"nom": data["nom"]},
            )
            lecteurs.append(lecteur)
        return lecteurs

    def _creer_reservations(self, livres, lecteurs):
        now = datetime(2026, 10, 31, 10, 0, 0)

        reservations_data = [
            # RG1 respecté : un livre = une réservation active max
            # RG2 respecté : un lecteur = 3 réservations actives max
            {
                "livre": livres[0],
                "lecteur": lecteurs[0],
                "statut": StatutReservation.RESERVEE,
                "date_reservation": now,
            },
            {
                "livre": livres[1],
                "lecteur": lecteurs[0],
                "statut": StatutReservation.EMPRUNTEE,
                "date_reservation": now,
            },
            {
                "livre": livres[2],
                "lecteur": lecteurs[1],
                "statut": StatutReservation.RESERVEE,
                "date_reservation": now,
            },
            # Réservations terminées
            {
                "livre": livres[3],
                "lecteur": lecteurs[2],
                "statut": StatutReservation.RETOURNEE,
                "date_reservation": now,
                "date_emprunt": now,
                "date_retour": now,
            },
            {
                "livre": livres[4],
                "lecteur": lecteurs[0],
                "statut": StatutReservation.ANNULEE,
                "date_reservation": now,
            },
        ]

        reservations = []
        for data in reservations_data:
            reservation, _ = ReservationModel.objects.update_or_create(
                livre=data["livre"],
                lecteur=data["lecteur"],
                defaults={
                    "statut": data["statut"].value,
                    "date_reservation": data["date_reservation"],
                    "date_emprunt": data.get("date_emprunt"),
                    "date_retour": data.get("date_retour"),
                },
            )
            reservations.append(reservation)
        return reservations
