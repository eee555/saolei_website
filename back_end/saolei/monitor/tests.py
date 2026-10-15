from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.core.cache import cache
from django.tasks import TaskResultStatus
from django.test import override_settings, TestCase
from django.urls import resolve, Resolver404
from django_tasks_db.models import DBTaskResult, get_date_max

from . import services


@override_settings(
    CACHES={**settings.CACHES, 'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'monitor-tests'}},
    RATELIMIT_ENABLE=False,
)
class MonitorStatisticsTests(TestCase):
    def setUp(self):
        keys = [f'api:monitor/{name}' for name in ('diskusage', 'tasksummary', 'videosummary')]
        cache.delete_many(keys)
        self.addCleanup(cache.delete_many, keys)

    def test_statistics_are_cached_for_five_minutes_without_extending_ttl(self):
        cases = [
            ('diskusage', 'get_disk_usage', {'total': 100, 'used': 60, 'free': 40, 'video': 20, 'db': 10}),
            ('tasksummary', 'get_task_summary', {'total': 0, 'status': {'READY': 0}}),
            ('videosummary', 'get_video_summary', {'total': 0, 'software': {}, 'level': {}, 'mode': {}, 'state': {}}),
        ]
        for name, collector, result in cases:
            with self.subTest(name=name), patch(f'monitor.api.{collector}', return_value=result) as collect:
                with patch('time.time', return_value=1_700_000_000):
                    response = self.client.get(f'/api/monitor/{name}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), result)
                updated = {**result, 'total': result['total'] + 1}
                collect.return_value = updated

                with patch('time.time', return_value=1_700_000_299):
                    self.assertEqual(self.client.get(f'/api/monitor/{name}').json(), result)
                collect.assert_called_once_with()

                with patch('time.time', return_value=1_700_000_301):
                    self.assertEqual(self.client.get(f'/api/monitor/{name}').json(), updated)
                self.assertEqual(collect.call_count, 2)

    def test_old_statistics_and_world_monitor_routes_are_absent(self):
        for path in ('/api/common/diskusage', '/api/common/tasksummary', '/api/common/videosummary', '/monitor/io_cpus/', '/monitor/capacity/'):
            with self.subTest(path=path), self.assertRaises(Resolver404):
                resolve(path)

    def test_task_summary_includes_empty_statuses(self):
        DBTaskResult.objects.create(status=TaskResultStatus.READY, args_kwargs={'args': [], 'kwargs': {}}, run_after=get_date_max())
        response = self.client.get('/api/monitor/tasksummary')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'total': 1,
            'status': {str(status): int(status == TaskResultStatus.READY) for status in TaskResultStatus},
        })

    def test_empty_video_summary_retains_all_choice_groups(self):
        response = self.client.get('/api/monitor/videosummary')

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['total'], 0)
        for name in ('software', 'level', 'mode', 'state'):
            self.assertTrue(result[name])
            self.assertTrue(all(count == 0 for count in result[name].values()))

    def test_disk_usage_preserves_response_fields(self):
        with (
            patch.object(services.psutil, 'disk_usage', return_value=SimpleNamespace(total=100, used=60, free=40)),
            patch.object(services, 'get_db_size', return_value=10),
        ):
            response = self.client.get('/api/monitor/diskusage')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'total': 100, 'used': 60, 'free': 40, 'video': None, 'db': 10})
