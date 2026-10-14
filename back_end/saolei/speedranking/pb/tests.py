from datetime import datetime, timedelta, timezone as datetime_timezone
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import override_settings, SimpleTestCase, TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, MAX_TIMEMS, VideoModel
from .cache import PBRankingCache
from .utils import encode_score, member, record_field, record_from_score, SCORE_TIME_FACTOR, upload_time_from_score
from ..cache import cache
from ..saolei.cache import SpeedRankingCache
from ..saolei.utils import RANK_STATS, RANKING_NAMES
from ..services import add_videos_to_speed_ranks, remove_videos_from_speed_ranks, sync_video


class PBScoreTests(SimpleTestCase):
    def test_encoding_preserves_milliseconds_and_minute_order(self):
        epoch = datetime(1970, 1, 1, tzinfo=datetime_timezone.utc)
        for timems in (0, 1, MAX_TIMEMS):
            for minutes in (0, SCORE_TIME_FACTOR - 1):
                score = encode_score(timems, epoch + timedelta(minutes=minutes))
                self.assertLess(score, 2 ** 53)
                self.assertEqual(int(float(score)), score)
                self.assertEqual(record_from_score(42, float(score))['timems'], timems)
                self.assertEqual(upload_time_from_score(float(score)), epoch + timedelta(minutes=minutes))
        self.assertLess(encode_score(1, epoch + timedelta(minutes=SCORE_TIME_FACTOR - 1)), encode_score(2, epoch))
        self.assertEqual(encode_score(1, epoch), encode_score(1, epoch + timedelta(seconds=59)))


@override_settings(RATELIMIT_ENABLE=False)
class PBRankingTests(TestCase):
    def setUp(self):
        self.ranking = PBRankingCache()
        self.ranking.flush()
        self.addCleanup(self.ranking.flush)
        for name in RANKING_NAMES:
            ranking = SpeedRankingCache(name, stats=RANK_STATS)
            ranking.flush()
            self.addCleanup(ranking.flush)
        self.user = self.create_user('pb')

    def create_user(self, username):
        return UserProfile.objects.create_user(username=username, email=f'{username}@example.com', userms=UserMS.objects.create())

    def create_video(self, **kwargs):
        fields = {'player': self.user, 'video': ExpandVideoModel.objects.create(identifier='pb'), 'file': 'videos/pb.evf', 'software': 'e', 'state': MS_TextChoices.State.OFFICIAL, 'level': 'b', 'mode': '00', 'bv': 4, 'timems': 1000, 'right_ce': 0}
        fields.update(kwargs)
        with self.captureOnCommitCallbacks(execute=True):
            return VideoModel.objects.create(**fields)

    def save_video(self, video, **fields):
        for field, value in fields.items():
            setattr(video, field, value)
        with self.captureOnCommitCallbacks(execute=True):
            video.save(update_fields=fields)

    def records(self, player=None):
        response = self.client.get(f'/api/speedranking/pb/player/{(player or self.user).id}')
        self.assertEqual(response.status_code, 200, response.content)
        return {(row['nf'], row['level'], row['bv']): row for row in response.json()}

    def test_buckets_nf_eligibility_and_cached_ranks(self):
        standard = self.create_video(timems=1000, right_ce=1)
        nf = self.create_video(timems=2000)
        zero = self.create_video(bv=1, timems=0)
        for fields in ({'mode': MS_TextChoices.Mode.JSW}, {'state': MS_TextChoices.State.IDENTIFIER}, {'ongoing_tournament': True}):
            self.create_video(timems=1, **fields)
        self.create_video(level='i', bv=4)
        other = self.create_user('pb-faster')
        faster = self.create_video(player=other, timems=500)
        with self.assertNumQueries(0), patch.object(cache, 'zrank', wraps=cache.zrank) as zrank:
            records = self.records()
            zrank.assert_not_called()
        self.assertEqual((records[False, 'b', 4]['video_id'], records[False, 'b', 4]['rank']), (standard.id, 2))
        self.assertEqual((records[True, 'b', 4]['video_id'], records[True, 'b', 4]['rank']), (nf.id, 2))
        self.assertEqual(records[False, 'b', 1]['timems'], zero.timems)
        with self.assertNumQueries(0):
            response = self.client.get('/api/speedranking/pb/rank', {'level': 'b', 'bv': 4, 'start': 1, 'end': 2})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['players'][0]['video_id'], standard.id)
        self.assertEqual(datetime.fromisoformat(response.json()['players'][0]['upload_time']), standard.upload_time.replace(second=0, microsecond=0))
        self.assertEqual(self.ranking.get_counts(), {'std:b:4': 2, 'nf:b:4': 2, 'std:b:1': 1, 'nf:b:1': 1, 'std:i:4': 1, 'nf:i:4': 1})
        with self.assertNumQueries(0):
            counts_response = self.client.get('/api/speedranking/pb/counts')
        self.assertEqual(counts_response.status_code, 200, counts_response.content)
        self.assertEqual(counts_response.json(), self.ranking.get_counts())
        self.save_video(faster, timems=3000)
        self.assertEqual(self.records()[False, 'b', 4]['rank'], 1)
        self.assertEqual(self.records()[True, 'b', 4]['rank'], 1)
        expected_counts = self.ranking.get_counts()
        cache.hset(self.ranking.counts_key, mapping={'std:b:4': 999, 'nf:e:381': 999})
        output = StringIO()
        call_command('rebuild_pb_ranks', batch_size=1, stdout=output)
        self.assertEqual(self.ranking.get_counts(), expected_counts)
        self.assertIn('ranks and counts refreshed', output.getvalue())

    def test_worsening_deletion_and_category_moves(self):
        first = self.create_video()
        backup = self.create_video(timems=2000)
        self.save_video(first, timems=3000)
        self.assertEqual(self.records()[False, 'b', 4]['video_id'], backup.id)
        other = self.create_user('pb-moved')
        self.save_video(backup, player=other, level='e', bv=100, right_ce=1)
        self.assertEqual(self.records()[False, 'b', 4]['video_id'], first.id)
        self.assertEqual(self.records(other)[False, 'e', 100]['video_id'], backup.id)
        self.assertNotIn((True, 'e', 100), self.records(other))
        with self.captureOnCommitCallbacks(execute=True):
            first.delete()
        self.assertEqual(self.records(), {})
        self.assertEqual(cache.zcard(self.ranking.rank_key('std:b:4')), 0)
        self.assertEqual(self.ranking.get_counts(), {'std:b:4': 0, 'nf:b:4': 0, 'std:e:100': 1})

    def test_record_changes_refresh_only_the_affected_rank_range(self):
        players = [self.user] + [self.create_user(f'pb-range-{index}') for index in range(4)]
        videos = [self.create_video(player=player, timems=(index + 1) * 1000) for index, player in enumerate(players)]
        refresh_ranks = PBRankingCache.refresh_ranks

        def assert_refresh(action, start, end):
            with patch.object(PBRankingCache, 'refresh_ranks', autospec=True, side_effect=refresh_ranks) as refresh:
                action()
            self.assertEqual(refresh.call_count, 1)
            self.assertEqual(refresh.call_args.args[1], {'std:b:4': (start, end), 'nf:b:4': (start, end)})
            for nf in (False, True):
                rows = self.ranking.get_range(nf, 'b', 4, 0, 100)['players']
                self.assertEqual(self.ranking.get_counts()[record_field(nf, 'b', 4)], len(rows))
                for rank, row in enumerate(rows, start=1):
                    records = self.ranking.get_player_records(row['player_id'])
                    record = next(record for record in records if record['nf'] == nf)
                    self.assertEqual(record['rank'], rank)

        moved = videos[3]
        assert_refresh(lambda: self.save_video(moved, timems=2500), 2, 3)
        assert_refresh(lambda: self.save_video(moved, timems=3500), 2, 3)
        assert_refresh(lambda: self.save_video(moved, upload_time=timezone.now() + timedelta(minutes=1)), 3, 3)

        def bulk_improve():
            queryset = VideoModel.objects.filter(pk__in=[videos[1].pk, moved.pk])
            with self.captureOnCommitCallbacks(execute=True):
                queryset.update(timems=500)
                add_videos_to_speed_ranks(queryset)

        assert_refresh(bulk_improve, 0, 3)
        newcomer = self.create_user('pb-range-new')
        inserted = []
        assert_refresh(lambda: inserted.append(self.create_video(player=newcomer, timems=4500)), 4, -1)

        def remove(video):
            with self.captureOnCommitCallbacks(execute=True):
                video.delete()

        assert_refresh(lambda: remove(inserted[0]), 4, -1)
        assert_refresh(lambda: remove(videos[0]), 2, -1)
        assert_refresh(lambda: remove(videos[-1]), 3, -1)

    def test_bulk_changes_and_rebuild_use_full_upload_precision(self):
        minute = timezone.now().replace(second=0, microsecond=0)
        held = self.create_video(right_ce=1)
        earlier = self.create_video(right_ce=1, state=MS_TextChoices.State.IDENTIFIER)
        VideoModel.objects.filter(pk=held.pk).update(upload_time=minute + timedelta(seconds=50))
        VideoModel.objects.filter(pk=earlier.pk).update(upload_time=minute + timedelta(seconds=1))
        call_command('rebuild_pb_ranks', batch_size=1, stdout=StringIO())
        videos = VideoModel.objects.filter(pk=earlier.pk)
        with self.captureOnCommitCallbacks(execute=True):
            videos.update(state=MS_TextChoices.State.OFFICIAL)
            add_videos_to_speed_ranks(videos)
        self.assertEqual(self.records()[False, 'b', 4]['video_id'], held.id)
        call_command('rebuild_pb_ranks', batch_size=1, stdout=StringIO())
        self.assertEqual(self.records()[False, 'b', 4]['video_id'], earlier.id)
        with self.captureOnCommitCallbacks(execute=True):
            videos.update(state=MS_TextChoices.State.IDENTIFIER)
            remove_videos_from_speed_ranks(videos)
        self.assertEqual(self.records()[False, 'b', 4]['video_id'], held.id)
        self.ranking.flush()
        with self.assertNumQueries(0):
            self.assertEqual(self.records(), {})
            self.assertEqual(self.ranking.get_counts(), {})
        call_command('rebuild_pb_ranks', batch_size=1, stdout=StringIO())
        self.assertEqual(self.records()[False, 'b', 4]['rank'], 1)
        self.assertEqual(self.ranking.get_counts(), {'std:b:4': 1})

    def test_admin_rebuild_cleans_duplicate_members_and_refreshes_other_ranks(self):
        video = self.create_video()
        field = record_field(False, 'b', 4)
        cache.zadd(self.ranking.rank_key(field), {member(self.user.id, video.id + 1000): 0})
        payload = {'player_id': self.user.id, 'level': 'b', 'bv': 4, 'nf': False}
        url = '/api/speedranking/pb/admin/rebuild_record'
        self.assertEqual(self.client.post(url, payload).status_code, 403)
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.client.force_login(self.user)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['video_id'], video.id)
        self.assertEqual(cache.zcard(self.ranking.rank_key(field)), 1)
        self.assertEqual(self.ranking.get_counts()[field], 1)
        for invalid in ({'level': 'c'}, {'bv': 0}, {'player_id': self.user.id + 1000}):
            self.assertEqual(self.client.post(url, {**payload, **invalid}).status_code, 404 if 'player_id' in invalid else 422)
        VideoModel.objects.filter(pk=video.pk).update(state=MS_TextChoices.State.IDENTIFIER)
        self.assertIsNone(self.client.post(url, payload).json())
        self.assertNotIn((False, 'b', 4), self.records())
        self.assertEqual(self.ranking.get_counts()[field], 0)
        cache.hset(self.ranking.counts_key, field, 42)
        self.assertIsNone(self.client.post(url, payload).json())
        self.assertEqual(self.ranking.get_counts()[field], 0)

    def test_update_error_logs_context_and_preserves_exception(self):
        video = self.create_video()
        VideoModel.objects.filter(pk=video.pk).update(timems=500)
        with patch.object(PBRankingCache, 'refresh_ranks', side_effect=RuntimeError('rank failed')):
            with self.assertLogs('speedranking', level='ERROR') as logs, self.assertRaises(RuntimeError):
                with self.captureOnCommitCallbacks(execute=True):
                    sync_video(video.id, self.user.id)
        self.assertEqual(len(logs.output), 1)
        self.assertIn(str(video.id), logs.output[0])
        self.assertIn('rank failed', logs.output[0])
