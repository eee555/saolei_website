import json

from django.core.management.base import BaseCommand

from config.customranking import CUSTOM_PLUCK_LEVELS
from customranking.cache import get_custom_pluck_detail_key
from videomanager.cache import cache, newest_cache


class Command(BaseCommand):
    help = 'Remove redundant video fields from known Redis hashes without changing newest-queue membership.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        # Compare the old value inside Redis: concurrent updates/removals must not be overwritten or resurrected.
        replace = cache.register_script("""
            if redis.call('HGET', KEYS[1], ARGV[1]) == ARGV[2] then
                redis.call('HSET', KEYS[1], ARGV[1], ARGV[3])
                return 1
            end
            return 0
        """)
        definitions = [(newest_cache.key, ('state', 'time', 'player_id'))]
        definitions.extend((get_custom_pluck_detail_key(level), ('video_id', 'timems', 'upload_time')) for level in sorted(CUSTOM_PLUCK_LEVELS))
        changed = 0
        for key, fields in definitions:
            before = cache.memory_usage(key, samples=5) or 0
            count = 0
            for member, raw in cache.hscan_iter(key, count=100):
                previous = json.loads(raw)
                compact = {field: previous[field] for field in fields}
                if compact == previous:
                    continue
                value = json.dumps(compact)
                count += 1 if options['dry_run'] else int(replace(keys=[key], args=[member, raw, value]))
            changed += count
            after = cache.memory_usage(key, samples=5) or 0
            self.stdout.write(f'{key}: changed={count}, bytes={before}->{after}')
        if not options['dry_run']:
            cache.delete('freeze_queue', 'review_queue')
        self.stdout.write(self.style.SUCCESS(f'Entries compacted: {changed}; dry_run={options["dry_run"]}'))
