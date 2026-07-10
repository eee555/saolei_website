from django.test import TestCase

from config.global_settings import DefaultRankingScores
from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .models import UserMS
from .signals import get_stats_update_set


class PersonalRecordSignalTests(TestCase):
    def setUp(self):
        self.userms = UserMS.objects.create()
        self.user = UserProfile.objects.create_user(
            username='player',
            email='player@example.com',
            password='password',
            userms=self.userms,
        )

    def create_video(self, *, state=MS_TextChoices.State.OFFICIAL, level=MS_TextChoices.Level.BEGINNER, timems=1000, bv=10):
        expand = ExpandVideoModel.objects.create(identifier='identifier')
        return VideoModel.objects.create(
            player=self.user,
            file='videos/test.avf',
            file_size=1,
            video=expand,
            state=state,
            software=MS_TextChoices.Software.AVF,
            level=level,
            mode=MS_TextChoices.Mode.STD,
            timems=timems,
            bv=bv,
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

    def test_create_refreshes_personal_record(self):
        video = self.create_video()

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_std, video.timems)
        self.assertEqual(self.userms.b_timems_id_std, video.id)
        self.assertAlmostEqual(self.userms.b_stnb_std, video.stnb)
        self.assertEqual(self.userms.b_stnb_id_std, video.id)

    def test_leaving_official_rebuilds_personal_record(self):
        video = self.create_video()
        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_std, video.timems)

        video.state = MS_TextChoices.State.PLAIN
        video.save(update_fields=['state'])

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_std, DefaultRankingScores.timems)
        self.assertIsNone(self.userms.b_timems_id_std)

    def test_get_stats_update_set_returns_only_affected_records(self):
        video = self.create_video(timems=1000)
        old_values = {'timems': video.timems}

        video._skip_msuser_ranking_signal = True
        video.timems = 2000
        video.save(update_fields=['timems'])
        video = VideoModel.objects.select_related('player__userms', 'video').get(pk=video.pk)

        better_stats, worse_stats = get_stats_update_set(video, old_values)
        self.assertEqual(better_stats, set())
        self.assertEqual(worse_stats, {'timems', 'bvs', 'stnb', 'ioe', 'path'})

    def test_delete_rebuilds_only_records_held_by_deleted_video(self):
        fast_video = self.create_video(timems=1000)
        slow_video = self.create_video(timems=2000)
        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_id_std, fast_video.id)

        fast_video.delete()

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_timems_std, slow_video.timems)
        self.assertEqual(self.userms.b_timems_id_std, slow_video.id)

    def test_custom_level_does_not_refresh_stnb_record(self):
        video = self.create_video(level=MS_TextChoices.Level.CUSTOM_8_8_40)

        self.assertIsNone(video.stnb)
        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_stnb_std, DefaultRankingScores.stnb)
        self.assertIsNone(self.userms.b_stnb_id_std)

    def test_bv_update_refreshes_stnb_record(self):
        video = self.create_video(bv=10, timems=1000)
        self.userms.refresh_from_db()
        self.assertAlmostEqual(self.userms.b_stnb_std, 360)

        video.bv = 20
        video.save(update_fields=['bv'])

        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertAlmostEqual(self.userms.b_stnb_std, video.stnb)
        self.assertAlmostEqual(self.userms.b_stnb_std, 720)
        self.assertEqual(self.userms.b_stnb_id_std, video.id)

    def test_timems_update_refreshes_stnb_record(self):
        video = self.create_video(bv=10, timems=2000)
        self.userms.refresh_from_db()
        old_stnb = self.userms.b_stnb_std

        video.timems = 1000
        video.save(update_fields=['timems'])

        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertGreater(self.userms.b_stnb_std, old_stnb)
        self.assertAlmostEqual(self.userms.b_stnb_std, video.stnb)
        self.assertEqual(self.userms.b_stnb_id_std, video.id)

    def test_level_change_rebuilds_old_category_and_updates_new_category_stnb(self):
        video = self.create_video(level=MS_TextChoices.Level.BEGINNER, bv=10, timems=1000)
        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_stnb_id_std, video.id)

        video.level = MS_TextChoices.Level.INTERMEDIATE
        video.save(update_fields=['level'])

        video.refresh_from_db()
        self.userms.refresh_from_db()
        self.assertEqual(self.userms.b_stnb_std, DefaultRankingScores.stnb)
        self.assertIsNone(self.userms.b_stnb_id_std)
        self.assertAlmostEqual(self.userms.i_stnb_std, video.stnb)
        self.assertEqual(self.userms.i_stnb_id_std, video.id)
