from django.test import TestCase
from django_redis import get_redis_connection

from config.customranking import CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from config.text_choices import MS_TextChoices
from customranking.cache import PLuckRankingCache
from customranking.models import CustomPluckRecord
from msuser.models import UserMS
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .models import Identifier
from .services import bind_identifier, set_safe, unbind_identifier


class BindIdentifierServiceTest(TestCase):
    def setUp(self):
        self.userms = UserMS.objects.create()
        self.user = UserProfile.objects.create_user(
            username='identifier_service_user',
            email='identifier_service@example.com',
            password='password',
            userms=self.userms,
        )

    def tearDown(self):
        cache = get_redis_connection('saolei_website')
        cache.delete('newest_queue', 'freeze_queue', 'review_queue')
        for level in CUSTOM_PLUCK_LEVELS:
            PLuckRankingCache(level).flush()

    def create_video(self, identifier: str, *, level=MS_TextChoices.Level.BEGINNER, mode=MS_TextChoices.Mode.STD, pluck=None):
        expand_video = ExpandVideoModel.objects.create(identifier=identifier)
        return VideoModel.objects.create(
            player=self.user,
            file='videos/test.evf',
            video=expand_video,
            state=MS_TextChoices.State.IDENTIFIER,
            software=MS_TextChoices.Software.EVF,
            level=level,
            mode=mode,
            timems=10000,
            bv=50,
            left=1,
            right=1,
            double=1,
            left_ce=1,
            right_ce=1,
            double_ce=1,
            path=20,
            pluck=pluck,
        )

    def test_bind_identifier_bulk_updates_videos_and_personal_record(self):
        identifier = Identifier.objects.create(identifier='classic-id', safe=True)
        video = self.create_video('classic-id')

        changed_count = bind_identifier(identifier, self.userms)

        identifier.refresh_from_db()
        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertEqual(changed_count, 1)
        self.assertEqual(identifier.userms_id, self.userms.id)
        self.assertIn(identifier.identifier, self.userms.identifiers)
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        self.assertEqual(self.userms.b_timems_std, video.timems)
        self.assertEqual(self.userms.b_timems_id_std, video.id)

        changed_count = unbind_identifier(identifier, self.userms)

        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertEqual(changed_count, 1)
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assertNotIn(identifier.identifier, self.userms.identifiers)
        self.assertIsNone(self.userms.b_timems_id_std)

    def test_bind_identifier_bulk_updates_custom_pluck_record(self):
        identifier = Identifier.objects.create(identifier='custom-id', safe=True)
        video = self.create_video(
            'custom-id',
            level=next(iter(CUSTOM_PLUCK_LEVELS)),
            mode=next(iter(CUSTOM_PLUCK_MODES)),
            pluck=0.25,
        )

        bind_identifier(identifier, self.userms)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.OFFICIAL)
        record = CustomPluckRecord.objects.get(player=self.user, level=video.level)
        self.assertEqual(record.video_id, video.id)
        self.assertEqual(record.pluck, video.pluck)

        unbind_identifier(identifier, self.userms)

        video.refresh_from_db()
        self.assertEqual(video.state, MS_TextChoices.State.IDENTIFIER)
        self.assertFalse(CustomPluckRecord.objects.filter(player=self.user, level=video.level).exists())

    def test_set_safe_updates_unbound_identifier(self):
        identifier = Identifier.objects.create(identifier='review-id', safe=False)

        set_safe(identifier, True)
        identifier.refresh_from_db()
        self.assertTrue(identifier.safe)

        set_safe(identifier, False)
        identifier.refresh_from_db()
        self.assertFalse(identifier.safe)

    def test_set_safe_rejects_bound_identifier_marked_unsafe(self):
        identifier = Identifier.objects.create(identifier='bound-id', safe=True, userms=self.userms)

        with self.assertRaises(ValueError):
            set_safe(identifier, False)

        identifier.refresh_from_db()
        self.assertTrue(identifier.safe)
        self.assertEqual(identifier.userms_id, self.userms.id)
