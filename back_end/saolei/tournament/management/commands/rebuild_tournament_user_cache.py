from django.core.management.base import BaseCommand

from tournament.cache import TournamentCache


class Command(BaseCommand):
    help = '重建 TournamentUser Redis 排行缓存'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=1000)

    def handle(self, *args, **options):
        count = TournamentCache().rebuild_tournament_user_cache(batch_size=options['batch_size'])
        self.stdout.write(self.style.SUCCESS(
            f'rebuilt {count} tournament user cache rows',
        ))
