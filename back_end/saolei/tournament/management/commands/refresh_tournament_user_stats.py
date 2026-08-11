from django.core.management.base import BaseCommand

from tournament.services import refresh_tournament_user_total_and_best_fields


class Command(BaseCommand):
    help = '刷新 TournamentUser 的历史 total 和 best 字段，不修改实时 score_current'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=1000)

    def handle(self, *args, **options):
        updated_count = refresh_tournament_user_total_and_best_fields(batch_size=options['batch_size'])
        self.stdout.write(self.style.SUCCESS(
            f'refreshed {updated_count} tournament users',
        ))
