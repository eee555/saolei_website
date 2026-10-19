from django.core.management.base import BaseCommand

from speedranking.top.services import rebuild_soft_ranks


class Command(BaseCommand):
    help = 'Rebuild all nine top soft-strength and LSF indexes from Redis.'

    def handle(self, *args, **options):
        count = rebuild_soft_ranks()
        self.stdout.write(self.style.SUCCESS(f'{count} players: soft rankings and anchor snapshot published'))
