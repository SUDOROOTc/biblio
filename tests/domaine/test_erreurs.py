"""Tests de la hiérarchie d'erreurs du domaine."""
from src.domaine.erreurs import (
    ErreurDomaine,
    ErreurValidation,
    ErreurConflit,
    ErreurIntrouvable,
    ErreurTransitionInvalide,
)


def test_chaque_erreur_est_une_erreur_domaine():
    assert issubclass(ErreurValidation, ErreurDomaine)
    assert issubclass(ErreurConflit, ErreurDomaine)
    assert issubclass(ErreurIntrouvable, ErreurDomaine)
    assert issubclass(ErreurTransitionInvalide, ErreurDomaine)
