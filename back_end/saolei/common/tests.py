from datetime import timedelta
import json
import tempfile
from pathlib import Path

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, RequestFactory, TestCase
from django.utils import timezone
from django_redis import get_redis_connection

from config.customranking import CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from config.global_settings import RankingGameStats
from config.text_choices import MS_TextChoices, Tournament_TextChoices
from customranking.cache import PLuckRankingCache
from customranking.models import CustomPluckRecord
from identifier.models import Identifier
from identifier.services import bind_identifier as bind_identifier_service
from identifier.services import unbind_identifier
from msuser.models import UserMS
from tournament.models import GSCTournament
from userprofile.models import UserProfile
from utils.parser import MSVideoParser
from videomanager.models import VideoModel
from .views import video_upload


FIXTURE_DIR = Path(__file__).resolve().parent / 'test_fixtures' / 'video_upload_ranking'


class VideoUploadRankingIntegrationTest(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.media_dir.name,
            RATELIMIT_ENABLE=False,
        )
        self.settings_override.enable()
        self.factory = RequestFactory()
        self.userms = UserMS.objects.create()
        self.user = UserProfile.objects.create_user(
            username='video_upload_rank_user',
            email='video_upload_rank@example.com',
            password='password',
            realname='测试用户',
            userms=self.userms,
        )

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

    def upload_fixture(self, filename: str, *, bind_identifier=True):
        path = self.fixture_path(filename)
        parser = self.parse_fixture(path)
        if bind_identifier:
            self.bind_identifier(parser.identifier)

        with path.open('rb') as file:
            uploaded_file = SimpleUploadedFile(path.name, file.read())
        request = self.factory.post('/common/uploadvideo/', {'file': uploaded_file})
        request.user = self.user

        response = video_upload(request)
        self.assertEqual(response.status_code, 200, response.content)
        data = json.loads(response.content)
        video = VideoModel.objects.select_related('video', 'player__userms').get(pk=data['data']['id'])
        return video, parser

    def assert_no_personal_record(self):
        self.userms.refresh_from_db()
        for stat in RankingGameStats:
            for level in [MS_TextChoices.Level.BEGINNER, MS_TextChoices.Level.INTERMEDIATE, MS_TextChoices.Level.EXPERT]:
                self.assertIsNone(getattr(self.userms, f'{level}_{stat}_id_std'))

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
        video, parser = self.upload_fixture('standard_personal.evf')

        self.userms.refresh_from_db()
        self.assertFalse(video.ongoing_tournament)
        self.assertEqual(parser.state, MS_TextChoices.State.OFFICIAL)
        self.assertEqual(getattr(self.userms, f'{parser.level}_timems_std'), parser.timems)
        self.assertEqual(getattr(self.userms, f'{parser.level}_timems_id_std'), video.id)

    def test_identifier_bind_and_unbind_refreshes_personal_record(self):
        parser = self.parse_fixture(self.fixture_path('standard_personal.evf'))
        identifier = Identifier.objects.create(identifier=parser.identifier, safe=True)

        video, parser = self.upload_fixture('standard_personal.evf', bind_identifier=False)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assert_no_personal_record()

        bind_identifier_service(identifier, self.userms)

        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        self.assertEqual(getattr(self.userms, f'{parser.level}_timems_std'), parser.timems)
        self.assertEqual(getattr(self.userms, f'{parser.level}_timems_id_std'), video.id)

        unbind_identifier(identifier, self.userms)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assert_no_personal_record()

    def test_upload_custom_video_refreshes_custom_pluck_record_after_pluck_save(self):
        video, parser = self.upload_fixture('custom_pluck.evf')
        if parser.level not in CUSTOM_PLUCK_LEVELS or parser.mode not in CUSTOM_PLUCK_MODES:
            self.skipTest('custom_pluck.evf 需要是 Density 排行支持的自定义级别和模式')

        self.assertFalse(CustomPluckRecord.objects.filter(player=self.user, level=parser.level).exists())

        video.pluck = 0.25
        video.save(update_fields=['pluck'])

        record = CustomPluckRecord.objects.get(player=self.user, level=parser.level)
        self.assertEqual(record.video_id, video.id)
        self.assertEqual(record.pluck, video.pluck)
        self.assertEqual(record.timems, video.timems)
        self.assertEqual(record.upload_time, video.upload_time)

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
        self.assertFalse(CustomPluckRecord.objects.filter(player=self.user, level=parser.level).exists())

        bind_identifier_service(identifier, self.userms)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        record = CustomPluckRecord.objects.get(player=self.user, level=parser.level)
        self.assertEqual(record.video_id, video.id)

        unbind_identifier(identifier, self.userms)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assertFalse(CustomPluckRecord.objects.filter(player=self.user, level=parser.level).exists())
