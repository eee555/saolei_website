from datetime import datetime, timedelta, timezone
import json
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import override_settings, SimpleTestCase, TestCase
import requests

from common.services import new_video_by_file
from msuser.models import UserMS
from userprofile.models import UserProfile
from utils import ComplexEncoder
from .cache import cache, NEWEST_QUEUE_LIMIT, serialize_video_to_queue, VideoQueueCache
from .models import ExpandVideoModel, VideoModel
from .services import delete_newest_queue
from .view_utils import refresh_video
# Create your tests here.


class NewestQueueTests(SimpleTestCase):
    def setUp(self):
        self.queue = VideoQueueCache(f'test:newest_queue:{uuid4().hex}')
        self.addCleanup(cache.delete, self.queue.key)
        self.time = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)

    def video(self, video_id, *, upload_time=None, ongoing=False):
        return SimpleNamespace(id=video_id, state='c', player_id=1, upload_time=upload_time or self.time, ongoing_tournament=ongoing)

    def seed(self, videos):
        mapping = {video.id: json.dumps(serialize_video_to_queue(video), cls=ComplexEncoder) for video in videos}
        if mapping:
            cache.hset(self.queue.key, mapping=mapping)

    def ids(self):
        return {int(video_id) for video_id in cache.hkeys(self.queue.key)}

    def test_trim_keeps_at_most_1000_entries_regardless_of_age(self):
        for size in (0, NEWEST_QUEUE_LIMIT - 1, NEWEST_QUEUE_LIMIT):
            with self.subTest(size=size):
                cache.delete(self.queue.key)
                self.seed(self.video(index, upload_time=self.time - timedelta(days=30)) for index in range(1, size + 1))
                self.assertEqual(self.queue.trim(), 0)
                self.assertEqual(len(self.ids()), size)

    def test_single_add_allows_overflow_until_cleanup_and_trim_removes_oldest(self):
        self.seed(self.video(index) for index in range(1, NEWEST_QUEUE_LIMIT + 1))
        self.queue.add(self.video(NEWEST_QUEUE_LIMIT + 1, upload_time=self.time - timedelta(days=30)))
        self.queue.add(self.video(NEWEST_QUEUE_LIMIT + 2, upload_time=self.time + timedelta(seconds=1)))
        self.queue.add(self.video(NEWEST_QUEUE_LIMIT + 3, ongoing=True))
        self.assertEqual(len(self.ids()), NEWEST_QUEUE_LIMIT + 2)
        self.assertNotIn(NEWEST_QUEUE_LIMIT + 3, self.ids())
        self.assertEqual(self.queue.trim(), 2)
        self.assertEqual(self.ids(), {*range(2, NEWEST_QUEUE_LIMIT + 1), NEWEST_QUEUE_LIMIT + 2})

    def test_bulk_add_allows_overflow_and_cleanup_keeps_latest_uploads(self):
        # IDs deliberately run opposite to upload times; imports are not necessarily chronological.
        self.queue.add_bulk([
            *(self.video(index, upload_time=self.time - timedelta(seconds=index)) for index in range(1, 2501)),
            self.video(2501, upload_time=self.time + timedelta(seconds=1), ongoing=True),
        ])
        self.assertEqual(len(self.ids()), 2500)
        self.assertNotIn(2501, self.ids())
        self.assertEqual(self.queue.trim(), 1500)
        self.assertEqual(self.ids(), set(range(1, NEWEST_QUEUE_LIMIT + 1)))

    def test_update_only_changes_existing_entries_and_cleanup_uses_updated_timestamp(self):
        self.seed(self.video(index) for index in range(1, NEWEST_QUEUE_LIMIT + 2))
        changed = self.video(NEWEST_QUEUE_LIMIT + 1, upload_time=self.time - timedelta(days=30))
        self.queue.update_bulk([changed, self.video(NEWEST_QUEUE_LIMIT + 2)])
        self.assertEqual(self.ids(), set(range(1, NEWEST_QUEUE_LIMIT + 2)))
        self.assertEqual(self.queue.trim(), 1)
        self.assertEqual(self.ids(), set(range(1, NEWEST_QUEUE_LIMIT + 1)))
        self.queue.update_bulk([changed])
        self.assertEqual(self.ids(), set(range(1, NEWEST_QUEUE_LIMIT + 1)))
        kept = self.video(1)
        kept.state = 'a'
        self.queue.update_bulk([kept])
        self.assertEqual(json.loads(cache.hget(self.queue.key, kept.id))['state'], 'a')

    def test_service_and_management_command_trim_preexisting_overflow_with_numeric_id_tiebreak(self):
        with patch('videomanager.services.newest_cache', self.queue):
            for cleanup in (delete_newest_queue, lambda: call_command('delete_newest_queue', verbosity=0)):
                with self.subTest(cleanup=cleanup):
                    cache.delete(self.queue.key)
                    self.seed(self.video(index) for index in range(1, NEWEST_QUEUE_LIMIT + 2))
                    cleanup()
                    self.assertEqual(self.ids(), set(range(2, NEWEST_QUEUE_LIMIT + 2)))


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
