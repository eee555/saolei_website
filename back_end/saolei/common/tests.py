from datetime import timedelta
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from django.utils import timezone
from django_redis import get_redis_connection
from django_tasks import TaskResultStatus
from django_tasks_db.models import DBTaskResult, get_date_max

from common.management.commands import db_worker_robust
from config.common import TASK_CLEANUP_CONFIGS
from config.customranking import CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from config.global_settings import GameLevels, GameModes, RankingGameStats
from config.text_choices import MS_TextChoices, Tournament_TextChoices
from customranking.cache import PLuckRankingCache
from identifier.models import Identifier
from msuser.models import UserMS
from msuser.utils import get_video_num_limit
from tournament.cache import TournamentCache
from tournament.models import GSCParticipant, GSCTournament
from userprofile.models import UserProfile
from utils.parser import MSVideoParser
from videomanager.models import VideoModel
from . import api as common_api


FIXTURE_DIR = Path(__file__).resolve().parent / 'test_fixtures' / 'video_upload_ranking'
EXPERT_PERSONAL_PLUCK = 0.16342814596696364
CUSTOM_PLUCK_FIXTURE_PLUCK = 6.493148642054213


class LogPollTests(TestCase):
    def setUp(self):
        self.log_dir_context = tempfile.TemporaryDirectory()
        self.log_dir = Path(self.log_dir_context.name)
        self.log_dir_patch = patch.object(common_api, 'LOG_DIR', self.log_dir)
        self.log_dir_patch.start()

    def tearDown(self):
        self.log_dir_patch.stop()
        self.log_dir_context.cleanup()

    def write_log(self, filename: str, content: str):
        path = self.log_dir / filename
        path.write_bytes(content.encode())
        return path

    def test_poll_returns_content_from_offset(self):
        content = 'first\nsecond\n'
        offset = len('first\n'.encode())
        self.write_log('app.log', content)

        response = common_api.poll_log_tail(None, 'app.log', offset=offset)

        self.assertEqual(response, {
            'content': 'second\n',
            'offset': len(content.encode()),
            'size': len(content.encode()),
            'status': 'ok',
        })

    def test_poll_returns_empty_content_when_offset_matches_file_size(self):
        content = 'ready\n'
        self.write_log('app.log', content)

        response = common_api.poll_log_tail(None, 'app.log', offset=len(content.encode()))

        self.assertEqual(response, {
            'content': '',
            'offset': len(content.encode()),
            'size': len(content.encode()),
            'status': 'ok',
        })

    def test_poll_returns_reset_and_tail_when_file_shrinks(self):
        content = 'new-tail'
        self.write_log('app.log', content)

        response = common_api.poll_log_tail(None, 'app.log', offset=20, tail_bytes=4)

        self.assertEqual(response, {
            'content': 'tail',
            'offset': len(content.encode()),
            'size': len(content.encode()),
            'status': 'reset',
        })

    def test_poll_returns_deleted_when_file_disappears(self):
        response = common_api.poll_log_tail(None, 'app.log')

        self.assertEqual(response, {
            'content': '',
            'offset': 0,
            'size': 0,
            'status': 'deleted',
        })

    def test_list_logs_uses_file_modified_time(self):
        log_path = self.write_log('app.log', 'ready\n')
        modified_at = 1710979200
        os.utime(log_path, (modified_at - 3600, modified_at))

        [response] = common_api.list_logs(None)

        self.assertEqual(response['name'], 'app.log')
        self.assertEqual(response['mtime'].timestamp(), modified_at)


class TaskDeletionTests(TestCase):
    def setUp(self):
        self.staff = UserProfile.objects.create_user(
            username='task_delete_staff',
            email='task_delete_staff@example.com',
            password='password',
            is_staff=True,
        )
        self.client.force_login(self.staff)

    def create_task(
        self,
        *,
        status: TaskResultStatus = TaskResultStatus.READY,
        task_path: str = 'videomanager.tasks.task_video_pluck',
        finished_at=None,
        started_at=None,
        worker_ids=None,
    ):
        task = DBTaskResult.objects.create(
            status=status,
            args_kwargs={'args': [], 'kwargs': {}},
            priority=0,
            task_path=task_path,
            worker_ids=worker_ids or [],
            queue_name='default',
            backend_name='default',
            run_after=get_date_max(),
        )
        if started_at is not None:
            DBTaskResult.objects.filter(id=task.id).update(started_at=started_at)
            task.refresh_from_db()
        if finished_at is not None:
            DBTaskResult.objects.filter(id=task.id).update(finished_at=finished_at)
            task.refresh_from_db()
        return task

    def test_delete_ready_task(self):
        task = self.create_task()

        response = self.client.post('/common/staff/taskdelete/', {'task_id': task.id})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(DBTaskResult.objects.filter(id=task.id).exists())

    def test_delete_running_task_returns_conflict(self):
        task = self.create_task(status=TaskResultStatus.RUNNING)

        response = self.client.post('/common/staff/taskdelete/', {'task_id': task.id})

        self.assertEqual(response.status_code, 409)
        self.assertTrue(DBTaskResult.objects.filter(id=task.id).exists())

    def test_cleanup_tasks_deletes_only_one_batch_per_config(self):
        old_finished_at = timezone.now() - TASK_CLEANUP_CONFIGS[0]['expires'] - timedelta(days=1)
        for _ in range(3):
            self.create_task(
                status=TaskResultStatus.SUCCESSFUL,
                task_path=TASK_CLEANUP_CONFIGS[0]['task_path'],
                finished_at=old_finished_at,
            )

        with patch.object(common_api, 'TASK_CLEANUP_BATCH_SIZE', 2):
            deleted_count = common_api.cleanup_tasks(SimpleNamespace(user=self.staff))

        self.assertEqual(deleted_count, 2)
        self.assertEqual(
            DBTaskResult.objects.filter(
                status=TaskResultStatus.SUCCESSFUL,
                task_path=TASK_CLEANUP_CONFIGS[0]['task_path'],
            ).count(),
            1,
        )

    def test_running_task_health_marks_stale_unknown_worker_as_probably_orphaned(self):
        started_at = timezone.now() - timedelta(minutes=10)
        task = self.create_task(
            status=TaskResultStatus.RUNNING,
            started_at=started_at,
            worker_ids=['legacy-random-worker-id'],
        )

        result = common_api.running_task_health(SimpleNamespace(user=self.staff), stale_after_seconds=60)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], str(task.id))
        self.assertEqual(result[0]['worker_state'], common_api.WORKER_STATE_UNKNOWN)
        self.assertTrue(result[0]['stale_by_age'])
        self.assertTrue(result[0]['probably_orphaned'])

    def test_running_task_health_marks_dead_pid_worker_as_orphaned(self):
        started_at = timezone.now()
        task = self.create_task(
            status=TaskResultStatus.RUNNING,
            started_at=started_at,
            worker_ids=['testhost-12345-1700000000'],
        )

        with (
            patch.object(common_api, '_local_hostname_aliases', return_value={'testhost'}),
            patch.object(common_api.psutil, 'Process', side_effect=common_api.psutil.NoSuchProcess(12345)),
        ):
            result = common_api.running_task_health(SimpleNamespace(user=self.staff))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], str(task.id))
        self.assertEqual(result[0]['worker_state'], common_api.WORKER_STATE_DEAD)
        self.assertFalse(result[0]['stale_by_age'])
        self.assertTrue(result[0]['probably_orphaned'])

    def robust_command_options(self, pidfile: Path):
        return {
            'queue_name': 'default',
            'interval': 2,
            'batch': False,
            'backend_name': 'default',
            'startup_delay': False,
            'max_tasks': None,
            'worker_id': 'testhost-12345-1700000000',
            'pidfile': str(pidfile),
            'verbosity': 1,
        }

    def test_db_worker_robust_exits_when_worker_is_already_running(self):
        task = self.create_task(status=TaskResultStatus.RUNNING, started_at=timezone.now())

        with tempfile.TemporaryDirectory() as temp_dir:
            pidfile = Path(temp_dir) / 'worker.pid'
            with (
                patch.object(
                    db_worker_robust,
                    'iter_running_worker_processes',
                    return_value=[SimpleNamespace(info={'pid': 98765})],
                ),
                patch.object(db_worker_robust, 'call_command') as call_mock,
            ):
                db_worker_robust.Command().handle(**self.robust_command_options(pidfile))

        task.refresh_from_db()
        self.assertEqual(task.status, TaskResultStatus.RUNNING)
        call_mock.assert_not_called()

    def test_db_worker_robust_fails_orphans_then_starts_safe_worker(self):
        task = self.create_task(
            status=TaskResultStatus.RUNNING,
            started_at=timezone.now() - timedelta(minutes=1),
            worker_ids=['legacy-worker-id'],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            pidfile = Path(temp_dir) / 'worker.pid'
            with (
                patch.object(db_worker_robust, 'iter_running_worker_processes', return_value=[]),
                patch.object(db_worker_robust, 'call_command') as call_mock,
            ):
                db_worker_robust.Command().handle(**self.robust_command_options(pidfile))

        task.refresh_from_db()
        self.assertEqual(task.status, TaskResultStatus.FAILED)
        self.assertEqual(task.exception_class_path, 'builtins.RuntimeError')
        self.assertIn('db_worker_robust', task.traceback)
        call_mock.assert_called_once()
        self.assertEqual(call_mock.call_args.args, ('db_worker',))
        self.assertFalse(call_mock.call_args.kwargs['reload'])
        self.assertTrue(call_mock.call_args.kwargs['skip_checks'])
        self.assertEqual(call_mock.call_args.kwargs['worker_id'], 'testhost-12345-1700000000')


class VideoUploadRankingIntegrationTest(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.media_dir.name,
            RATELIMIT_ENABLE=False,
        )
        self.settings_override.enable()
        self.userms = UserMS.objects.create()
        self.user = UserProfile.objects.create_user(
            username='video_upload_rank_user',
            email='video_upload_rank@example.com',
            password='password',
            realname='测试用户',
            userms=self.userms,
        )
        self.client.force_login(self.user)

    def tearDown(self):
        cache = get_redis_connection('saolei_website')
        cache.delete('newest_queue', 'freeze_queue', 'news_queue')
        for level in CUSTOM_PLUCK_LEVELS:
            PLuckRankingCache(level).flush()
        self.settings_override.disable()
        self.media_dir.cleanup()

    def fixture_path(self, filename: str) -> Path:
        path = FIXTURE_DIR / filename
        if not path.exists():
            self.skipTest(f'缺少测试录像 fixture: {path}')
        return path

    def parse_fixture(self, path: Path) -> MSVideoParser:
        with path.open('rb') as file:
            return MSVideoParser(File(file, name=path.name))

    def bind_identifier(self, identifier: str):
        Identifier.objects.update_or_create(
            identifier=identifier,
            defaults={
                'userms': self.userms,
                'safe': True,
            },
        )

    def add_identifier_by_request(self, identifier: str):
        response = self.client.post('/identifier/add/', {'identifier': identifier})
        self.assertEqual(response.status_code, 200, response.content)
        return json.loads(response.content)

    def delete_identifier_by_request(self, identifier: str):
        response = self.client.post('/identifier/del/', {'identifier': identifier})
        self.assertEqual(response.status_code, 200, response.content)
        return json.loads(response.content)

    def get_records_by_request(self):
        response = self.client.get('/api/msuser/records', {'user_id': self.user.id})
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def get_record_group_by_request(self, mode: str):
        records = self.get_records_by_request()
        grouped_records = {}
        for stat in RankingGameStats:
            grouped_records[stat] = [
                records[f'{level}_{stat}_{mode}']
                for level in GameLevels
            ]
            grouped_records[f'{stat}_id'] = [
                records[f'{level}_{stat}_id_{mode}']
                for level in GameLevels
            ]
        return grouped_records

    def get_pluck_rank_by_request(self, level: str):
        response = self.client.get(
            '/api/customranking/pluck',
            {'level': level, 'start': 0, 'end': 20},
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def assert_pluck_task_not_enqueued(self, video: VideoModel):
        self.assertFalse(
            DBTaskResult.objects.filter(
                task_path='videomanager.tasks.task_video_pluck',
                args_kwargs={'args': [video.id], 'kwargs': {}},
            ).exists(),
        )

    def upload_fixture(self, filename: str, *, bind_identifier=True):
        path = self.fixture_path(filename)
        parser = self.parse_fixture(path)
        if bind_identifier:
            self.bind_identifier(parser.identifier)

        with path.open('rb') as file:
            uploaded_file = SimpleUploadedFile(path.name, file.read())

        response = self.client.post('/common/uploadvideo/', {'file': uploaded_file})
        self.assertEqual(response.status_code, 200, response.content)
        data = json.loads(response.content)
        video = VideoModel.objects.select_related('video', 'player__userms').get(pk=data['data']['id'])
        return video, parser

    def assert_no_personal_record(self):
        for mode in GameModes:
            records = self.get_record_group_by_request(mode)
            for stat in RankingGameStats:
                for level_index, _level in enumerate(GameLevels):
                    self.assertIsNone(records[f'{stat}_id'][level_index])

    def assert_personal_record(self, parser: MSVideoParser, video: VideoModel):
        records = self.get_record_group_by_request('std')
        level_index = GameLevels.index(parser.level)
        self.assertEqual(records['timems'][level_index], parser.timems)
        self.assertEqual(records['timems_id'][level_index], video.id)

    def test_upload_tournament_video_checkin_blocks_personal_record_refresh(self):
        parser = self.parse_fixture(self.fixture_path('standard_gsc.evf'))
        token = next((identifier for identifier in parser.tournament_identifier if identifier), None)
        if token is None:
            self.skipTest('standard_gsc.evf 需要包含非空 GSC token')

        now = timezone.now()
        tournament = GSCTournament.objects.create(
            order=1,
            token=token,
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            state=Tournament_TextChoices.State.NORMAL,
        )
        participant = GSCParticipant.objects.create(
            tournament=tournament,
            user=self.user,
            token=token,
            start_time=tournament.start_time,
            end_time=tournament.end_time,
        )
        tournament_cache = TournamentCache()
        tournament_cache.update_tournament(tournament)
        tournament_cache.update_participant(participant)

        video, _ = self.upload_fixture('standard_gsc.evf')

        video.refresh_from_db()
        self.assertTrue(video.ongoing_tournament)
        self.assertTrue(tournament.videos.filter(pk=video.pk).exists())
        self.assert_no_personal_record()

    def test_upload_standard_video_refreshes_personal_record(self):
        video, parser = self.upload_fixture('beginner_personal.evf')

        self.userms.refresh_from_db()
        self.assertFalse(video.ongoing_tournament)
        self.assertEqual(parser.state, MS_TextChoices.State.OFFICIAL)
        self.assert_personal_record(parser, video)

    def test_identifier_bind_and_unbind_refreshes_personal_record(self):
        parser = self.parse_fixture(self.fixture_path('beginner_personal.evf'))
        identifier = Identifier.objects.create(identifier=parser.identifier, safe=True)

        video, parser = self.upload_fixture('beginner_personal.evf', bind_identifier=False)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assert_no_personal_record()

        self.add_identifier_by_request(identifier.identifier)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        self.assert_personal_record(parser, video)

        self.delete_identifier_by_request(identifier.identifier)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assert_no_personal_record()

    def test_identifier_bind_refreshes_video_num_limit_for_expert_standard_video(self):
        parser = self.parse_fixture(self.fixture_path('expert_personal.evf'))
        if parser.level != MS_TextChoices.Level.EXPERT or parser.mode != MS_TextChoices.Mode.STD:
            self.skipTest('expert_personal.evf 需要是高级标准录像')
        identifier = Identifier.objects.create(identifier=parser.identifier, safe=True)

        video, _ = self.upload_fixture('expert_personal.evf', bind_identifier=False)

        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assertAlmostEqual(video.pluck, EXPERT_PERSONAL_PLUCK, places=12)
        self.assert_pluck_task_not_enqueued(video)
        self.assertEqual(self.userms.video_num_limit, 100)

        self.add_identifier_by_request(identifier.identifier)

        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        self.assertEqual(self.userms.video_num_limit, get_video_num_limit(parser.timems))

    def test_upload_custom_video_calculates_pluck_and_refreshes_custom_pluck_record(self):
        video, parser = self.upload_fixture('custom_pluck.evf')
        if parser.level not in CUSTOM_PLUCK_LEVELS or parser.mode not in CUSTOM_PLUCK_MODES:
            self.skipTest('custom_pluck.evf 需要是 Density 排行支持的自定义级别和模式')

        video.refresh_from_db()
        self.assertAlmostEqual(video.pluck, CUSTOM_PLUCK_FIXTURE_PLUCK, places=12)
        self.assert_pluck_task_not_enqueued(video)
        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 1)
        self.assertEqual(rank['players'][0]['video_id'], video.id)
        self.assertAlmostEqual(rank['players'][0]['pluck'], CUSTOM_PLUCK_FIXTURE_PLUCK, places=12)
        self.assertEqual(rank['players'][0]['timems'], video.timems)

    def test_identifier_bind_and_unbind_refreshes_custom_pluck_record(self):
        parser = self.parse_fixture(self.fixture_path('custom_pluck.evf'))
        if parser.level not in CUSTOM_PLUCK_LEVELS or parser.mode not in CUSTOM_PLUCK_MODES:
            self.skipTest('custom_pluck.evf 需要是 Density 排行支持的自定义级别和模式')
        identifier = Identifier.objects.create(identifier=parser.identifier, safe=True)

        video, parser = self.upload_fixture('custom_pluck.evf', bind_identifier=False)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assertAlmostEqual(video.pluck, CUSTOM_PLUCK_FIXTURE_PLUCK, places=12)
        self.assert_pluck_task_not_enqueued(video)
        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 0)

        self.add_identifier_by_request(identifier.identifier)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 1)
        self.assertEqual(rank['players'][0]['video_id'], video.id)
        self.assertAlmostEqual(rank['players'][0]['pluck'], CUSTOM_PLUCK_FIXTURE_PLUCK, places=12)

        self.delete_identifier_by_request(identifier.identifier)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 0)
