from django.core.management.base import BaseCommand, CommandError

from effranking.thrp.services import rebuild_thrp_ranks


class Command(BaseCommand):
    help = '从录像库重建效率榜，完成后原子替换 Redis 榜单；执行期间暂停相关写入'

    def add_arguments(self, parser):
        parser.add_argument('--ranking-name', choices=['thrp'], default='thrp')
        parser.add_argument('--batch-size', type=int, default=1000)

    def handle(self, *args, **options):
        if options['batch_size'] <= 0:
            raise CommandError('--batch-size must be positive')
        count = rebuild_thrp_ranks(options['batch_size'])
        self.stdout.write(self.style.SUCCESS(f'thrp: {count} players'))
