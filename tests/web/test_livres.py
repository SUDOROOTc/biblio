"""Tests web pour les livres."""

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_creer_un_livre_retourne_201():
    client = APIClient()
    response = client.post(
        "/api/livres",
        {"titre": "Dune", "auteur": "Frank Herbert", "annee_publication": 1965},
        format="json",
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titre"] == "Dune"
    assert data["auteur"] == "Frank Herbert"
    assert data["annee_publication"] == 1965
    assert "id" in data
