from django.core.management.base import BaseCommand, CommandError

from videomanager.models import VideoModel
from videomanager.utils import VideoParseError
from videomanager.view_utils import refresh_video


class Command(BaseCommand):
    help = '逐条重新解析全部录像，通过实例保存触发信号接收器'

    def handle(self, *args, **options):
        refreshed = 0
        skipped = 0
        videos = VideoModel.objects.select_related('video', 'player').order_by('pk')
        for video in videos.iterator():
            try:
                refresh_video(video)
            except VideoParseError as exc:
                skipped += 1
                self.stderr.write(self.style.WARNING(f'录像#{video.pk}解析失败，已跳过：{exc}'))
                continue
            except Exception as exc:
                raise CommandError(f'录像#{video.pk}刷新失败，已完成 {refreshed} 条：{exc}') from exc
            refreshed += 1
        self.stdout.write(self.style.SUCCESS(f'已刷新 {refreshed} 条录像，跳过 {skipped} 条解析失败的录像'))
