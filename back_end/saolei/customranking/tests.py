from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel

from .cache import PLuckRankingCache, cache_to_dict, record_to_member
from .models import CustomPluckRecord
from .services import get_pluck_rank_range


LEVEL = MS_TextChoices.Level.CUSTOM_8_8_40


class CustomRankingTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)
        self.players = []
        for index in range(5):
            self.players.append(UserProfile.objects.create_user(
                username=f'player_{index}',
                email=f'player_{index}@example.com',
                password='password',
            ))
        self.cache = PLuckRankingCache(LEVEL)
        self.cache.flush()

    def tearDown(self):
        self.cache.flush()

    def create_video(self, player, *, pluck: float, timems: int, seconds: int = 0, mode=MS_TextChoices.Mode.STD):
        expand = ExpandVideoModel.objects.create(identifier=f'id-{player.id}-{timems}', stnb=0)
        video = VideoModel.objects.create(
            player=player,
            file=f'videos/test-{player.id}-{timems}.avf',
            file_size=1,
            video=expand,
            state=MS_TextChoices.State.PLAIN,
            software=MS_TextChoices.Software.AVF,
            level=LEVEL,
            mode=mode,
            timems=timems,
            bv=40,
            pluck=pluck,
        )
        upload_time = self.now + timedelta(seconds=seconds)
        VideoModel.objects.filter(id=video.id).update(upload_time=upload_time)
        video.refresh_from_db()
        return video

    def create_record(self, player, *, pluck: float, timems: int, seconds: int = 0):
        video = self.create_video(player, pluck=pluck, timems=timems, seconds=seconds)
        return CustomPluckRecord.objects.create(
            player=player,
            video=video,
            level=LEVEL,
            pluck=pluck,
            timems=timems,
            upload_time=video.upload_time,
        )


class CustomPluckRecordTests(CustomRankingTestCase):
    def test_add_video_uses_cached_timems_and_upload_time(self):
        original_video = self.create_video(self.players[0], pluck=10, timems=1000, seconds=10)
        worse_pluck = self.create_video(self.players[0], pluck=11, timems=1, seconds=1)
        same_pluck_slower = self.create_video(self.players[0], pluck=10, timems=1001, seconds=1)
        same_pluck_faster = self.create_video(self.players[0], pluck=10, timems=999, seconds=20)
        record = CustomPluckRecord.objects.create(
            player=self.players[0],
            video=original_video,
            level=LEVEL,
            pluck=original_video.pluck,
            timems=original_video.timems,
            upload_time=original_video.upload_time,
        )

        self.assertFalse(record.add_video(worse_pluck))
        self.assertEqual(record.video_id, original_video.id)

        self.assertFalse(record.add_video(same_pluck_slower))

        self.assertTrue(record.add_video(same_pluck_faster))
        record.refresh_from_db()
        self.assertEqual(record.video_id, same_pluck_faster.id)
        self.assertEqual(record.timems, same_pluck_faster.timems)
        self.assertEqual(record.upload_time, same_pluck_faster.upload_time)


class PLuckRankingCacheTests(CustomRankingTestCase):
    def test_record_member_uses_player_id_and_cache_range_returns_rank_dicts(self):
        record = self.create_record(self.players[0], pluck=2.5, timems=1234, seconds=3)
        member = record_to_member(record)

        self.assertTrue(member.endswith(f':{record.player_id}'))
        self.assertNotIn(f':{record.video_id}', member)

        self.cache.add_record(record)
        self.assertEqual(len(self.cache), 1)
        rows = self.cache.get_rank_range(0, 1)

        self.assertEqual(rows[0]['player_id'], record.player_id)
        self.assertEqual(rows[0]['video_id'], record.video_id)
        self.assertEqual(rows[0]['pluck'], record.pluck)
        self.assertEqual(rows[0]['timems'], record.timems)

    def test_clamp_truncates_rank_detail_and_player_indexes(self):
        records = [
            self.create_record(self.players[0], pluck=1, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=2, timems=1000, seconds=0),
            self.create_record(self.players[2], pluck=3, timems=1000, seconds=0),
        ]
        ranking_cache = PLuckRankingCache(LEVEL).open()
        ranking_cache.add_record_batch(records)
        ranking_cache.close()

        self.cache.clamp(2)

        self.assertEqual(len(self.cache), 2)
        self.assertIsNotNone(self.cache.get_member(records[0].player_id))
        self.assertIsNotNone(self.cache.get_member(records[1].player_id))
        self.assertIsNone(self.cache.get_member(records[2].player_id))
        self.assertEqual([row['player_id'] for row in self.cache.get_rank_range(0, 2)], [
            records[0].player_id,
            records[1].player_id,
        ])

    def test_cache_to_dict_decodes_player_id_from_member_and_video_id_from_detail(self):
        record = self.create_record(self.players[0], pluck=1.5, timems=1000, seconds=0)
        data = cache_to_dict(record_to_member(record), record.pluck, {
            'video_id': record.video_id,
            'mode': record.video.mode,
            'bv': record.video.bv,
        })

        self.assertEqual(data['player_id'], record.player_id)
        self.assertEqual(data['video_id'], record.video_id)


class PluckRankingServiceTests(CustomRankingTestCase):
    def test_get_pluck_rank_range_uses_database_for_range_beyond_cache(self):
        records = [
            self.create_record(self.players[0], pluck=1, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=2, timems=1000, seconds=0),
            self.create_record(self.players[2], pluck=3, timems=1000, seconds=0),
        ]
        self.cache.add_record(records[0])

        rows = get_pluck_rank_range(LEVEL, 0, 3)

        self.assertEqual([row['player_id'] for row in rows], [
            records[0].player_id,
            records[1].player_id,
            records[2].player_id,
        ])

    def test_get_pluck_rank_range_can_start_outside_cache(self):
        records = [
            self.create_record(self.players[0], pluck=1, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=2, timems=1000, seconds=0),
            self.create_record(self.players[2], pluck=3, timems=1000, seconds=0),
        ]
        self.cache.add_record(records[0])

        rows = get_pluck_rank_range(LEVEL, 1, 3)

        self.assertEqual([row['player_id'] for row in rows], [
            records[1].player_id,
            records[2].player_id,
        ])
