from django.apps import AppConfig


class IdentifierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'identifier'

    def ready(self):
        import identifier.signals  # noqa: F401 - 信号注册需要
