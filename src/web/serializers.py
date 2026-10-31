"""Sérialiseurs pour valider uniquement la forme des requêtes."""

from rest_framework import serializers


class LivreCreationSerializer(serializers.Serializer):
    """Sérialiseur pour la création d'un livre."""

    titre = serializers.CharField()
    auteur = serializers.CharField()
    annee_publication = serializers.IntegerField()


class LivreModificationSerializer(serializers.Serializer):
    """Sérialiseur pour la modification d'un livre."""

    titre = serializers.CharField()
    auteur = serializers.CharField()
    annee_publication = serializers.IntegerField()


class LecteurCreationSerializer(serializers.Serializer):
    """Sérialiseur pour la création d'un lecteur."""

    nom = serializers.CharField()
    email = serializers.EmailField()


class LecteurModificationSerializer(serializers.Serializer):
    """Sérialiseur pour la modification d'un lecteur."""

    nom = serializers.CharField()
    email = serializers.EmailField()


class ReservationCreationSerializer(serializers.Serializer):
    """Sérialiseur pour la création d'une réservation."""

    livre_id = serializers.UUIDField()
    lecteur_id = serializers.UUIDField()


class ReservationActionSerializer(serializers.Serializer):
    """Sérialiseur vide utilisé pour les actions sur une réservation."""

    pass
