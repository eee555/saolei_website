from django.apps import AppConfig


class SpeedrankingConfig(AppConfig):
    name = 'speedranking'

    def ready(self):
        import speedranking.signals  # noqa: F401
