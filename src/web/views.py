"""Vues de l'API Biblio."""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.domaine.erreurs import ErreurDomaine
from src.web.exceptions import traduire_erreur_domaine
from src.web.factories import get_service_livre, get_service_lecteur, get_service_reservation
from src.web.serializers import (
    ChangerMotDePasseSerializer,
    LecteurCreationSerializer,
    LecteurModificationSerializer,
    LivreCreationSerializer,
    LivreModificationSerializer,
    ReservationCreationSerializer,
)


def _livre_vers_dict(livre):
    return {
        "id": str(livre.id),
        "titre": livre.titre,
        "auteur": livre.auteur,
        "annee_publication": livre.annee_publication,
        "date_suppression": livre.date_suppression.isoformat() if livre.date_suppression else None,
    }


def _lecteur_vers_dict(lecteur):
    return {
        "id": str(lecteur.id),
        "nom": lecteur.nom,
        "email": lecteur.email,
        "date_suppression": lecteur.date_suppression.isoformat() if lecteur.date_suppression else None,
    }


def _reservation_vers_dict(reservation):
    return {
        "id": str(reservation.id),
        "livre_id": str(reservation.livre_id),
        "lecteur_id": str(reservation.lecteur_id),
        "statut": reservation.statut.value,
        "date_reservation": reservation.date_reservation.isoformat() if reservation.date_reservation else None,
        "date_emprunt": reservation.date_emprunt.isoformat() if reservation.date_emprunt else None,
        "date_retour": reservation.date_retour.isoformat() if reservation.date_retour else None,
    }


class LivreListCreateView(APIView):
    @extend_schema(request=LivreCreationSerializer, responses={201: None})
    def post(self, request):
        serializer = LivreCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = get_service_livre()
        try:
            livre = service.creer(
                serializer.validated_data["titre"],
                serializer.validated_data["auteur"],
                serializer.validated_data["annee_publication"],
            )
            return Response(_livre_vers_dict(livre), status=status.HTTP_201_CREATED)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class LivreDetailView(APIView):
    @extend_schema(request=LivreModificationSerializer, responses={200: None})
    def put(self, request, livre_id):
        serializer = LivreModificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = get_service_livre()
        try:
            livre = service.modifier(
                livre_id,
                serializer.validated_data["titre"],
                serializer.validated_data["auteur"],
                serializer.validated_data["annee_publication"],
            )
            return Response(_livre_vers_dict(livre), status=status.HTTP_200_OK)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)

    @extend_schema(responses={204: None})
    def delete(self, request, livre_id):
        service = get_service_livre()
        try:
            service.supprimer(livre_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class LivreRechercheView(APIView):
    @extend_schema(responses={200: None})
    def get(self, request):
        texte = request.query_params.get("q", "")
        annee_publication = request.query_params.get("annee_publication")
        if annee_publication is not None:
            try:
                annee_publication = int(annee_publication)
            except (TypeError, ValueError):
                annee_publication = None
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)

        service = get_service_livre()
        livres = service.rechercher(texte, annee_publication)

        paginator = Paginator(livres, page_size)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return Response({
            "count": paginator.count,
            "next": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "results": [_livre_vers_dict(l) for l in page_obj.object_list],
        })


class LecteurListCreateView(APIView):
    @extend_schema(request=None, responses={200: None})
    def get(self, request):
        service = get_service_lecteur()
        lecteurs = service.lister()
        return Response([_lecteur_vers_dict(lecteur) for lecteur in lecteurs])

    @extend_schema(request=LecteurCreationSerializer, responses={201: None})
    def post(self, request):
        serializer = LecteurCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = get_service_lecteur()
        try:
            lecteur = service.creer(
                serializer.validated_data["nom"],
                serializer.validated_data["email"],
            )
            return Response(_lecteur_vers_dict(lecteur), status=status.HTTP_201_CREATED)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class LecteurDetailView(APIView):
    @extend_schema(request=LecteurModificationSerializer, responses={200: None})
    def put(self, request, lecteur_id):
        serializer = LecteurModificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = get_service_lecteur()
        try:
            lecteur = service.modifier(
                lecteur_id,
                serializer.validated_data["nom"],
                serializer.validated_data["email"],
            )
            return Response(_lecteur_vers_dict(lecteur), status=status.HTTP_200_OK)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)

    @extend_schema(responses={204: None})
    def delete(self, request, lecteur_id):
        service = get_service_lecteur()
        try:
            service.supprimer(lecteur_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class LecteurConsulterView(APIView):
    @extend_schema(responses={200: None})
    def get(self, request, lecteur_id):
        service = get_service_lecteur()
        try:
            lecteur, reservations = service.consulter(lecteur_id)
            return Response(
                {
                    "lecteur": _lecteur_vers_dict(lecteur),
                    "reservations_actives": [_reservation_vers_dict(r) for r in reservations],
                }
            )
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class ReservationListCreateView(APIView):
    @extend_schema(request=ReservationCreationSerializer, responses={201: None})
    def get(self, request):
        service = get_service_reservation()
        reservations = service.lister()
        return Response([_reservation_vers_dict(r) for r in reservations])

    @extend_schema(request=ReservationCreationSerializer, responses={201: None})
    def post(self, request):
        serializer = ReservationCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = get_service_reservation()
        try:
            reservation = service.reserver(
                serializer.validated_data["livre_id"],
                serializer.validated_data["lecteur_id"],
            )
            return Response(_reservation_vers_dict(reservation), status=status.HTTP_201_CREATED)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class ReservationAnnulerView(APIView):
    @extend_schema(request=None, responses={200: None})
    def post(self, request, reservation_id):
        service = get_service_reservation()
        try:
            service.annuler(reservation_id)
            return Response(status=status.HTTP_200_OK)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class ReservationEmprunterView(APIView):
    @extend_schema(request=None, responses={200: None})
    def post(self, request, reservation_id):
        service = get_service_reservation()
        try:
            service.enregistrer_emprunt(reservation_id)
            return Response(status=status.HTTP_200_OK)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class ReservationRetournerView(APIView):
    @extend_schema(request=None, responses={200: None})
    def post(self, request, reservation_id):
        service = get_service_reservation()
        try:
            service.enregistrer_retour(reservation_id)
            return Response(status=status.HTTP_200_OK)
        except ErreurDomaine as exc:
            return traduire_erreur_domaine(exc)


class ChangerMotDePasseView(APIView):
    """Permet au bibliothécaire connecté de changer son mot de passe."""

    @extend_schema(request=ChangerMotDePasseSerializer, responses={200: None})
    def post(self, request):
        serializer = ChangerMotDePasseSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["nouveau_mot_de_passe"])
        user.save()
        return Response({"detail": "Mot de passe modifié avec succès."}, status=status.HTTP_200_OK)
