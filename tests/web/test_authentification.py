"""Tests des endpoints JSON d'authentification."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_obtenir_csrf_retourne_un_json_et_initialise_le_cookie():
    client = APIClient()

    reponse = client.get("/api/auth/csrf")

    assert reponse.status_code == 200
    assert reponse.json() == {"detail": "Cookie CSRF initialise."}
    assert "csrftoken" in reponse.cookies


@pytest.mark.django_db
def test_login_valide_retourne_l_utilisateur_et_cree_une_session():
    User.objects.create_user(
        username="bibliothecaire",
        password="bibliothecaire",
        email="bibliothecaire@biblio.local",
        is_staff=True,
    )
    client = APIClient(enforce_csrf_checks=True)
    csrf = client.get("/api/auth/csrf").cookies["csrftoken"].value

    reponse = client.post(
        "/api/auth/login",
        {"username": "bibliothecaire", "password": "bibliothecaire"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf,
    )

    assert reponse.status_code == 200
    assert reponse.json() == {
        "utilisateur": {
            "username": "bibliothecaire",
            "email": "bibliothecaire@biblio.local",
            "role": "bibliothecaire",
        }
    }
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_me_retourne_l_utilisateur_connecte():
    User.objects.create_user(
        username="bibliothecaire",
        password="bibliothecaire",
        email="bibliothecaire@biblio.local",
        is_staff=True,
    )
    client = APIClient()
    client.login(username="bibliothecaire", password="bibliothecaire")

    reponse = client.get("/api/auth/me")

    assert reponse.status_code == 200
    assert reponse.json()["utilisateur"]["username"] == "bibliothecaire"


@pytest.mark.django_db
def test_logout_deconnecte_l_utilisateur():
    User.objects.create_user(username="bibliothecaire", password="bibliothecaire")
    client = APIClient()
    client.login(username="bibliothecaire", password="bibliothecaire")

    reponse = client.post("/api/auth/logout")

    assert reponse.status_code == 204
    assert client.get("/api/auth/me").status_code == 401
