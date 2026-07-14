import json

from django.test import TestCase
from django_redis import get_redis_connection

from config.global_settings import DefaultRankingScores
from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .models import UserMS
from .signals import get_stats_update_set
from .utils import RankingField, RankingValue


class PersonalRecordSignalTests(TestCase):
    def setUp(self):
        self.cache = get_redis_connection('saolei_website')
        self.cache.delete('news_queue')
        self.userms = UserMS.objects.create()
        self.user = UserProfile.objects.create_user(
            username='player',
            email='player@example.com',
            password='password',
            userms=self.userms,
        )

    def test_ranking_field_constructs_from_record_name(self):
        ranking_field = RankingField('b_timems_std')

        self.assertEqual(ranking_field.level, 'b')
        self.assertEqual(ranking_field.stat, 'timems')
        self.assertEqual(ranking_field.mode, 'std')
        self.assertEqual(ranking_field.name, 'b_timems_std')
        self.assertEqual(ranking_field.id_name, 'b_timems_id_std')

    def test_ranking_field_constructs_from_record_id_name(self):
        ranking_field = RankingField('e_stnb_id_nf')

        self.assertEqual(ranking_field.level, 'e')
        self.assertEqual(ranking_field.stat, 'stnb')
        self.assertEqual(ranking_field.mode, 'nf')
        self.assertEqual(ranking_field.name, 'e_stnb_nf')
        self.assertEqual(ranking_field.id_name, 'e_stnb_id_nf')

    def test_userms_gets_and_sets_record_by_ranking_field(self):
        ranking_field = RankingField('b_timems_std')

        self.userms.set_record(ranking_field, RankingValue(1234, 56))

        self.assertEqual(self.userms.b_timems_std, 1234)
        self.assertEqual(self.userms.b_timems_id_std, 56)
        self.assertEqual(self.userms.get_record(ranking_field), RankingValue(1234, 56))

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

    def test_personal_record_update_pushes_news_queue_from_userms_signal(self):
        UserMS.objects.filter(pk=self.userms.pk).update(e_timems_std=50000)

        video = self.create_video()

        news_items = [json.loads(item) for item in self.cache.zrevrange('news_queue', 0, -1)]
        self.assertTrue(any(
            item['video_id'] == video.id
            and item['index'] == 'timems'
            and item['mode'] == 'std'
            and item['level'] == MS_TextChoices.Level.BEGINNER
            and item['old_value'] is None
            and 'delta' not in item
            for item in news_items
        ))

    def test_news_queue_old_timems_value_uses_display_unit(self):
        UserMS.objects.filter(pk=self.userms.pk).update(e_timems_std=50000)
        self.create_video(timems=2000)
        self.cache.delete('news_queue')

        video = self.create_video(timems=1000)

        news_items = [json.loads(item) for item in self.cache.zrevrange('news_queue', 0, -1)]
        self.assertTrue(any(
            item['video_id'] == video.id
            and item['index'] == 'timems'
            and item['level'] == MS_TextChoices.Level.BEGINNER
            and item['old_value'] == 2000
            for item in news_items
        ))

    def test_news_queue_skips_incomplete_record_update_fields(self):
        UserMS.objects.filter(pk=self.userms.pk).update(e_timems_std=50000)
        self.create_video(timems=2000)
        self.cache.delete('news_queue')
        self.userms.refresh_from_db()

        self.userms.b_timems_std = 1000
        self.userms.save(update_fields=['b_timems_std'])

        self.assertEqual(self.cache.zcard('news_queue'), 0)

    def test_rebuild_personal_record_does_not_push_news_queue(self):
        fast_video = self.create_video(timems=1000)
        self.create_video(timems=2000)
        self.cache.delete('news_queue')

        fast_video.delete()

        self.assertEqual(self.cache.zcard('news_queue'), 0)

    def test_news_queue_keeps_latest_200_items(self):
        for i in range(205):
            self.cache.zadd('news_queue', {json.dumps({'time': i}): i})
            news_count = self.cache.zcard('news_queue')
            if news_count > 200:
                self.cache.zremrangebyrank('news_queue', 0, news_count - 201)

        self.assertEqual(self.cache.zcard('news_queue'), 200)
        self.assertEqual(json.loads(self.cache.zrange('news_queue', 0, 0)[0])['time'], 5)

    def test_create_updates_video_count(self):
        self.create_video()

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.video_num_total, 1)
        self.assertEqual(self.userms.video_num_beg, 1)
        self.assertEqual(self.userms.video_num_std, 1)

    def test_frozen_video_updates_video_count(self):
        self.create_video(state=MS_TextChoices.State.FROZEN)

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.video_num_total, 1)
        self.assertEqual(self.userms.video_num_beg, 1)
        self.assertEqual(self.userms.video_num_std, 1)

    def test_state_to_official_does_not_update_video_count_again(self):
        video = self.create_video(state=MS_TextChoices.State.FROZEN)

        video.state = MS_TextChoices.State.OFFICIAL
        video.save(update_fields=['state'])

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.video_num_total, 1)
        self.assertEqual(self.userms.video_num_beg, 1)
        self.assertEqual(self.userms.video_num_std, 1)

    def test_delete_video_decrements_video_count(self):
        video = self.create_video()

        video.delete()

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.video_num_total, 0)
        self.assertEqual(self.userms.video_num_beg, 0)
        self.assertEqual(self.userms.video_num_std, 0)

    def test_expert_std_official_video_expands_video_count_limit(self):
        self.create_video(level=MS_TextChoices.Level.EXPERT, timems=59000)

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.video_num_limit, 3000)

    def test_delete_video_does_not_reduce_video_count_limit(self):
        video = self.create_video(level=MS_TextChoices.Level.EXPERT, timems=59000)

        video.delete()

        self.userms.refresh_from_db()
        self.assertEqual(self.userms.video_num_limit, 3000)

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
