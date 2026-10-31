"""Erreurs du domaine Biblio.

Couche domaine. Ces exceptions ne connaissent pas HTTP : c'est la couche web
qui les traduit en codes (404, 409, 422…).
"""


class ErreurDomaine(Exception):
    """Classe de base pour toutes les erreurs métier."""


class ErreurValidation(ErreurDomaine):
    """Données invalides (champ vide, format incorrect, année incohérente…)."""


class ErreurConflit(ErreurDomaine):
    """Opération refusée à cause d'un état existant (RG1, RG2, suppression bloquée…)."""


class ErreurIntrouvable(ErreurDomaine):
    """Entité demandée absente du dépôt."""


class ErreurTransitionInvalide(ErreurDomaine):
    """Transition d'état refusée par le cycle de vie de la réservation (RG4)."""
