from django.apps import AppConfig


class MsuserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'msuser'

    def ready(self):
        import msuser.signals  # noqa: F401 - register signal handlers
