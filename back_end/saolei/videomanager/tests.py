from datetime import datetime, timezone
import json
from unittest.mock import call, patch

from django.core.files.base import ContentFile
from django.test import override_settings, SimpleTestCase, TestCase
import requests

from common.utils import new_video_by_file
from msuser.models import UserMS
from userprofile.models import UserProfile
from .models import ExpandVideoModel, VideoModel
from .services import delete_newest_queue
from .view_utils import refresh_video
# Create your tests here.


class DeleteNewestQueueTests(SimpleTestCase):
    def setUp(self):
        cache_patch = patch('videomanager.services.cache')
        self.cache = cache_patch.start()
        self.addCleanup(cache_patch.stop)
        datetime_patch = patch('videomanager.services.datetime', wraps=datetime)
        self.mock_datetime = datetime_patch.start()
        self.addCleanup(datetime_patch.stop)
        self.mock_datetime.now.return_value = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)

    def set_queue(self, times):
        queue = {
            str(index).encode(): json.dumps({'time': time_str}).encode()
            for index, time_str in enumerate(times)
        }
        self.cache.hlen.return_value = len(queue)
        self.cache.hgetall.return_value = queue
        return queue

    def test_skips_queues_with_at_most_100_entries(self):
        for size in (0, 99, 100):
            with self.subTest(size=size):
                self.cache.reset_mock()
                self.set_queue(['2026-09-01T12:00:00Z'] * size)

                delete_newest_queue()

                self.cache.hgetall.assert_not_called()
                self.cache.hdel.assert_not_called()

    def test_deletes_only_entries_strictly_older_than_seven_days(self):
        self.set_queue([
            '2026-09-14T11:59:59Z',
            '2026-09-14T12:00:00Z',
            '2026-09-14T12:00:01Z',
            *['2026-09-21T12:00:00Z'] * 98,
        ])

        delete_newest_queue()

        self.cache.hlen.assert_called_once_with('newest_queue')
        self.cache.hgetall.assert_called_once_with('newest_queue')
        self.cache.hdel.assert_called_once_with('newest_queue', b'0')

    def test_keeps_large_queue_without_expired_entries(self):
        self.set_queue(['2026-09-21T12:00:00Z'] * 101)

        delete_newest_queue()

        self.cache.hdel.assert_not_called()

    def test_deletes_all_expired_entries_even_if_fewer_than_100_remain(self):
        queue = self.set_queue(['2026-09-01T12:00:00Z'] * 101)
        self.cache.hlen.side_effect = lambda key: len(queue)
        self.cache.hgetall.side_effect = lambda key: queue.copy()
        self.cache.hdel.side_effect = lambda key, field: queue.pop(field)
        expected_calls = [call('newest_queue', key) for key in queue]

        delete_newest_queue()

        self.assertCountEqual(self.cache.hdel.call_args_list, expected_calls)
        self.assertEqual(queue, {})


class VideoManagerTestCase(TestCase):
    def setUp(self):
        self.userms = UserMS.objects.create()
        self.user = UserProfile.objects.create(
            username='setUp', email='setUp@test.com', userms=self.userms)

        try:
            self.testfile_exp = requests.get(
                'https://github.com/putianyi889/replays/raw/refs/heads/master/EXP/sub40/Exp_FL_35.09_3BV=132_3BVs=3.76_Pu%20Tian%20Yi(Hu%20Bei).avf',
            )
        except Exception:
            self.testfile_exp = requests.get(
                'http://saolei.wang/Video/Mvf/9952/Pu%20Tian%20Yi_Exp_36.09(3bv132).avf',
            )
        self.testfile_exp_values = {
            'end_time': datetime(2023, 10, 5, 21, 25, 57, 244000, tzinfo=timezone.utc),
            'software': 'a', 'level': 'e', 'mode': '00',
            'timems': 35090, 'bv': 132,
            'left': 95, 'right': 20, 'double': 43,
            'left_ce': 90, 'right_ce': 20, 'double_ce': 27,
            'path': 5960.945576017859, 'flag': 20,
            'op': 11, 'isl': 11,
            'cell0': 90, 'cell1': 118, 'cell2': 103,
            'cell3': 45, 'cell4': 24, 'cell5': 1,
            'cell6': 0, 'cell7': 0, 'cell8': 0,
        }
        self.testfile_exp_values_extended = {
            'identifier': 'Pu Tian Yi(Hu Bei)',
            'tournament_identifier': [],
        }

    def multiple_values_test(self, obj, expected_values):
        for field, expected_value in expected_values.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(obj, field), expected_value)

    def test_zero_time(self):
        expandvideo = ExpandVideoModel.objects.create(
            identifier='test')
        video = VideoModel.objects.create(player=self.user, file='test.evf', video=expandvideo, state='a', software='e', level='b', mode='00', timems=0, bv=1, left=1, right=0,
                                          double=0, path=0, flag=0, left_ce=1, right_ce=0, double_ce=0, op=1, isl=0, cell0=0, cell1=0, cell2=0, cell3=0, cell4=0, cell5=0, cell6=0, cell7=0, cell8=0)

        expected_values = {
            'software': 'e', 'level': 'b', 'mode': '00',
            'timems': 0, 'bv': 1,
            'left': 1, 'right': 0, 'double': 0,
            'left_ce': 1, 'right_ce': 0, 'double_ce': 0,
            'path': 0, 'flag': 0,
            'op': 1, 'isl': 0,
            'cell0': 0, 'cell1': 0, 'cell2': 0,
            'cell3': 0, 'cell4': 0, 'cell5': 0,
            'cell6': 0, 'cell7': 0, 'cell8': 0,

            'bvs': 0, 'cl': 1, 'ce': 1,
            'cl_s': 0, 'ce_s': 0, 'flag_s': 0,
            'ioe': 1, 'thrp': 1, 'corr': 1,
        }

        self.multiple_values_test(video, expected_values)
        self.assertEqual(video.stnb, 0)

    @override_settings(BAIDU_VERIFY_SKIP=True)
    def test_new_video_by_file(self):
        video = new_video_by_file(self.user, ContentFile(
            self.testfile_exp.content, name='Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf'))
        self.multiple_values_test(video, self.testfile_exp_values)
        self.multiple_values_test(video.video, self.testfile_exp_values_extended)
        self.assertAlmostEqual(video.stnb, 135.59743119854784)
        video.delete()

    def test_refresh(self):
        expandvideo = ExpandVideoModel.objects.create(
            identifier='test')
        video = VideoModel.objects.create(player=self.user, file=ContentFile(
            self.testfile_exp.content, name='Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf'), video=expandvideo, state='a')
        refresh_video(video)

        video = VideoModel.objects.get(id=video.id)
        self.multiple_values_test(video, self.testfile_exp_values)
        self.multiple_values_test(video.video, self.testfile_exp_values_extended)
        self.assertAlmostEqual(video.stnb, 135.59743119854784)
        video.delete()

    def test_stnb_depends_on_standard_level(self):
        expandvideo = ExpandVideoModel.objects.create(identifier='test')
        video = VideoModel.objects.create(player=self.user, file='test.evf', video=expandvideo, state='a', software='e', level='b', mode='00', timems=1000, bv=10, left=1, right=0,
                                          double=0, path=0, flag=0, left_ce=1, right_ce=0, double_ce=0, op=1, isl=0, cell0=0, cell1=0, cell2=0, cell3=0, cell4=0, cell5=0, cell6=0, cell7=0, cell8=0)

        self.assertAlmostEqual(video.iqg, 10)
        self.assertAlmostEqual(video.stnb, 360)

        video.level = 'i'
        self.assertAlmostEqual(video.stnb, 1620)

        video.level = 'e'
        self.assertAlmostEqual(video.stnb, 4350)

        video.level = 'c8_8_40'
        self.assertIsNone(video.stnb)
