"""Horloge système pour la production."""

from datetime import datetime

from src.application.horloge import Horloge


class HorlogeSysteme(Horloge):
    """Horloge utilisant l'heure réelle du système."""

    def maintenant(self) -> datetime:
        return datetime.now()
