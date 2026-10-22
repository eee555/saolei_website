from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.tasks import TaskContext
from django.test import override_settings, SimpleTestCase, TestCase
from django_tasks_db.models import DBTaskResult

from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .cache import TopRankingCache
from .services import rebuild_soft_ranks, write_records
from .tasks import task_refresh_soft_ranks
from .utils import insert_video, MINIMUM_BV, RANK_FIELDS, ranking_score, record_field, record_mean, SOFT_FIELDS, soft_values, stat_record
from ..cache import cache, pipeline
from ..pb.cache import PBRankingCache
from ..saolei.cache import SpeedRankingCache
from ..saolei.utils import RANK_STATS, RANKING_NAMES
from ..services import add_videos_to_speed_ranks, remove_videos_from_speed_ranks


class TopSelectionTests(SimpleTestCase):
    def test_ordered_insertion_and_missing_values(self):
        for stat in ('t', 'b', 's'):
            videos = []
            for index, value in enumerate((3, 6, 1, 2, 5, 4), start=1):
                videos = insert_video(stat, videos, {'video_id': index, 'value': value})
            self.assertEqual([video['value'] for video in videos], [1, 2, 3, 4, 5] if stat == 't' else [6, 5, 4, 3, 2])
            repeated = insert_video(stat, videos, videos[0])
            self.assertEqual({video['video_id'] for video in repeated}, {video['video_id'] for video in videos})
        self.assertEqual(record_mean('t', stat_record('t', [{'value': 1000, 'video_id': 1}])), (1000 + 4 * 999999) / 5)
        self.assertEqual(record_mean('s', stat_record('s', [{'value': 2, 'video_id': 1}])), 0.4)
        records, anchors = {}, {}
        for field in RANK_FIELDS:
            value = 1000 if field.endswith('t') else 2
            records[field] = {'videos': [{'value': value, 'video_id': index} for index in range(1, 6)]}
            anchors[field] = {'value': value}
        values = soft_values(records, anchors)
        for mode in ('std', 'nf'):
            for level in MINIMUM_BV:
                self.assertAlmostEqual(values[f'{mode}:{level}'], 100)
            self.assertAlmostEqual(values[f'{mode}:sum'], 4000)
        self.assertAlmostEqual(values['lsf'], 4000)


@override_settings(RATELIMIT_ENABLE=False)
class TopRankingTests(TestCase):
    def setUp(self):
        self.ranking = TopRankingCache()
        for ranking in [self.ranking, PBRankingCache(), *[SpeedRankingCache(name, stats=RANK_STATS) for name in RANKING_NAMES]]:
            ranking.flush()
            self.addCleanup(ranking.flush)
        self.user = self.create_user('top')

    def create_user(self, username):
        return UserProfile.objects.create_user(username=username, email=f'{username}@example.com', userms=UserMS.objects.create())

    def create_video(self, **kwargs):
        fields = {'player': self.user, 'video': ExpandVideoModel.objects.create(identifier='top'), 'file': 'videos/top.evf', 'software': 'e', 'state': MS_TextChoices.State.OFFICIAL, 'level': 'b', 'mode': '00', 'bv': 10, 'timems': 1000, 'right_ce': 0}
        fields.update(kwargs)
        with self.captureOnCommitCallbacks(execute=True):
            return VideoModel.objects.create(**fields)

    def save_video(self, video, **fields):
        for field, value in fields.items():
            setattr(video, field, value)
        with self.captureOnCommitCallbacks(execute=True):
            video.save(update_fields=fields)

    def player_records(self, user=None):
        response = self.client.get(f'/api/speedranking/top/player/{(user or self.user).id}')
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_thresholds_eligibility_nf_and_iqg_contract(self):
        for level, minimum in MINIMUM_BV.items():
            self.create_video(level=level, bv=minimum - 1)
            self.assertNotIn(record_field(False, level, 's'), self.ranking.get_record(self.user.id))
            video = self.create_video(level=level, bv=minimum)
            video.refresh_from_db()
            record = self.ranking.get_record(self.user.id)
            for nf in (False, True):
                self.assertEqual(record[record_field(nf, level, 's')]['videos'][0]['value'], video.iqg)
        ordinary = self.create_video(timems=500, right_ce=1)
        for fields in ({'mode': MS_TextChoices.Mode.JSW}, {'state': MS_TextChoices.State.IDENTIFIER}, {'ongoing_tournament': True}):
            self.create_video(timems=1, **fields)
        zero = self.create_video(level='e', bv=100, timems=0, right_ce=None)
        zero.refresh_from_db()
        self.assertEqual((zero.bvs, zero.iqg), (0, 0))
        record = self.ranking.get_record(self.user.id)
        self.assertIn({'video_id': zero.id, 'value': 0}, record['std:es']['videos'])
        self.assertNotIn(zero.id, [video['video_id'] for video in record['nf:es']['videos']])
        self.assertEqual(record['std:bt']['videos'][0]['video_id'], ordinary.id)
        self.assertNotIn(ordinary.id, [video['video_id'] for video in record['nf:bt']['videos']])
        with self.assertNumQueries(0):
            summary = self.player_records()
            response = self.client.get('/api/speedranking/top/rank', {'level': 'b', 'stat': 's'})
        self.assertEqual(len(summary), 18)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['players'][0]['records'], record)
        self.assertEqual(summary, record)
        self.assertEqual(len(summary['std:bt']['videos']), 2)

    def test_five_videos_same_bv_mean_order_and_bounded_details(self):
        videos = [self.create_video(timems=value * 1000) for value in range(1, 8)]
        record = self.ranking.get_record(self.user.id)
        self.assertEqual([video['video_id'] for video in record['std:bt']['videos']], [video.id for video in videos[:5]])
        self.assertEqual(record_mean('t', record['std:bt']), 3000)
        other = self.create_user('top-single')
        self.create_video(player=other, timems=500)
        with self.assertNumQueries(0):
            response = self.client.get('/api/speedranking/top/rank', {'level': 'b', 'stat': 't', 'start': 0, 'end': 1})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['players'][0]['player_id'], self.user.id)
        self.assertEqual(len(response.json()['players'][0]['records']['std:bt']['videos']), 5)

    def test_worsening_deletion_and_player_level_nf_moves(self):
        videos = [self.create_video(timems=value * 1000) for value in range(1, 7)]
        self.save_video(videos[0], timems=7000)
        self.assertEqual(record_mean('t', self.player_records()['std:bt']), 4000)
        with self.captureOnCommitCallbacks(execute=True):
            videos[-1].delete()
        self.assertEqual(record_mean('t', self.player_records()['std:bt']), 4200)
        other = self.create_user('top-moved')
        self.save_video(videos[1], player=other, level='i', bv=30, right_ce=1)
        record = self.ranking.get_record(self.user.id)
        self.assertNotIn(videos[1].id, [video['video_id'] for video in record['std:bt']['videos']])
        moved = self.player_records(other)
        self.assertEqual(len(moved['std:it']['videos']), 1)
        self.assertNotIn('nf:it', moved)
        self.save_video(videos[1], state=MS_TextChoices.State.IDENTIFIER)
        self.assertEqual(self.player_records(other), {})

    def test_bulk_updates_rebuild_and_atomic_failure(self):
        videos = [self.create_video(timems=value * 1000, state=MS_TextChoices.State.IDENTIFIER) for value in range(1, 7)]
        queryset = VideoModel.objects.filter(pk__in=[video.pk for video in videos])
        with self.captureOnCommitCallbacks(execute=True):
            queryset.update(state=MS_TextChoices.State.OFFICIAL)
            add_videos_to_speed_ranks(queryset)
        self.assertEqual(record_mean('t', self.player_records()['std:bt']), 3000)
        removed = queryset.filter(pk__in=[video.pk for video in videos[:2]])
        with self.captureOnCommitCallbacks(execute=True):
            removed.update(ongoing_tournament=True)
            remove_videos_from_speed_ranks(removed)
        before = self.ranking.get_record(self.user.id)
        anchors = self.ranking.get_anchors()
        output = StringIO()
        call_command('rebuild_top_ranks', batch_size=1, stdout=output)
        self.assertEqual(self.ranking.get_record(self.user.id), before)
        rebuilt_anchors = self.ranking.get_anchors()
        self.assertEqual({field: rebuilt_anchors[field] for field in anchors}, anchors)
        self.assertIn('rankings and anchors published', output.getvalue())
        with patch('speedranking.top.services.prepare_add_videos', side_effect=RuntimeError('failed')), self.assertLogs('speedranking', level='ERROR'):
            with self.assertRaises(RuntimeError):
                call_command('rebuild_top_ranks', stdout=StringIO())
        self.assertEqual(self.ranking.get_record(self.user.id), before)

    def test_anchor_averages_top_twenty_original_means(self):
        previous = {player_id: {} for player_id in range(1000, 1025)}
        records = {player_id: {'std:bt': stat_record('t', [{'video_id': player_id * 10 + index, 'value': player_id - 999} for index in range(5)])} for player_id in previous}
        with pipeline() as pipe:
            affected = write_records(pipe, previous, records, self.ranking)
            pipe.execute()
        self.ranking.refresh_anchors(affected)
        with self.assertNumQueries(0):
            response = self.client.get('/api/speedranking/top/anchors')
        self.assertEqual(response.status_code, 200, response.content)
        anchors = response.json()
        self.assertEqual(set(anchors), affected)
        self.assertEqual(anchors['std:bt'], {'value': 10.5, 'sample_count': 20})

    def test_admin_repair_restores_details_score_and_anchor(self):
        video = self.create_video()
        field = 'std:bt'
        cache.zadd(self.ranking.rank_key(field), {str(self.user.id): -1})
        payload = {'player_id': self.user.id, 'level': 'b', 'stat': 't', 'nf': False}
        url = '/api/speedranking/top/admin/rebuild_record'
        self.assertEqual(self.client.post(url, payload).status_code, 403)
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.client.force_login(self.user)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['records'][field]['videos'][0]['video_id'], video.id)
        mean = record_mean('t', response.json()['records'][field])
        self.assertEqual(cache.zscore(self.ranking.rank_key(field), self.user.id), ranking_score('t', mean))
        self.assertAlmostEqual(self.ranking.get_anchors()[field]['value'], mean)

    def test_soft_union_local_updates_and_complete_membership(self):
        self.create_video(right_ce=1)
        self.assertEqual(rebuild_soft_ranks(), 1)
        other = self.create_user('soft-other')
        other_video = self.create_video(player=other, level='e', bv=100, right_ce=1, timems=2000)
        for field in RANK_FIELDS:
            self.assertEqual(cache.zcard(self.ranking.rank_key(field)), 2)
        self.assertEqual(cache.zscore(self.ranking.rank_key('nf:et'), other.id), 1 / 999999)
        publication = self.ranking.get_publication()
        expected = soft_values(self.ranking.get_record(other.id), publication['anchors'])
        for field, value in expected.items():
            self.assertAlmostEqual(cache.zscore(self.ranking.soft_key(field), other.id), value)
        self.assertEqual(rebuild_soft_ranks(), 2)
        publication = self.ranking.get_publication()
        for player in (self.user, other):
            values = soft_values(self.ranking.get_record(player.id), publication['anchors'])
            for field, value in values.items():
                self.assertAlmostEqual(cache.zscore(self.ranking.soft_key(field), player.id), value)
        with self.assertNumQueries(0):
            response = self.client.get('/api/speedranking/top/soft/rank', {'ranking': 'nf:sum'})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['players'][0]['records'], self.ranking.get_record(response.json()['players'][0]['player_id']))
        self.save_video(other_video, state=MS_TextChoices.State.IDENTIFIER)
        for key in [*[self.ranking.rank_key(field) for field in RANK_FIELDS], *[self.ranking.soft_key(field) for field in SOFT_FIELDS]]:
            self.assertIsNone(cache.zscore(key, other.id))
        self.assertTrue(self.ranking.get_record(self.user.id))
        self.assertEqual(self.ranking.get_record(other.id), {})

    def test_queued_refresh_uses_latest_anchors_and_failure_keeps_published_data(self):
        self.create_video()
        tasks = DBTaskResult.objects.filter(task_path='speedranking.top.tasks.task_refresh_soft_ranks')
        queued = tasks.first().task_result
        task_refresh_soft_ranks.enqueue()
        self.assertEqual(task_refresh_soft_ranks.call(TaskContext(task_result=queued)), {'skipped': True})
        self.assertIsNone(self.ranking.get_publication())
        tasks.exclude(pk=queued.id).delete()
        result = task_refresh_soft_ranks.call(TaskContext(task_result=queued))
        self.assertEqual(result, {'players': 1})
        published = self.ranking.get_publication()
        self.assertEqual(published['anchors'], self.ranking.get_anchors())
        before = cache.zrange(self.ranking.soft_key('lsf'), 0, -1, withscores=True)
        with patch('redis.client.Pipeline.zunionstore', side_effect=RuntimeError('failed')), self.assertLogs('speedranking', level='ERROR'):
            with self.assertRaises(RuntimeError):
                rebuild_soft_ranks()
        self.assertEqual(self.ranking.get_publication(), published)
        self.assertEqual(cache.zrange(self.ranking.soft_key('lsf'), 0, -1, withscores=True), before)
