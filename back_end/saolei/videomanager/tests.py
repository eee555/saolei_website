from datetime import datetime, timezone

from django.core.files.base import ContentFile
from django.test import override_settings, TestCase
import requests

from accountlink.models import AccountSaolei
from userprofile.models import UserProfile
from .models import ExpandVideoModel, VideoModel
from .view_utils import new_video_by_file, refresh_video, video_saolei_import_by_userid_helper
# Create your tests here.


class VideoManagerTestCase(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            username='setUp', email='setUp@test.com')

        try:
            self.testfile_exp = requests.get(
                'https://github.com/putianyi889/replays/raw/refs/heads/master/EXP/sub40/Exp_FL_35.09_3BV=132_3BVs=3.76_Pu%20Tian%20Yi(Hu%20Bei).avf',
            )
        except:
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
            'stnb': 135.59774291678048,
        }

    def multiple_values_test(self, obj, expected_values):
        for field, expected_value in expected_values.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(obj, field), expected_value)

    def test_zero_time(self):
        expandvideo = ExpandVideoModel.objects.create(
            identifier='test', stnb=0)
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

    @override_settings(BAIDU_VERIFY_SKIP=True)
    def test_new_video_by_file(self):
        video = new_video_by_file(self.user, ContentFile(
            self.testfile_exp.content, name='Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf'))
        self.multiple_values_test(video, self.testfile_exp_values)
        self.multiple_values_test(video.video, self.testfile_exp_values_extended)
        video.delete()

    def test_refresh(self):
        expandvideo = ExpandVideoModel.objects.create(
            identifier='test', stnb=0)
        video = VideoModel.objects.create(player=self.user, file=ContentFile(
            self.testfile_exp.content, name='Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf'), video=expandvideo, state='a')
        refresh_video(video)

        video = VideoModel.objects.get(id=video.id)
        self.multiple_values_test(video, self.testfile_exp_values)
        self.multiple_values_test(video.video, self.testfile_exp_values_extended)
        video.delete()

    def test_video_saolei_import_by_userid(self):
        accountSaolei = AccountSaolei.objects.create(
            id=23756, parent=self.user)
        video_saolei_import_by_userid_helper(
            userProfile=self.user, accountSaolei=accountSaolei)
        video_saolei_import_by_userid_helper(
            userProfile=self.user, accountSaolei=accountSaolei)
        videos = list(VideoModel.objects.filter(player=self.user))
        self.assertEqual(len(videos), 13)
        self.assertEqual(videos[0].upload_time, datetime(2023, 8, 18, 16, 47, tzinfo=timezone.utc))
