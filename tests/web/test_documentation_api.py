"""Tests de la documentation de l'API : le schéma OpenAPI doit être servi."""

def test_le_schema_openapi_est_servi_avec_le_titre_de_l_api(client):
    """Vérifie que l'adresse du schéma répond et décrit bien l'API Biblio."""
    reponse = client.get("/api/schema/")

    contenu = reponse.content.decode()
    assert reponse.status_code == 200
    assert "openapi" in contenu
    assert "API Biblio" in contenu


def test_le_schema_documente_les_actions_de_reservation():
    from django.test import Client

    schema = Client().get("/api/schema/", HTTP_ACCEPT="application/json").json()

    assert "/api/reservations/{reservation_id}/annuler" in schema["paths"]
    assert "/api/reservations/{reservation_id}/emprunter" in schema["paths"]