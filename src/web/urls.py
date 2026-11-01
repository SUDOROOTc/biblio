"""URLs de l'API web."""

from django.urls import path

from src.web import views

urlpatterns = [
    path("auth/changer-mot-de-passe", views.ChangerMotDePasseView.as_view()),
    path("livres", views.LivreListCreateView.as_view()),
    path("livres/<uuid:livre_id>", views.LivreDetailView.as_view()),
    path("livres/recherche", views.LivreRechercheView.as_view()),
    path("lecteurs", views.LecteurListCreateView.as_view()),
    path("lecteurs/<uuid:lecteur_id>", views.LecteurDetailView.as_view()),
    path("lecteurs/<uuid:lecteur_id>/reservations", views.LecteurConsulterView.as_view()),
    path("reservations", views.ReservationListCreateView.as_view()),
    path("reservations/<uuid:reservation_id>/annuler", views.ReservationAnnulerView.as_view()),
    path("reservations/<uuid:reservation_id>/emprunter", views.ReservationEmprunterView.as_view()),
    path("reservations/<uuid:reservation_id>/retourner", views.ReservationRetournerView.as_view()),
]
