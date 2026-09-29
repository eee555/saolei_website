from itertools import islice
import re

from django.core.management.base import BaseCommand
from django_redis import get_redis_connection


# Keep the legacy key format independent of the ranking code being removed.
LEGACY_RECORD_KEY = re.compile(r'player_(timems|bvs|stnb|ioe|path)_(std|nf|ng|dg)_([0-9]+|ids)')
BATCH_SIZE = 1000


class Command(BaseCommand):
    help = 'Delete legacy speed ranking Redis keys and news_queue.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='List matching keys without deleting them.')

    def handle(self, *args, **options):
        cache = get_redis_connection('saolei_website')
        keys = (
            key
            for key in cache.scan_iter(match='player_*', count=BATCH_SIZE)
            if LEGACY_RECORD_KEY.fullmatch(key.decode() if isinstance(key, bytes) else key)
        )
        count = 0
        while batch := list(islice(keys, BATCH_SIZE)):
            if options['dry_run']:
                for key in batch:
                    self.stdout.write(key.decode() if isinstance(key, bytes) else key)
                count += len(batch)
            else:
                count += cache.unlink(*batch)

        if options['dry_run']:
            if cache.exists('news_queue'):
                self.stdout.write('news_queue')
                count += 1
            self.stdout.write(self.style.SUCCESS(f'Matched {count} legacy Redis keys (dry run).'))
        else:
            count += cache.unlink('news_queue')
            self.stdout.write(self.style.SUCCESS(f'Deleted {count} legacy Redis keys.'))
