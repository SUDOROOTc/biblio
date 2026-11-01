"""Vues JSON d'authentification de l'API.

Cette couche expose les opérations de session Django au frontend sans
réintroduire les pages HTML de l'interface d'authentification DRF.
"""

from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.web.serializers import ConnexionSerializer


def _utilisateur_vers_dict(utilisateur):
    return {
        "username": utilisateur.username,
        "email": utilisateur.email,
        "role": "bibliothecaire",
    }


class CsrfView(APIView):
    """Initialise le cookie CSRF nécessaire aux requêtes JSON protégées."""

    permission_classes = [AllowAny]

    @extend_schema(
        description="Initialise le cookie CSRF de la session frontend.",
        responses={200: None},
    )
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """Retourne une confirmation JSON après initialisation du cookie CSRF."""
        return Response({"detail": "Cookie CSRF initialise."})


class ConnexionView(APIView):
    """Authentifie un bibliothécaire et ouvre une session Django."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=ConnexionSerializer,
        description="Authentifie un bibliothécaire avec une session Django.",
        responses={200: None, 401: None, 422: None},
    )
    @method_decorator(csrf_protect)
    def post(self, request):
        """Vérifie les identifiants et retourne le profil connecté."""
        serializer = ConnexionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        utilisateur = authenticate(
            request=request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if utilisateur is None:
            return Response(
                {"detail": "Identifiant ou mot de passe incorrect."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, utilisateur)
        return Response({"utilisateur": _utilisateur_vers_dict(utilisateur)})


class UtilisateurConnecteView(APIView):
    """Retourne l'utilisateur associé à la session Django courante."""

    permission_classes = [AllowAny]

    @extend_schema(
        description="Retourne le profil du bibliothécaire connecté.",
        responses={200: None, 401: None},
    )
    def get(self, request):
        """Retourne le profil connecté ou une erreur JSON d'authentification."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentification requise."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response({"utilisateur": _utilisateur_vers_dict(request.user)})
