import datetime
from django.test import TestCase
from django.core.files.base import ContentFile
from userprofile.models import UserProfile
from accountlink.models import AccountSaolei
from .models import VideoModel, ExpandVideoModel
import requests
from .view_utils import refresh_video, video_saolei_import_by_userid_helper
from config.text_choices import MS_TextChoices
# Create your tests here.


class VideoManagerTestCase(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(
            username='setUp', email='setUp@test.com')

    def multiple_values_test(self, object, expected_values):
        for field, expected_value in expected_values.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(object, field), expected_value)

    def test_zero_time(self):
        expandvideo = ExpandVideoModel.objects.create(
            identifier='test', stnb=0, rqp=0)
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

    def test_refresh(self):
        response = requests.get(
            'https://github.com/putianyi889/replays/raw/refs/heads/master/EXP/sub40/Exp_FL_35.09_3BV=132_3BVs=3.76_Pu%20Tian%20Yi(Hu%20Bei).avf')
        expandvideo = ExpandVideoModel.objects.create(
            identifier='test', stnb=0, rqp=0)
        video = VideoModel.objects.create(player=self.user, file=ContentFile(
            response.content, name='Exp_FL_35.09_3BV=132_3BVs=3.76_Pu Tian Yi(Hu Bei).avf'), video=expandvideo, state='a')
        refresh_video(video)

        video = VideoModel.objects.get(id=video.id)

        expected_values = {
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

        self.multiple_values_test(video, expected_values)

        expected_extended_values = {
            'identifier': 'Pu Tian Yi(Hu Bei)',
            'stnb': 135.59774291678048,
            'rqp': 9.328091666666667,
        }

        self.multiple_values_test(video.video, expected_extended_values)

    def test_video_saolei_import_by_userid(self):
        accountSaolei = AccountSaolei.objects.create(
            id=23756, parent=self.user)
        info = video_saolei_import_by_userid_helper(
            userProfile=self.user, accountSaolei=accountSaolei, beginTime=datetime.datetime.min, endTime=datetime.datetime.max)
        if info:
            model = VideoModel.objects.filter(url_web=info.showUrl).first()
            # 断言非空
            self.assertIsNotNone(model)
            self.assertEqual(model.level, info.level[0].lower())
            self.assertEqual(model.mode, (MS_TextChoices.Mode.STD,
                             MS_TextChoices.Mode.NF)[info.mode])
            self.assertEqual(model.timems, info.grade * 1000)
            self.assertEqual(model.bv, info.bv)
            self.assertEqual(model.url_web, info.showUrl)
            self.assertEqual(model.url_file, info.url)
        video_saolei_import_by_userid_helper(
            userProfile=self.user, accountSaolei=accountSaolei, beginTime=datetime.datetime.min, endTime=datetime.datetime.max)
        videos = VideoModel.objects.filter(player=self.user).values_list()
        self.assertEqual(len(videos), len(set(videos)))
