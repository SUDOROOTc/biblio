"""Routes JSON d'authentification de l'API."""

from django.urls import path

from src.web.auth_views import ConnexionView, CsrfView

urlpatterns = [
    path("csrf", CsrfView.as_view(), name="auth-csrf"),
    path("login", ConnexionView.as_view(), name="auth-login"),
]
