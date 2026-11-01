"""Tests de la configuration nécessaire au déploiement web."""

from django.conf import settings


def test_les_fichiers_statiques_sont_configures_pour_la_production():
    assert settings.STATIC_ROOT.name == "staticfiles"
    assert "whitenoise.middleware.WhiteNoiseMiddleware" in settings.MIDDLEWARE
