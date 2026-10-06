from django.core.management.base import BaseCommand, CommandError

from speedranking.pb.services import rebuild_pb_ranks


class Command(BaseCommand):
    help = '清空并分段重建 PB 普通/NF 榜、用户 rank hash 及小榜人数 hash，执行前暂停相关读写'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=100)

    def handle(self, *args, **options):
        if options['batch_size'] <= 0:
            raise CommandError('--batch-size must be positive')
        count = rebuild_pb_ranks(options['batch_size'], progress=self.progress)
        self.stdout.write(self.style.SUCCESS(f'PB: {count} players; ranks and counts refreshed'))

    def progress(self, count, last_player):
        self.stdout.write(f'PB: {count} players; last player id={last_player}')
