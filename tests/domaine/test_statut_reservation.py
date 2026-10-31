"""Tests de l'énumération StatutReservation."""
from src.domaine.statut_reservation import StatutReservation


def test_les_cinq_statuts_existent():
    assert StatutReservation.RESERVEE
    assert StatutReservation.EMPRUNTEE
    assert StatutReservation.RETOURNEE
    assert StatutReservation.ANNULEE
    assert StatutReservation.EXPIREE


def test_reservee_et_empruntee_sont_actifs_les_autres_non():
    assert StatutReservation.RESERVEE.est_actif()
    assert StatutReservation.EMPRUNTEE.est_actif()
    assert not StatutReservation.RETOURNEE.est_actif()
    assert not StatutReservation.ANNULEE.est_actif()
    assert not StatutReservation.EXPIREE.est_actif()
