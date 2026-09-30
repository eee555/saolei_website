from django.core.management.base import BaseCommand, CommandError

from speedranking.services import rebuild_speed_ranks
from speedranking.utils import BOARDS


class Command(BaseCommand):
    help = '从 VideoModel 重建竞速榜，完成后原子替换 Redis 榜单'

    def add_arguments(self, parser):
        parser.add_argument('--board', choices=BOARDS)
        parser.add_argument('--batch-size', type=int, default=1000)

    def handle(self, *args, **options):
        if options['batch_size'] <= 0:
            raise CommandError('--batch-size must be positive')
        boards = (options['board'],) if options['board'] else BOARDS
        for board, count in rebuild_speed_ranks(boards, options['batch_size']).items():
            self.stdout.write(self.style.SUCCESS(f'{board}: {count} players'))
