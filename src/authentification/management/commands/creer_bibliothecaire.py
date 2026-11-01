"""Commande pour créer le compte du bibliothécaire."""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée le compte du bibliothécaire s'il n'existe pas."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="bibliothecaire")
        parser.add_argument("--password", default="bibliothecaire")
        parser.add_argument("--email", default="bibliothecaire@biblio.local")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options["email"]

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Compte '{username}' déjà existant."))
            return

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Compte bibliothécaire '{username}' créé avec succès."))
