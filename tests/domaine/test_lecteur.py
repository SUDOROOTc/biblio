"""Tests de l'entité Lecteur."""
import uuid
import pytest
from datetime import datetime
from src.domaine.lecteur import Lecteur
from src.domaine.erreurs import ErreurValidation


def un_lecteur() -> Lecteur:
    return Lecteur(
        id=uuid.uuid4(),
        nom="Dupont",
        email="dupont@example.com",
    )


def test_creation_lecteur_valide():
    lecteur = un_lecteur()

    assert lecteur.nom == "Dupont"
    assert lecteur.email == "dupont@example.com"
    assert lecteur.date_suppression is None


def test_modifier_met_a_jour_les_champs():
    lecteur = un_lecteur()
    lecteur.modifier(nom="Martin", email="martin@example.com")

    assert lecteur.nom == "Martin"
    assert lecteur.email == "martin@example.com"


def test_supprimer_positionne_date_suppression():
    lecteur = un_lecteur()
    maintenant = datetime(2024, 1, 1, 12, 0, 0)
    lecteur.supprimer(maintenant)

    assert lecteur.date_suppression == maintenant


def test_est_supprime_vrai_apres_suppression():
    lecteur = un_lecteur()
    lecteur.supprimer(datetime(2024, 1, 1, 12, 0, 0))

    assert lecteur.est_supprime() is True


def test_est_supprime_faux_si_pas_supprime():
    assert un_lecteur().est_supprime() is False


def test_creation_avec_nom_vide_leve_erreur_validation():
    with pytest.raises(ErreurValidation):
        Lecteur(id=uuid.uuid4(), nom="", email="dupont@example.com")


def test_creation_avec_email_vide_leve_erreur_validation():
    with pytest.raises(ErreurValidation):
        Lecteur(id=uuid.uuid4(), nom="Dupont", email="")


def test_creation_avec_email_invalide_leve_erreur_validation():
    with pytest.raises(ErreurValidation):
        Lecteur(id=uuid.uuid4(), nom="Dupont", email="pas-un-email")
