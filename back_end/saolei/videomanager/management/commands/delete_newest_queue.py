from django.core.management.base import BaseCommand

from videomanager.services import delete_newest_queue


class Command(BaseCommand):
    help = '清理 Redis 最新录像队列：超过 100 条时删除超过 7 天的记录'

    def handle(self, *args, **options):
        delete_newest_queue()
        self.stdout.write(self.style.SUCCESS('最新录像队列清理完成'))
