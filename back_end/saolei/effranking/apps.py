from django.apps import AppConfig


class EffrankingConfig(AppConfig):
    name = 'effranking'
    verbose_name = '效率排行榜'

    def ready(self):
        import effranking.signals  # noqa: F401
