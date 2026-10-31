"""Tests du service de gestion des livres."""

import uuid
from datetime import datetime

import pytest
from src.application.depots_memoire import (
    DepotLivreMemoire,
    DepotReservationMemoire,
)
from src.application.horloge import HorlogeFictive
from src.application.service_livre import ServiceLivre
from src.domaine.erreurs import ErreurConflit, ErreurIntrouvable
from src.domaine.reservation import Reservation
from src.domaine.statut_reservation import StatutReservation


def un_service_livre(depot_livre: DepotLivreMemoire) -> ServiceLivre:
    """Construit un service de livre avec des collaborateurs contrôlés."""
    return ServiceLivre(
        depot_livre,
        DepotReservationMemoire(),
        HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0)),
    )


def test_creer_enregistre_un_livre_avec_un_uuid() -> None:
    depot_livre = DepotLivreMemoire()
    service_livre = un_service_livre(depot_livre)

    livre = service_livre.creer("Dune", "Frank Herbert", 1965)

    assert isinstance(livre.id, uuid.UUID)
    assert depot_livre.trouver_par_id(livre.id) == livre


def test_modifier_met_a_jour_un_livre_existant() -> None:
    depot_livre = DepotLivreMemoire()
    service_livre = un_service_livre(depot_livre)
    livre = service_livre.creer("Dune", "Frank Herbert", 1965)

    livre_modifie = service_livre.modifier(
        livre.id, "Dune Messiah", "Frank Herbert", 1969
    )

    assert livre_modifie.titre == "Dune Messiah"
    assert livre_modifie.annee_publication == 1969
    assert depot_livre.trouver_par_id(livre.id) == livre_modifie


def test_modifier_un_livre_absent_leve_erreur_introuvable() -> None:
    service_livre = un_service_livre(DepotLivreMemoire())

    with pytest.raises(ErreurIntrouvable):
        service_livre.modifier(
            uuid.uuid4(), "Dune Messiah", "Frank Herbert", 1969
        )


def test_rechercher_retourne_les_livres_correspondant_au_texte() -> None:
    depot_livre = DepotLivreMemoire()
    service_livre = un_service_livre(depot_livre)
    livre_trouve = service_livre.creer("Dune", "Frank Herbert", 1965)
    service_livre.creer("Fondation", "Isaac Asimov", 1951)

    livres = service_livre.rechercher("dune")

    assert livres == [livre_trouve]


def test_supprimer_effectue_une_suppression_logique() -> None:
    depot_livre = DepotLivreMemoire()
    maintenant = datetime(2026, 10, 31, 10, 0, 0)
    service_livre = ServiceLivre(
        depot_livre,
        DepotReservationMemoire(),
        HorlogeFictive(maintenant),
    )
    livre = service_livre.creer("Dune", "Frank Herbert", 1965)

    service_livre.supprimer(livre.id)

    assert livre.date_suppression == maintenant
    assert depot_livre.trouver_par_id(livre.id) == livre


def test_supprimer_un_livre_avec_reservation_active_leve_erreur_conflit() -> None:
    depot_livre = DepotLivreMemoire()
    depot_reservation = DepotReservationMemoire()
    service_livre = ServiceLivre(
        depot_livre,
        depot_reservation,
        HorlogeFictive(datetime(2026, 10, 31, 10, 0, 0)),
    )
    livre = service_livre.creer("Dune", "Frank Herbert", 1965)
    depot_reservation.enregistrer(
        Reservation(
            id=uuid.uuid4(),
            livre_id=livre.id,
            lecteur_id=uuid.uuid4(),
            statut=StatutReservation.RESERVEE,
            date_reservation=datetime(2026, 10, 31, 9, 0, 0),
        )
    )

    with pytest.raises(ErreurConflit):
        service_livre.supprimer(livre.id)

    assert livre.date_suppression is None