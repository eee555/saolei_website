from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.db import transaction
from django.test import override_settings, SimpleTestCase, TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from userprofile.services import has_sub200_expert_video
from videomanager.models import ExpandVideoModel, VideoModel
from .cache import cache, SpeedRankingCache
from .services import add_videos_to_speed_ranks, best_candidate, remove_videos_from_speed_ranks
from .utils import encode_zset_score, is_better, MAX_RECORD_UNITS, RANK_STATS, RANKING_NAMES, SCORE_TIME_FACTOR, TIME_STATS, TOTAL_PARTS, upload_microseconds


class SpeedRankingScoreTests(SimpleTestCase):
    def test_score_precision_order_and_admission_boundaries(self):
        for stat in RANK_STATS:
            with self.subTest(stat=stat):
                maximum = MAX_RECORD_UNITS * (3 if stat in TOTAL_PARTS else 1)
                value = maximum if stat in TIME_STATS else maximum / 10000
                for upload in (0, SCORE_TIME_FACTOR - 1):
                    encoded = encode_zset_score(stat, value, upload * 60_000_000)
                    self.assertLess(abs(encoded), 2 ** 53)
                    self.assertEqual(int(float(encoded)), encoded)
                    self.assertEqual(float(encoded) + 1, encoded + 1)
                step = 1 if stat in TIME_STATS else 0.0001
                better, worse = (value - step, value) if stat in TIME_STATS else (value, value - step)
                self.assertLess(encode_zset_score(stat, better, (SCORE_TIME_FACTOR - 1) * 60_000_000), encode_zset_score(stat, worse, 0))
                for invalid in (-1, value + step / 10, float('inf'), float('nan')):
                    self.assertIsNone(encode_zset_score(stat, invalid, 0))
                self.assertIsNone(encode_zset_score(stat, value, SCORE_TIME_FACTOR * 60_000_000))
        self.assertEqual(encode_zset_score('bb', 1.23445, 0), -12345 * SCORE_TIME_FACTOR)
        self.assertEqual(encode_zset_score('bb', 1.23441, 1), encode_zset_score('bb', 1.23442, 2))
        self.assertTrue(is_better('bb', {'value': 1.23442, 'upload': 2}, {'bb': 1.23441, '_uploads': {'bb': 1}}))


@override_settings(RATELIMIT_ENABLE=False)
class SpeedRankingTests(TestCase):
    def setUp(self):
        for ranking_name in RANKING_NAMES:
            ranking = SpeedRankingCache(ranking_name)
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

    def record(self, ranking_name='saolei', player=None):
        response = self.client.get(f'/api/speedranking/player/{(player or self.user).id}', {'ranking_name': ranking_name})
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
        self.save_video(older, upload_time=timezone.now() - timedelta(minutes=2))
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

    def test_personal_best_keeps_upload_precision_when_redis_scores_tie(self):
        minute = timezone.now().replace(second=0, microsecond=0)
        first = self.create_video(timems=100000)
        second = self.create_video(timems=100000)
        self.save_video(first, upload_time=minute + timedelta(seconds=50))
        for fields, expected in (
            ({'upload_time': minute + timedelta(seconds=55)}, first),
            ({'upload_time': first.upload_time - timedelta(microseconds=1)}, second),
        ):
            self.save_video(second, **fields)
            expected.refresh_from_db()
            self.assertEqual(self.record()['bb'], expected.bvs)
            self.assertEqual(self.record()['sumb'], expected.bvs)
            self.assertEqual(self.record()['bb_id'], expected.id)
            self.assertEqual(best_candidate(self.user.id, 'saolei', 'bb')['id'], expected.id)
            call_command('rebuild_speed_ranks', stdout=StringIO())
            self.assertEqual(self.record()['bb_id'], expected.id)
            self.assertEqual(cache.zscore(SpeedRankingCache('saolei').rank_key('bb'), self.user.id), encode_zset_score('bb', 0.04, upload_microseconds(minute)))
        ranking = SpeedRankingCache('saolei')
        self.assertEqual(cache.zrange(ranking.rank_key('bb'), 0, -1), [str(self.user.id).encode()])

    def test_over_limit_records_stay_in_hash_and_totals_rank_independently(self):
        video = self.create_video()
        self.create_video(level='i', bv=30, timems=1000)
        for bv, timems, ranked in (
            (200, 1000, {'bt', 'sumt', 'sumb'}),
            (400, 1000, {'bt', 'sumt'}),
            (4, 1000000, {'bb', 'sumt', 'sumb'}),
            (4, 3000000, {'bb', 'sumb'}),
            (4, 999999, {'bt', 'bb', 'sumt', 'sumb'}),
        ):
            with self.subTest(bv=bv, timems=timems):
                self.save_video(video, bv=bv, timems=timems)
                video.refresh_from_db()
                for rebuild in (False, True):
                    if rebuild:
                        call_command('rebuild_speed_ranks', stdout=StringIO())
                    for ranking_name in RANKING_NAMES:
                        record = self.record(ranking_name)
                        self.assertEqual((record['bt'], record['bb']), (video.timems, video.bvs))
                        self.assertEqual((record['bt_id'], record['bb_id']), (video.id, video.id))
                        self.assertEqual(record['sumt'], video.timems + 1000 + 999999)
                        self.assertEqual(record['sumb'], video.bvs + 30)
                        for stat in ('bt', 'bb', 'sumt', 'sumb'):
                            response = self.client.get('/api/speedranking/rank', {'ranking_name': ranking_name, 'stat': stat})
                            self.assertEqual(response.status_code, 200)
                            self.assertEqual(response.json()['count'], int(stat in ranked))

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
        cache.zadd(SpeedRankingCache('saolei').rank_key('bt'), {f'00000000000000000000:{self.user.id}': 1000})
        call_command('rebuild_speed_ranks', '--ranking-name', 'saolei', batch_size=1, stdout=StringIO())
        self.assertEqual(self.record()['bt_id'], video.id)
        self.assertEqual(cache.zrange(SpeedRankingCache('saolei').rank_key('bt'), 0, -1), [str(self.user.id).encode()])
        with patch('speedranking.services._add_videos', side_effect=ValueError('failed')):
            with self.assertRaises(ValueError):
                call_command('rebuild_speed_ranks', stdout=StringIO())
        self.assertEqual(self.record()['bt_id'], video.id)
        VideoModel.objects.filter(pk=video.pk).update(state=MS_TextChoices.State.IDENTIFIER)
        call_command('rebuild_speed_ranks', stdout=StringIO())
        self.assertIsNone(self.record()['bt'])
        self.assertEqual(self.client.get('/api/speedranking/rank', {'ranking_name': 'invalid'}).status_code, 422)
        self.assertEqual(self.client.get('/api/speedranking/rank', {'stat': 'invalid'}).status_code, 422)
