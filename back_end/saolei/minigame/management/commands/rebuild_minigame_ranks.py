from django.core.management.base import BaseCommand

from minigame.cache import MiniGameRankingCache
from minigame.utils import RANKINGS


class Command(BaseCommand):
    help = '从数据库重建小游戏排行榜缓存'

    def add_arguments(self, parser):
        parser.add_argument('--ranking-key', choices=tuple(RANKINGS))

    def handle(self, *args, **options):
        cache = MiniGameRankingCache()
        for ranking_key in (options['ranking_key'],) if options['ranking_key'] else RANKINGS:
            count = cache.rebuild(ranking_key)
            self.stdout.write(f'{ranking_key}: {count}')
