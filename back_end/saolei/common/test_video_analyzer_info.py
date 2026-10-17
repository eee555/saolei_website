import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import override_settings, SimpleTestCase, TestCase

from common.services import get_video_rankings
from msuser.models import UserMS
from tournament.models import Tournament
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel


class VideoAnalyzerRankingTests(SimpleTestCase):
    def speed_results(self, video_id):
        return [json.dumps({'bt_id': video_id, 'bb_id': 999}), 2, 0, None, None, None, None, None, None, None, None, None, None, None]

    def test_only_current_video_receives_cached_ranks_and_positions_are_one_based(self):
        video = SimpleNamespace(id=42, player_id=7, level='b', bv=10)
        pipe = MagicMock()
        pipe.__enter__.return_value = pipe
        pipe.execute.side_effect = [self.speed_results(video.id), [4, None]]
        with patch('common.services.SpeedRankingCache.pipeline', return_value=pipe):
            self.assertEqual(get_video_rankings(video), [
                {'ranking': 'saolei', 'stat': 'bt', 'nf': False, 'rank': 3},
                {'ranking': 'pb', 'stat': 'time', 'nf': False, 'rank': 5},
            ])
        pipe.zrank.assert_any_call('speedranking:pb:std:b:10', '7:42')

    def test_other_video_and_missing_rank_are_not_reported(self):
        video = SimpleNamespace(id=42, player_id=7, level='b', bv=10)
        pipe = MagicMock()
        pipe.__enter__.return_value = pipe
        pipe.execute.side_effect = [self.speed_results(999), [None, None]]
        with patch('common.services.SpeedRankingCache.pipeline', return_value=pipe):
            self.assertEqual(get_video_rankings(video), [])

    def test_pluck_rank_checks_the_cached_video_id(self):
        video = SimpleNamespace(id=42, player_id=7, level='c8_8_40', bv=24)
        speed_pipe = MagicMock()
        speed_pipe.__enter__.return_value = speed_pipe
        speed_pipe.execute.return_value = [None] * 14
        pluck_pipe = MagicMock()
        pluck_pipe.__enter__.return_value = pluck_pipe
        pluck = MagicMock()
        pluck.client.pipeline.return_value = pluck_pipe
        with patch('common.services.SpeedRankingCache.pipeline', return_value=speed_pipe), patch('common.services.PLuckRankingCache', return_value=pluck):
            for cached_id in (42, 999):
                pluck_pipe.execute.return_value = [0, json.dumps({'video_id': cached_id})]
                expected = [{'ranking': 'pluck', 'stat': 'pluck', 'nf': False, 'rank': 1}] if cached_id == video.id else []
                self.assertEqual(get_video_rankings(video), expected)


@override_settings(RATELIMIT_ENABLE=False)
class VideoAnalyzerInfoTests(TestCase):
    def setUp(self):
        self.player = UserProfile.objects.create_user(username='analyzer-player', email='analyzer@example.com', userms=UserMS.objects.create())
        self.video = VideoModel.objects.create(
            player=self.player, video=ExpandVideoModel.objects.create(identifier='analyzer'),
            file='videos/20261012/原始录像.evf', software='e', level='b', mode='00', bv=10, timems=1500,
        )
        self.url = f'/api/common/video/{self.video.id}/analyzer-info'
        self.rankings = patch('common.api.get_video_rankings', return_value=[])
        self.mock_rankings = self.rankings.start()
        self.addCleanup(self.rankings.stop)

    def test_returns_full_models_original_filename_and_all_tournament_ids(self):
        first = Tournament.objects.create()
        second = Tournament.objects.create()
        first.videos.add(self.video)
        second.videos.add(self.video)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertEqual(data['filename'], '原始录像.evf')
        self.assertEqual(data['video']['player'], self.player.id)
        self.assertEqual(data['tournament_ids'], [first.id, second.id])
        self.assertEqual(data['rankings'], [])
        self.assertEqual(set(data['video']), {field.name for field in VideoModel._meta.fields})
        self.assertEqual(set(data['expanded_video']), {field.name for field in ExpandVideoModel._meta.fields})
        self.assertEqual(data['expanded_video']['identifier'], 'analyzer')
        self.assertIsNone(data['video']['cl'])
        self.mock_rankings.assert_called_once()

    def test_missing_video_is_404(self):
        response = self.client.get('/api/common/video/999999999/analyzer-info')
        self.assertEqual(response.status_code, 404)
        self.mock_rankings.assert_not_called()

    def test_hidden_tournament_video_is_only_available_to_owner(self):
        VideoModel.objects.filter(pk=self.video.pk).update(ongoing_tournament=True)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.mock_rankings.assert_not_called()
        other = UserProfile.objects.create_user(username='analyzer-other', email='other@example.com', userms=UserMS.objects.create())
        self.client.force_login(other)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.client.force_login(self.player)
        self.assertEqual(self.client.get(self.url).status_code, 200)
