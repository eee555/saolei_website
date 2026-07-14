from django.apps import AppConfig


class VideomanagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videomanager'

    def ready(self):
        import videomanager.signals  # noqa: F401 - 信号注册需要
