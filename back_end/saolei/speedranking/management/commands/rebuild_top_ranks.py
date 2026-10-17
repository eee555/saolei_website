from django.core.management.base import BaseCommand, CommandError

from speedranking.top.services import rebuild_top_ranks


class Command(BaseCommand):
    help = '分段重建 top 前五、十八个小榜及锚点，成功后原子发布'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=100)

    def handle(self, *args, **options):
        if options['batch_size'] <= 0:
            raise CommandError('--batch-size must be positive')
        count = rebuild_top_ranks(options['batch_size'], progress=lambda count, last: self.stdout.write(f'{count} players, last player id: {last}'))
        self.stdout.write(self.style.SUCCESS(f'top: {count} players; rankings and anchors published'))
