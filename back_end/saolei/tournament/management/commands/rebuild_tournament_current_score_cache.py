from django.core.management.base import BaseCommand, CommandError

from tournament.cache import TournamentCache


class Command(BaseCommand):
    help = '按当年 1 月 1 日 UTC 锚点重算当前比赛积分排行缓存，不修改数据库积分'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=1000)

    def handle(self, *args, **options):
        if options['batch_size'] < 1:
            raise CommandError('--batch-size must be positive')
        count = TournamentCache().rebuild_tournament_current_score_cache(batch_size=options['batch_size'])
        self.stdout.write(self.style.SUCCESS(f'rebuilt {count} tournament current score cache rows'))
