from django.apps import AppConfig


class MinigameConfig(AppConfig):
    name = 'minigame'
    verbose_name = '小游戏'

    def ready(self):
        from . import signals  # noqa: F401
