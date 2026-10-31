"""Modèles Django pour la couche infrastructure.

Ces modèles ne contiennent aucune règle métier. Seuls les dépôts Django
les manipulent. La conversion vers/depuis les entités du domaine est assurée
par les dépôts.
"""

import uuid

from django.db import models

from src.domaine.statut_reservation import StatutReservation


class LivreModel(models.Model):
    """Modèle Django pour les livres."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(max_length=255)
    auteur = models.CharField(max_length=255)
    annee_publication = models.IntegerField()
    date_suppression = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "livre"

    def __str__(self) -> str:
        return self.titre


class LecteurModel(models.Model):
    """Modèle Django pour les lecteurs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    date_suppression = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lecteur"
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(date_suppression__isnull=True),
                name="unique_email_lecteur_non_supprime",
            )
        ]

    def __str__(self) -> str:
        return self.nom


class ReservationModel(models.Model):
    """Modèle Django pour les réservations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    livre = models.ForeignKey(
        LivreModel, on_delete=models.CASCADE, related_name="reservations"
    )
    lecteur = models.ForeignKey(
        LecteurModel, on_delete=models.CASCADE, related_name="reservations"
    )
    statut = models.CharField(max_length=20)
    date_reservation = models.DateTimeField()
    date_emprunt = models.DateTimeField(null=True, blank=True)
    date_retour = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "reservation"
        constraints = [
            models.UniqueConstraint(
                fields=["livre"],
                condition=models.Q(
                    statut__in=[StatutReservation.RESERVEE, StatutReservation.EMPRUNTEE]
                ),
                name="unique_reservation_active_par_livre",
            )
        ]

    def __str__(self) -> str:
        return f"{self.livre_id} - {self.lecteur_id} - {self.statut}"
