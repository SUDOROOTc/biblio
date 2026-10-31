"""Service d'application pour les cas d'usage liés aux lecteurs.

Ce service orchestre les entités Lecteur et les dépôts. Il ne dépend ni de
Django ni de modèles de base de données.
"""

import uuid

from src.application.depots import DepotLecteur, DepotReservation
from src.application.horloge import Horloge
from src.domaine.erreurs import ErreurConflit, ErreurIntrouvable
from src.domaine.lecteur import Lecteur
from src.domaine.reservation import Reservation


class ServiceLecteur:
    """Orchestre les cas d'usage de gestion des lecteurs.

    Le service crée des identifiants UUID et persiste les entités via le
    contrat DepotLecteur. Les règles propres au lecteur restent dans l'entité.
    """

    def __init__(
        self,
        depot_lecteur: DepotLecteur,
        depot_reservation: DepotReservation,
        horloge: Horloge,
    ) -> None:
        """Initialise le service avec ses dépôts.

        Args:
            depot_lecteur: Dépôt utilisé pour enregistrer et retrouver les lecteurs.
            depot_reservation: Dépôt utilisé pour consulter les réservations actives.
            horloge: Source de l'heure utilisée pour les suppressions logiques.
        """
        self._depot_lecteur = depot_lecteur
        self._depot_reservation = depot_reservation
        self._horloge = horloge

    def creer(self, nom: str, email: str) -> Lecteur:
        """Crée puis enregistre un lecteur valide.

        Args:
            nom: Nom non vide du lecteur.
            email: Adresse e-mail valide du lecteur.

        Returns:
            Le lecteur créé avec son UUID.

        Raises:
            ErreurValidation: Si les données ne respectent pas les règles du lecteur.
        """
        lecteur = Lecteur(uuid.uuid4(), nom, email)
        self._depot_lecteur.enregistrer(lecteur)
        return lecteur

    def modifier(self, lecteur_id: uuid.UUID, nom: str, email: str) -> Lecteur:
        """Modifie puis enregistre un lecteur existant.

        Args:
            lecteur_id: Identifiant UUID du lecteur à modifier.
            nom: Nouveau nom non vide.
            email: Nouvelle adresse e-mail valide.

        Returns:
            Le lecteur modifié.

        Raises:
            ErreurIntrouvable: Si aucun lecteur ne correspond à l'identifiant.
            ErreurValidation: Si les nouvelles données sont invalides.
        """
        lecteur = self._depot_lecteur.trouver_par_id(lecteur_id)
        if lecteur is None:
            raise ErreurIntrouvable("Lecteur introuvable.")
        lecteur.modifier(nom, email)
        self._depot_lecteur.enregistrer(lecteur)
        return lecteur

    def consulter(self, lecteur_id: uuid.UUID) -> tuple[Lecteur, list["Reservation"]]:
        """Retourne un lecteur avec ses réservations actives.

        Args:
            lecteur_id: Identifiant UUID du lecteur à consulter.

        Returns:
            Le lecteur et la liste de ses réservations actives.

        Raises:
            ErreurIntrouvable: Si aucun lecteur ne correspond à l'identifiant.
        """
        lecteur = self._depot_lecteur.trouver_par_id(lecteur_id)
        if lecteur is None:
            raise ErreurIntrouvable("Lecteur introuvable.")
        reservations_actives = self._depot_reservation.lister_actives_du_lecteur(
            lecteur_id
        )
        return lecteur, reservations_actives

    def supprimer(self, lecteur_id: uuid.UUID) -> None:
        """Supprime logiquement un lecteur sans réservation active.

        Args:
            lecteur_id: Identifiant UUID du lecteur à supprimer.

        Raises:
            ErreurIntrouvable: Si aucun lecteur ne correspond à l'identifiant.
            ErreurConflit: Si le lecteur possède une réservation active.
        """
        lecteur = self._depot_lecteur.trouver_par_id(lecteur_id)
        if lecteur is None:
            raise ErreurIntrouvable("Lecteur introuvable.")
        if self._depot_reservation.lister_actives_du_lecteur(lecteur_id):
            raise ErreurConflit("Impossible de supprimer un lecteur réservé.")
        lecteur.supprimer(self._horloge.maintenant())
        self._depot_lecteur.enregistrer(lecteur)