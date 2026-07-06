from django.test import TestCase

from config.global_settings import DefaultRankingScores
from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .models import UserMS


class PersonalRecordSignalTests(TestCase):
    def setUp(self):
        self.userms = UserMS.objects.create()
        self.user = UserProfile.objects.create_user(
            username='player',
            email='player@example.com',
            password='password',
            userms=self.userms,
        )

    def create_video(self, *, state=MS_TextChoices.State.OFFICIAL, timems=1000):
        expand = ExpandVideoModel.objects.create(identifier='identifier', stnb=10)
        return VideoModel.objects.create(
            player=self.user,
            file='videos/test.avf',
            file_size=1,
            video=expand,
            state=state,
            software=MS_TextChoices.Software.AVF,
            level=MS_TextChoices.Level.BEGINNER,
            mode=MS_TextChoices.Mode.STD,
            timems=timems,
            bv=10,
            left=1,
            right=1,
            double=1,
            left_ce=1,
            right_ce=1,
            double_ce=1,
            path=10,
            flag=1,
            op=1,
            isl=1,
            cell0=1,
            cell1=1,
            cell2=1,
            cell3=1,
            cell4=1,
            cell5=1,
            cell6=1,
            cell7=1,
            cell8=1,
        )

    def test_create_does_not_refresh_until_follow_up_save(self):
        video = self.create_video()

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_std, DefaultRankingScores.timems)

        video.save(update_fields=['state'])

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_std, video.timems)
        self.assertEqual(self.userms.b_timems_id_std, video.video_id)

    def test_leaving_official_rebuilds_personal_record(self):
        video = self.create_video()
        video.save(update_fields=['state'])
        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_std, video.timems)

        video.state = MS_TextChoices.State.PLAIN
        video.save(update_fields=['state'])

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_std, DefaultRankingScores.timems)
        self.assertIsNone(self.userms.b_timems_id_std)
