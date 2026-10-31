"""Entité Lecteur du domaine Biblio.

Couche domaine. Porte les données et les règles propres à un lecteur :
validation à la création, modification, suppression logique.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domaine.erreurs import ErreurValidation


@dataclass
class Lecteur:
    """Représente un lecteur de la bibliothèque.

    Le lecteur n'utilise pas le système directement : c'est le bibliothécaire
    qui saisit ses demandes. Le lecteur est une donnée du domaine.

    Attributes:
        id: Identifiant unique universel.
        nom: Nom du lecteur, non vide.
        email: Adresse email valide et unique parmi les lecteurs non supprimés.
        date_suppression: None si actif, sinon date de suppression logique.
    """

    id: uuid.UUID
    nom: str
    email: str
    date_suppression: datetime | None = field(default=None)

    def __post_init__(self) -> None:
        """Valide les données à la création.

        Raises:
            ErreurValidation: Si le nom est vide ou si l'email est invalide.
        """
        if not self.nom or not self.nom.strip():
            raise ErreurValidation("Le nom ne peut pas être vide.")
        if not self.email or not self.email.strip():
            raise ErreurValidation("L'email ne peut pas être vide.")
        if "@" not in self.email or "." not in self.email.split("@")[-1]:
            raise ErreurValidation("L'email est invalide.")

    def modifier(self, nom: str, email: str) -> None:
        """Met à jour les champs du lecteur après validation.

        Args:
            nom: Nouveau nom, non vide.
            email: Nouvel email valide.

        Raises:
            ErreurValidation: Si les nouvelles valeurs sont invalides.
        """
        self.nom = nom
        self.email = email
        self.__post_init__()

    def supprimer(self, maintenant: datetime) -> None:
        """Effectue la suppression logique du lecteur.

        Args:
            maintenant: Heure courante fournie par le service via Horloge.
        """
        self.date_suppression = maintenant

    def est_supprime(self) -> bool:
        """Indique si le lecteur a été supprimé logiquement.

        Returns:
            True si date_suppression est renseignée, False sinon.
        """
        return self.date_suppression is not None
