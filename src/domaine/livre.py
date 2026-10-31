"""Entité Livre du domaine Biblio.

Couche domaine. Porte les données et les règles propres à un livre :
validation à la création, modification, suppression logique.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domaine.erreurs import ErreurValidation


@dataclass
class Livre:
    """Représente un livre de la bibliothèque.

    Un livre n'a pas de champ « disponible » : la disponibilité se déduit
    des réservations actives (RG3).

    Attributes:
        id: Identifiant unique universel.
        titre: Titre du livre, non vide.
        auteur: Nom de l'auteur, non vide.
        annee_publication: Année de publication, entre 1 et l'année courante.
        date_suppression: None si le livre est actif, sinon date de suppression logique.
    """

    id: uuid.UUID
    titre: str
    auteur: str
    annee_publication: int
    date_suppression: datetime | None = field(default=None)

    def __post_init__(self) -> None:
        """Valide les données à la création.

        Raises:
            ErreurValidation: Si le titre ou l'auteur est vide, ou si l'année est invalide.
        """
        if not self.titre or not self.titre.strip():
            raise ErreurValidation("Le titre ne peut pas être vide.")
        if not self.auteur or not self.auteur.strip():
            raise ErreurValidation("L'auteur ne peut pas être vide.")
        if self.annee_publication < 1:
            raise ErreurValidation("L'année de publication doit être supérieure à 0.")

    def modifier(self, titre: str, auteur: str, annee_publication: int) -> None:
        """Met à jour les champs du livre après validation.

        Args:
            titre: Nouveau titre, non vide.
            auteur: Nouvel auteur, non vide.
            annee_publication: Nouvelle année, supérieure à 0.

        Raises:
            ErreurValidation: Si les nouvelles valeurs sont invalides.
        """
        self.titre = titre
        self.auteur = auteur
        self.annee_publication = annee_publication
        self.__post_init__()

    def supprimer(self, maintenant: datetime) -> None:
        """Effectue la suppression logique du livre.

        Args:
            maintenant: Heure courante fournie par le service via Horloge.
        """
        self.date_suppression = maintenant

    def est_supprime(self) -> bool:
        """Indique si le livre a été supprimé logiquement.

        Returns:
            True si date_suppression est renseignée, False sinon.
        """
        return self.date_suppression is not None
