"""Sérialiseurs pour valider uniquement la forme des requêtes."""

from django.contrib.auth.password_validation import validate_password
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


class ChangerMotDePasseSerializer(serializers.Serializer):
    """Sérialiseur pour changer le mot de passe du bibliothécaire connecté."""

    ancien_mot_de_passe = serializers.CharField(write_only=True)
    nouveau_mot_de_passe = serializers.CharField(write_only=True)

    def validate_ancien_mot_de_passe(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return value

    def validate_nouveau_mot_de_passe(self, value):
        user = self.context["request"].user
        validate_password(value, user)
        return value
