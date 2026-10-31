"""Traduction des erreurs du domaine vers les réponses HTTP."""

from rest_framework import status
from rest_framework.response import Response

from src.domaine.erreurs import (
    ErreurConflit,
    ErreurDomaine,
    ErreurIntrouvable,
    ErreurTransitionInvalide,
    ErreurValidation,
)


def traduire_erreur_domaine(exc: ErreurDomaine) -> Response:
    """Traduit une erreur du domaine en réponse HTTP avec un message exploitable.

    Args:
        exc: Erreur métier levée par le domaine ou le service.

    Returns:
        Réponse DRF avec le code HTTP approprié.
    """
    if isinstance(exc, ErreurIntrouvable):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, ErreurConflit):
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    if isinstance(exc, ErreurValidation):
        return Response(
            {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    if isinstance(exc, ErreurTransitionInvalide):
        return Response(
            {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
