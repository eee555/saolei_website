import logging
import os
import time

from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef
from django_redis import get_redis_connection

from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import VideoModel
from videomanager.view_utils import refresh_video, update_personal_record_stock

cache = get_redis_connection('saolei_website')

logger = logging.getLogger('videomanager.management.refresh_stnb')


class Command(BaseCommand):
    help = '根据录像文件全量更新录像数据和所有用户纪录（timems/bvs/stnb/ioe/path）及排行榜'

    def add_arguments(self, parser):
        parser.add_argument(
            '--video-delay', type=float, default=0.05,
            help='每批录像间延时秒数（默认0.05）',
        )
        parser.add_argument(
            '--user-delay', type=float, default=0.2,
            help='每个用户间延时秒数（默认0.2）',
        )
        parser.add_argument(
            '--yes', action='store_true', dest='yes',
            help='跳过确认提示，直接执行',
        )

    def handle(self, *args, **options):
        video_delay = options['video_delay']
        user_delay = options['user_delay']

        if not options['yes']:
            self.stdout.write(self.style.WARNING(
                '警告：此命令将根据录像文件全量重写所有录像数据和用户纪录（timems/bvs/stnb/ioe/path），'
                '并重建 Redis 排行榜。\n'
                '执行前建议备份 msuser_userms 表及 Redis，且期间不应有用户上传录像。\n',
            ))
            answer = input('确认执行？(yes/no): ')
            if answer.lower() != 'yes':
                self.stdout.write(self.style.NOTICE('已取消'))
                return

        # ---------------------------------------------------------------
        # Phase 1: 用 refresh_video() 重解析录像文件，刷新 ExpandVideoModel.stnb
        # ---------------------------------------------------------------
        self.stdout.write(self.style.NOTICE('=== Phase 1: 重解析所有官方录像文件 ==='))

        video_ids = list(
            VideoModel.objects.filter(
                state=MS_TextChoices.State.OFFICIAL,
            ).values_list('id', flat=True).iterator(),
        )
        total = len(video_ids)
        self.stdout.write(f'共 {total} 个官方录像')

        missing_files = []
        for i, vid in enumerate(video_ids, 1):
            video = VideoModel.objects.get(id=vid)
            if not os.path.exists(video.file.path):
                missing_files.append((vid, video.file.path))
                continue
            refresh_video(video)

            if i % 100 == 0:
                self.stdout.write(f'  Phase 1 进度: {i}/{total}')
            if video_delay > 0:
                time.sleep(video_delay)

        if missing_files:
            self.stdout.write(self.style.WARNING(
                f'\n以下 {len(missing_files)} 个录像文件缺失，无法重算：',
            ))
            for vid, fpath in missing_files:
                self.stdout.write(f'  录像#{vid}: {fpath}')
        self.stdout.write(self.style.SUCCESS(f'Phase 1 完成，处理 {total} 个录像'))

        # ---------------------------------------------------------------
        # Phase 2: 用 update_personal_record_stock() 全量重算个人纪录 + Redis
        # ---------------------------------------------------------------
        self.stdout.write(self.style.NOTICE('\n=== Phase 2: 重算个人纪录与排行榜 ==='))

        has_official_videos = Exists(
            VideoModel.objects.filter(
                player=OuterRef('pk'),
                state=MS_TextChoices.State.OFFICIAL,
            ),
        )
        user_ids = list(
            UserProfile.objects.filter(
                has_official_videos,
                userms__isnull=False,
            ).values_list('id', flat=True).iterator(),
        )
        total_users = len(user_ids)
        self.stdout.write(f'共 {total_users} 个有录像的用户')

        for i, uid in enumerate(user_ids, 1):
            user = UserProfile.objects.get(id=uid)
            update_personal_record_stock(user)

            if i % 50 == 0:
                self.stdout.write(f'  Phase 2 进度: {i}/{total_users}')
            if user_delay > 0:
                time.sleep(user_delay)

        self.stdout.write(self.style.SUCCESS(f'Phase 2 完成，已重算 {total_users} 个用户的纪录'))

        # ---------------------------------------------------------------
        # Phase 3: 清空 news_queue，避免重算刷出的历史 PB 污染首页
        # ---------------------------------------------------------------
        cache.delete('news_queue')
        self.stdout.write(self.style.NOTICE('已清空 news_queue'))

        self.stdout.write(self.style.SUCCESS('\n全部完成！'))
