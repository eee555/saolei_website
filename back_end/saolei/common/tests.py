from datetime import timedelta
import json
from pathlib import Path
import tempfile

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from django.utils import timezone
from django_redis import get_redis_connection
from django_tasks_db.models import DBTaskResult

from config.customranking import CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from config.global_settings import GameLevels, GameModes, RankingGameStats
from config.text_choices import MS_TextChoices, Tournament_TextChoices
from customranking.cache import PLuckRankingCache
from identifier.models import Identifier
from msuser.models import UserMS
from msuser.utils import get_video_num_limit
from tournament.models import GSCTournament
from userprofile.models import UserProfile
from utils.parser import MSVideoParser
from videomanager.models import VideoModel


FIXTURE_DIR = Path(__file__).resolve().parent / 'test_fixtures' / 'video_upload_ranking'


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
        response = self.client.get('/msuser/records/', {'id': self.user.id})
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def get_record_group_by_request(self, mode: str):
        records = self.get_records_by_request()
        return json.loads(records[f'{mode}_record'])

    def get_pluck_rank_by_request(self, level: str):
        response = self.client.get(
            '/api/customranking/pluck',
            {'level': level, 'start': 0, 'end': 20},
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def assert_pluck_task_enqueued(self, video: VideoModel):
        task_args = [
            task.args_kwargs
            for task in DBTaskResult.objects.filter(task_path='videomanager.tasks.task_video_pluck')
        ]
        self.assertIn(
            {'args': [video.id], 'kwargs': {}},
            task_args,
        )

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
        token = next((identifier for identifier in parser.tournament_identifiers if identifier), None)
        if token is None:
            self.skipTest('standard_gsc.evf 需要包含非空 GSC token')

        now = timezone.now()
        tournament = GSCTournament.objects.create(
            order=1,
            token=token,
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            state=Tournament_TextChoices.State.ONGOING,
        )

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
        self.assertIsNotNone(video.pluck)
        self.assert_pluck_task_not_enqueued(video)
        self.assertEqual(self.userms.video_num_limit, 100)

        self.add_identifier_by_request(identifier.identifier)

        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        self.assertEqual(self.userms.video_num_limit, get_video_num_limit(parser.timems))

    def test_upload_custom_video_refreshes_custom_pluck_record_after_pluck_save(self):
        video, parser = self.upload_fixture('custom_pluck.evf')
        if parser.level not in CUSTOM_PLUCK_LEVELS or parser.mode not in CUSTOM_PLUCK_MODES:
            self.skipTest('custom_pluck.evf 需要是 Density 排行支持的自定义级别和模式')

        self.assert_pluck_task_enqueued(video)
        self.assertIsNone(video.pluck)
        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 0)

        video.pluck = 0.25
        video.save(update_fields=['pluck'])

        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 1)
        self.assertEqual(rank['players'][0]['video_id'], video.id)
        self.assertEqual(rank['players'][0]['pluck'], video.pluck)
        self.assertEqual(rank['players'][0]['timems'], video.timems)

    def test_identifier_bind_and_unbind_refreshes_custom_pluck_record(self):
        parser = self.parse_fixture(self.fixture_path('custom_pluck.evf'))
        if parser.level not in CUSTOM_PLUCK_LEVELS or parser.mode not in CUSTOM_PLUCK_MODES:
            self.skipTest('custom_pluck.evf 需要是 Density 排行支持的自定义级别和模式')
        identifier = Identifier.objects.create(identifier=parser.identifier, safe=True)

        video, parser = self.upload_fixture('custom_pluck.evf', bind_identifier=False)
        video.pluck = 0.25
        video.save(update_fields=['pluck'])

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 0)

        self.add_identifier_by_request(identifier.identifier)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 1)
        self.assertEqual(rank['players'][0]['video_id'], video.id)

        self.delete_identifier_by_request(identifier.identifier)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        rank = self.get_pluck_rank_by_request(parser.level)
        self.assertEqual(rank['count'], 0)
