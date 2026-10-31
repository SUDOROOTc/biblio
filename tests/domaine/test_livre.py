"""Tests de l'entité Livre."""
import uuid
import pytest
from datetime import datetime
from src.domaine.livre import Livre
from src.domaine.erreurs import ErreurValidation


def un_livre() -> Livre:
    return Livre(
        id=uuid.uuid4(),
        titre="Les Misérables",
        auteur="Victor Hugo",
        annee_publication=1862,
    )


def test_creation_livre_valide():
    livre = un_livre()

    assert livre.titre == "Les Misérables"
    assert livre.auteur == "Victor Hugo"
    assert livre.annee_publication == 1862
    assert livre.date_suppression is None


def test_modifier_met_a_jour_les_champs():
    livre = un_livre()
    livre.modifier(titre="Germinal", auteur="Émile Zola", annee_publication=1885)

    assert livre.titre == "Germinal"
    assert livre.auteur == "Émile Zola"
    assert livre.annee_publication == 1885


def test_supprimer_positionne_date_suppression():
    livre = un_livre()
    maintenant = datetime(2024, 1, 1, 12, 0, 0)
    livre.supprimer(maintenant)

    assert livre.date_suppression == maintenant


def test_est_supprime_vrai_apres_suppression():
    livre = un_livre()
    livre.supprimer(datetime(2024, 1, 1, 12, 0, 0))

    assert livre.est_supprime() is True


def test_est_supprime_faux_si_pas_supprime():
    assert un_livre().est_supprime() is False


def test_creation_avec_titre_vide_leve_erreur_validation():
    with pytest.raises(ErreurValidation):
        Livre(id=uuid.uuid4(), titre="", auteur="Victor Hugo", annee_publication=1862)


def test_creation_avec_auteur_vide_leve_erreur_validation():
    with pytest.raises(ErreurValidation):
        Livre(id=uuid.uuid4(), titre="Les Misérables", auteur="", annee_publication=1862)


def test_creation_avec_annee_invalide_leve_erreur_validation():
    with pytest.raises(ErreurValidation):
        Livre(id=uuid.uuid4(), titre="Les Misérables", auteur="Victor Hugo", annee_publication=0)
