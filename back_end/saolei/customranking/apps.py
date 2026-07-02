from django.apps import AppConfig


class CustomrankingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customranking'

    def ready(self):
        import customranking.signals  # noqa: F401 - register signal handlers
