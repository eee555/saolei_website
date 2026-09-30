from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.db import transaction
from django.test import override_settings, TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from userprofile.services import has_sub200_expert_video
from videomanager.models import ExpandVideoModel, VideoModel
from .cache import SpeedRankingCache
from .services import add_videos_to_speed_ranks, best_candidate, remove_videos_from_speed_ranks
from .utils import BOARDS


@override_settings(RATELIMIT_ENABLE=False)
class SpeedRankingTests(TestCase):
    def setUp(self):
        for board in BOARDS:
            ranking = SpeedRankingCache(board)
            ranking.flush()
            self.addCleanup(ranking.flush)
        self.user = self.create_user('speed')

    def create_user(self, name):
        return UserProfile.objects.create_user(username=name, email=f'{name}@example.com', userms=UserMS.objects.create())

    def create_video(self, **kwargs):
        fields = {'player': self.user, 'video': ExpandVideoModel.objects.create(identifier='speed'), 'file': 'videos/speed.evf', 'software': 'e', 'state': MS_TextChoices.State.OFFICIAL, 'level': 'b', 'mode': '00', 'bv': 4, 'timems': 1000, 'right_ce': 0}
        fields.update(kwargs)
        with self.captureOnCommitCallbacks(execute=True):
            return VideoModel.objects.create(**fields)

    def save_video(self, video, **fields):
        for field, value in fields.items():
            setattr(video, field, value)
        with self.captureOnCommitCallbacks(execute=True):
            video.save(update_fields=fields)

    def record(self, board='saolei', player=None):
        response = self.client.get(f'/api/speedranking/player/{(player or self.user).id}', {'board': board})
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_thresholds_partial_totals_and_independent_nf(self):
        beginner = self.create_video(bv=2, right_ce=None)
        record = self.record()
        self.assertEqual(record['bt_id'], beginner.id)
        self.assertIsNone(record['bb'])
        self.assertEqual(record['sumt'], 1000 + 2 * 999999)
        self.assertEqual(record['sumb'], 0)
        self.assertIsNone(self.record('saolei_nf')['bt'])
        self.create_video(bv=4, timems=2000)
        self.create_video(level='i', bv=29, timems=1000)
        self.create_video(level='e', bv=99, timems=1000)
        record = self.record()
        self.assertEqual(record['bb'], 2)
        self.assertIsNone(record['it'])
        self.assertIsNone(record['et'])
        self.assertEqual(self.record('saolei_nf')['bt'], 2000)
        self.create_video(level='i', bv=30, timems=10000)
        self.create_video(level='e', bv=100, timems=100000)
        self.assertEqual(self.record()['sumt'], 111000)
        self.assertEqual(self.record()['sumb'], 6)

    def test_upload_time_breaks_ties_not_timems(self):
        older = self.create_video(bv=8, timems=2000)
        newer = self.create_video(bv=4, timems=1000)
        self.assertEqual(self.record()['bb_id'], older.id)
        self.save_video(newer, upload_time=older.upload_time - timedelta(days=1))
        self.assertEqual(self.record()['bb_id'], newer.id)
        self.save_video(newer, upload_time=timezone.now())
        self.assertEqual(self.record()['bb_id'], older.id)
        other = self.create_user('other')
        self.create_video(player=other, bv=4, timems=1000)
        response = self.client.get('/api/speedranking/rank', {'stat': 'bb', 'start': 0, 'end': 1})
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['players'][0]['player_id'], self.user.id)

    def test_worsening_and_deletion_backfill_only_held_records(self):
        first = self.create_video(timems=1000)
        backup = self.create_video(timems=2000)
        with patch('speedranking.services.best_candidate', wraps=best_candidate) as best:
            self.save_video(backup, timems=3000)
            best.assert_not_called()
        self.save_video(first, timems=4000)
        self.assertEqual(self.record()['bt_id'], backup.id)
        self.assertEqual(self.record()['bb_id'], backup.id)
        with self.captureOnCommitCallbacks(execute=True):
            backup.delete()
        self.assertEqual(self.record()['bt_id'], first.id)
        with self.captureOnCommitCallbacks(execute=True):
            first.delete()
        self.assertIsNone(self.record()['bt'])
        self.assertEqual(self.client.get('/api/speedranking/rank').json()['count'], 0)

    def test_category_changes_and_qualification(self):
        video = self.create_video()
        other = self.create_user('newowner')
        self.save_video(video, player=other, level='e', bv=100, timems=199999, right_ce=1)
        self.assertIsNone(self.record()['bt'])
        self.assertEqual(self.record(player=other)['et_id'], video.id)
        self.assertIsNone(self.record('saolei_nf', other)['et'])
        with self.assertNumQueries(0):
            self.assertTrue(has_sub200_expert_video(other))
        for fields in ({'timems': 200000}, {'bv': 99}, {'mode': MS_TextChoices.Mode.JSW}, {'state': MS_TextChoices.State.IDENTIFIER}, {'ongoing_tournament': True}):
            with self.subTest(fields=fields):
                self.save_video(video, timems=199999, bv=100, mode='00', state=MS_TextChoices.State.OFFICIAL, ongoing_tournament=False)
                self.save_video(video, **fields)
                self.assertFalse(has_sub200_expert_video(other))

    def test_bulk_add_and_remove_rebuild_affected_records(self):
        backup = self.create_video(timems=2000)
        video = self.create_video(state=MS_TextChoices.State.IDENTIFIER)
        videos = VideoModel.objects.filter(pk=video.pk)
        with self.captureOnCommitCallbacks(execute=True):
            videos.update(state=MS_TextChoices.State.OFFICIAL)
            add_videos_to_speed_ranks(videos)
        self.assertEqual(self.record()['bt_id'], video.id)
        with self.captureOnCommitCallbacks(execute=True):
            videos.update(state=MS_TextChoices.State.IDENTIFIER)
            remove_videos_from_speed_ranks(videos)
        self.assertEqual(self.record()['bt_id'], backup.id)

    def test_rollback_does_not_write_cache(self):
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(ValueError), transaction.atomic():
                VideoModel.objects.create(player=self.user, video=ExpandVideoModel.objects.create(), file='rollback.evf', software='e', state=MS_TextChoices.State.OFFICIAL, level='b', bv=4, timems=1000)
                raise ValueError('rollback')
        self.assertIsNone(self.record()['bt'])

    def test_rebuild_replaces_stale_entries_and_api_reads_only_redis(self):
        video = self.create_video()
        SpeedRankingCache('saolei').flush()
        with self.assertNumQueries(0):
            self.assertIsNone(self.record()['bt'])
        call_command('rebuild_speed_ranks', batch_size=1, stdout=StringIO())
        self.assertEqual(self.record()['bt_id'], video.id)
        with patch('speedranking.services._add_videos', side_effect=ValueError('failed')):
            with self.assertRaises(ValueError):
                call_command('rebuild_speed_ranks', stdout=StringIO())
        self.assertEqual(self.record()['bt_id'], video.id)
        VideoModel.objects.filter(pk=video.pk).update(state=MS_TextChoices.State.IDENTIFIER)
        call_command('rebuild_speed_ranks', stdout=StringIO())
        self.assertIsNone(self.record()['bt'])
        self.assertEqual(self.client.get('/api/speedranking/rank', {'board': 'invalid'}).status_code, 422)
        self.assertEqual(self.client.get('/api/speedranking/rank', {'stat': 'invalid'}).status_code, 422)
