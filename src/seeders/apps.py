from django.apps import AppConfig


class SeedersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.seeders"
    label = "seeders"
    verbose_name = "Seeders"
