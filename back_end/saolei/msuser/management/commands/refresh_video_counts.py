from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q

from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from videomanager.models import VideoModel


class Command(BaseCommand):
    help = '刷新所有用户的录像计数，排除比赛录像'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=1000)

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        if batch_size <= 0:
            raise CommandError('--batch-size must be positive')

        counts = {
            'video_num_total': Count('id'),
            'video_num_beg': Count('id', filter=Q(level=MS_TextChoices.Level.BEGINNER)),
            'video_num_int': Count('id', filter=Q(level=MS_TextChoices.Level.INTERMEDIATE)),
            'video_num_exp': Count('id', filter=Q(level=MS_TextChoices.Level.EXPERT)),
            'video_num_std': Count('id', filter=Q(mode=MS_TextChoices.Mode.STD)),
            'video_num_nf': Count('id', filter=Q(mode=MS_TextChoices.Mode.NF)),
            'video_num_ng': Count('id', filter=Q(mode=MS_TextChoices.Mode.JSW)),
            'video_num_dg': Count('id', filter=Q(mode=MS_TextChoices.Mode.BZD)),
        }
        last_pk = 0
        updated = 0
        while users := list(UserMS.objects.filter(pk__gt=last_pk).order_by('pk').only('pk')[:batch_size]):
            # The reverse relation includes videos from ended tournaments too.
            rows = (
                VideoModel.objects
                .filter(player__userms_id__in=[user.pk for user in users], ongoing_tournament=False, tournaments__isnull=True)
                .order_by()
                .values('player__userms_id')
                .annotate(**counts)
            )
            counts_by_user = {row['player__userms_id']: row for row in rows}
            for user in users:
                user_counts = counts_by_user.get(user.pk, {})
                for field in counts:
                    setattr(user, field, user_counts.get(field, 0))
            UserMS.objects.bulk_update(users, list(counts), batch_size=batch_size)
            last_pk = users[-1].pk
            updated += len(users)

        self.stdout.write(self.style.SUCCESS(f'refreshed video counts for {updated} users'))
