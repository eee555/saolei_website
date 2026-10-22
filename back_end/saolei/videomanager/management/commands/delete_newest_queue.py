from django.core.management.base import BaseCommand

from videomanager.services import delete_newest_queue


class Command(BaseCommand):
    help = '裁剪 Redis 最新录像队列：按上传时间保留最新 1000 条，时间相同时保留 ID 较大的录像'

    def handle(self, *args, **options):
        delete_newest_queue()
        self.stdout.write(self.style.SUCCESS('最新录像队列清理完成'))
