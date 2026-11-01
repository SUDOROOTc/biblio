"""Tests web pour les livres."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_creer_un_livre_retourne_201():
    User.objects.create_user(username="bibliothecaire", password="test")
    client = APIClient()
    client.login(username="bibliothecaire", password="test")
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


@pytest.mark.django_db
def test_rechercher_avec_filtre_annee_retourne_reponse_paginee():
    User.objects.create_user(username="bibliothecaire", password="test")
    client = APIClient()
    client.login(username="bibliothecaire", password="test")

    client.post(
        "/api/livres",
        {"titre": "Dune", "auteur": "Frank Herbert", "annee_publication": 1965},
        format="json",
    )
    client.post(
        "/api/livres",
        {"titre": "Fondation", "auteur": "Isaac Asimov", "annee_publication": 1951},
        format="json",
    )
    client.post(
        "/api/livres",
        {"titre": "Le Seigneur des Anneaux", "auteur": "J.R.R. Tolkien", "annee_publication": 1954},
        format="json",
    )

    response = client.get(
        "/api/livres/recherche?q=dune&annee_publication=1965&page=1",
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "next" in data
    assert "previous" in data
    assert "results" in data
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["titre"] == "Dune"


@pytest.mark.django_db
def test_lister_les_lecteurs_retourne_tous_les_lecteurs():
    User.objects.create_user(username="bibliothecaire", password="bibliothecaire")
    client = APIClient()
    client.login(username="bibliothecaire", password="bibliothecaire")

    client.post(
        "/api/lecteurs",
        {"nom": "Ada Lovelace", "email": "ada@example.com"},
        format="json",
    )
    client.post(
        "/api/lecteurs",
        {"nom": "Grace Hopper", "email": "grace@example.com"},
        format="json",
    )

    response = client.get("/api/lecteurs", format="json")

    assert response.status_code == 200
    assert [lecteur["nom"] for lecteur in response.json()] == [
        "Ada Lovelace",
        "Grace Hopper",
    ]
