from django.core.management.base import BaseCommand

from config.customranking import CUSTOM_PLUCK_CONFIGS
from customranking.services import rebuild_custom_pluck_cache


class Command(BaseCommand):
    help = '重建自定义 pLuck 排行 Redis 缓存'

    def add_arguments(self, parser):
        parser.add_argument(
            '--level',
            choices=list(CUSTOM_PLUCK_CONFIGS),
            help='只重建指定自定义配置；省略则重建全部配置',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='每批写入 Redis 的纪录数量，默认 1000',
        )

    def handle(self, *args, **options):
        level = options['level']
        levels = [level] if level is not None else CUSTOM_PLUCK_CONFIGS
        counts = rebuild_custom_pluck_cache(
            levels=levels,
            batch_size=options['batch_size'],
        )

        for level, count in counts.items():
            self.stdout.write(self.style.SUCCESS(
                f'{level}: rebuilt {count} records',
            ))
