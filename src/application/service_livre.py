"""Service d'application pour les cas d'usage liés aux livres.

Ce service orchestre les entités Livre et les dépôts. Il ne dépend ni de
Django ni de modèles de base de données.
"""

import uuid

from src.application.depots import DepotLivre, DepotReservation
from src.application.horloge import Horloge
from src.domaine.erreurs import ErreurConflit, ErreurIntrouvable
from src.domaine.livre import Livre


class ServiceLivre:
    """Orchestre les cas d'usage de gestion des livres.

    Le service crée des identifiants UUID et persiste les entités via le
    contrat DepotLivre. Les règles propres au livre restent dans l'entité.
    """

    def __init__(
        self,
        depot_livre: DepotLivre,
        depot_reservation: DepotReservation,
        horloge: Horloge,
    ) -> None:
        """Initialise le service avec ses collaborateurs.

        Args:
            depot_livre: Dépôt utilisé pour enregistrer et retrouver les livres.
            depot_reservation: Dépôt utilisé pour vérifier les réservations actives.
            horloge: Source de l'heure utilisée pour les suppressions logiques.
        """
        self._depot_livre = depot_livre
        self._depot_reservation = depot_reservation
        self._horloge = horloge

    def creer(self, titre: str, auteur: str, annee_publication: int) -> Livre:
        """Crée puis enregistre un livre valide.

        Args:
            titre: Titre non vide du livre.
            auteur: Auteur non vide du livre.
            annee_publication: Année de publication supérieure à zéro.

        Returns:
            Le livre créé avec son UUID.

        Raises:
            ErreurValidation: Si les données ne respectent pas les règles du livre.
        """
        livre = Livre(uuid.uuid4(), titre, auteur, annee_publication)
        self._depot_livre.enregistrer(livre)
        return livre

    def modifier(
        self,
        livre_id: uuid.UUID,
        titre: str,
        auteur: str,
        annee_publication: int,
    ) -> Livre:
        """Modifie puis enregistre un livre existant.

        Args:
            livre_id: Identifiant UUID du livre à modifier.
            titre: Nouveau titre non vide.
            auteur: Nouvel auteur non vide.
            annee_publication: Nouvelle année de publication supérieure à zéro.

        Returns:
            Le livre modifié.

        Raises:
            ErreurIntrouvable: Si aucun livre ne correspond à l'identifiant.
            ErreurValidation: Si les nouvelles données sont invalides.
        """
        livre = self._depot_livre.trouver_par_id(livre_id)
        if livre is None:
            raise ErreurIntrouvable("Livre introuvable.")
        livre.modifier(titre, auteur, annee_publication)
        self._depot_livre.enregistrer(livre)
        return livre

    def rechercher(self, texte: str, annee_publication: int | None = None) -> list[Livre]:
        """Recherche les livres correspondant à un texte.

        Args:
            texte: Texte recherché dans le titre ou le nom de l'auteur.
            annee_publication: Année de publication optionnelle pour filtrer.

        Returns:
            Les livres correspondant au texte.
        """
        return self._depot_livre.rechercher(texte, annee_publication)

    def supprimer(self, livre_id: uuid.UUID) -> None:
        """Supprime logiquement un livre sans réservation active.

        Args:
            livre_id: Identifiant UUID du livre à supprimer.

        Raises:
            ErreurIntrouvable: Si aucun livre ne correspond à l'identifiant.
            ErreurConflit: Si le livre possède une réservation active.
        """
        livre = self._depot_livre.trouver_par_id(livre_id)
        if livre is None:
            raise ErreurIntrouvable("Livre introuvable.")
        if self._depot_reservation.existe_active_pour_livre(livre_id):
            raise ErreurConflit("Impossible de supprimer un livre réservé.")
        livre.supprimer(self._horloge.maintenant())
        self._depot_livre.enregistrer(livre)