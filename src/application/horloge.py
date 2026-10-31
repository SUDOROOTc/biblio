"""Horloges utilisées par les services de la couche application.

Les services dépendent de l'interface Horloge pour fournir une heure aux
entités. Cette indirection rend les règles dépendantes du temps testables.
"""

from datetime import datetime, timedelta
from typing import Protocol


class Horloge(Protocol):
    """Contrat fournissant l'heure courante aux services."""

    def maintenant(self) -> datetime:
        """Retourne l'heure courante fournie par l'implémentation.

        Returns:
            L'heure courante.
        """


class HorlogeFictive:
    """Horloge contrôlable utilisée par les tests de la couche application.

    Elle conserve une heure initiale reçue en argument et ne consulte jamais
    l'horloge système. Les tests peuvent la faire avancer sans attendre.
    """

    def __init__(self, maintenant_initial: datetime) -> None:
        """Initialise l'horloge à une heure connue.

        Args:
            maintenant_initial: Heure qui sera retournée au départ.
        """
        self._maintenant = maintenant_initial

    def maintenant(self) -> datetime:
        """Retourne l'heure actuellement contrôlée par le test.

        Returns:
            L'heure courante de cette horloge fictive.
        """
        return self._maintenant

    def avancer(self, duree: timedelta) -> None:
        """Avance l'heure contrôlée d'une durée donnée.

        Args:
            duree: Durée à ajouter à l'heure courante.
        """
        self._maintenant += duree