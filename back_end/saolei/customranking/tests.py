from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, MAX_TIMEMS, VideoModel
from .cache import cache_to_dict, get_player_pluck_records, PLuckRankingCache, record_to_score
from .models import CustomPluckRecord
from .services import refresh_all_custom_pluck_ranks, refresh_custom_pluck_rank_range, update_custom_pluck_top_cache


LEVEL = MS_TextChoices.Level.CUSTOM_8_8_40
SECOND_LEVEL = MS_TextChoices.Level.CUSTOM_16_16_100


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
        PLuckRankingCache(SECOND_LEVEL).flush()

    def tearDown(self):
        self.cache.flush()
        PLuckRankingCache(SECOND_LEVEL).flush()

    def create_video(
        self,
        player,
        *,
        pluck: float,
        timems: int,
        seconds: int = 0,
        level=LEVEL,
        mode=MS_TextChoices.Mode.STD,
        state=MS_TextChoices.State.PLAIN,
    ):
        expand = ExpandVideoModel.objects.create(identifier=f'id-{player.id}-{level}-{timems}')
        video = VideoModel.objects.create(
            player=player,
            file=f'videos/test-{player.id}-{level}-{timems}.avf',
            file_size=1,
            video=expand,
            state=MS_TextChoices.State.PLAIN,
            software=MS_TextChoices.Software.AVF,
            level=level,
            mode=mode,
            timems=timems,
            bv=40,
            pluck=pluck,
        )
        upload_time = self.now + timedelta(seconds=seconds)
        VideoModel.objects.filter(id=video.id).update(upload_time=upload_time, state=state)
        video.refresh_from_db()
        return video

    def create_record(self, player, *, pluck: float, timems: int, seconds: int = 0, level=LEVEL):
        video = self.create_video(player, pluck=pluck, timems=timems, seconds=seconds, level=level)
        return CustomPluckRecord.objects.create(
            player=player,
            video=video,
            level=level,
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
        member = str(record.player_id)

        self.assertEqual(member, str(record.player_id))
        self.assertEqual(len(self.cache), 1)
        rows = self.cache.get_rank_range(0, 1)

        self.assertEqual(rows[0]['player_id'], record.player_id)
        self.assertEqual(rows[0]['video_id'], record.video_id)
        self.assertEqual(rows[0]['pluck'], record.pluck)
        self.assertEqual(rows[0]['timems'], record.timems)

    def test_zero_pluck_uses_timems_score(self):
        records = [
            self.create_record(self.players[0], pluck=0, timems=2000, seconds=0),
            self.create_record(self.players[1], pluck=0, timems=1000, seconds=0),
            self.create_record(self.players[2], pluck=0.001, timems=1, seconds=0),
        ]

        self.assertEqual(record_to_score(records[0]), records[0].timems - MAX_TIMEMS)
        self.assertEqual(record_to_score(records[2]), records[2].pluck)
        self.assertEqual([row['player_id'] for row in self.cache.get_rank_range(0, 3)], [
            records[1].player_id,
            records[0].player_id,
            records[2].player_id,
        ])

    def test_delete_record_removes_rank_and_detail(self):
        record = self.create_record(self.players[0], pluck=1, timems=1000, seconds=0)

        self.cache.delete_record(record.player_id)

        self.assertEqual(len(self.cache), 0)
        self.assertEqual(self.cache.get_rank_range(0, 1), [])

    def test_cache_to_dict_decodes_player_id_from_member_and_video_id_from_detail(self):
        record = self.create_record(self.players[0], pluck=1.5, timems=1000, seconds=0)
        data = cache_to_dict(str(record.player_id), record.pluck, {
            'video_id': record.video_id,
            'mode': record.video.mode,
            'pluck': record.pluck,
            'timems': record.timems,
            'bv': record.video.bv,
            'upload_time': record.upload_time.isoformat(),
        })

        self.assertEqual(data['player_id'], record.player_id)
        self.assertEqual(data['video_id'], record.video_id)

    def test_get_player_pluck_records_reads_multiple_levels_from_cache(self):
        first = self.create_record(self.players[0], pluck=1, timems=1000, level=LEVEL)
        second = self.create_record(self.players[0], pluck=2, timems=2000, level=SECOND_LEVEL)

        rows_by_level = get_player_pluck_records(self.players[0].id, [LEVEL, SECOND_LEVEL])

        self.assertEqual(rows_by_level[LEVEL]['video_id'], first.video_id)
        self.assertEqual(rows_by_level[SECOND_LEVEL]['video_id'], second.video_id)


class PluckRankingApiTests(CustomRankingTestCase):
    def get_player_records(self, player):
        response = self.client.get('/api/customranking/pluck/player', {'player_id': player.id})
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_player_records_reads_cache_without_database_fallback(self):
        cached_record = self.create_record(self.players[0], pluck=1, timems=1000)
        db_record = self.create_record(
            self.players[0],
            pluck=2,
            timems=2000,
            level=SECOND_LEVEL,
        )
        PLuckRankingCache(SECOND_LEVEL).flush()
        CustomPluckRecord.objects.filter(id=cached_record.id).update(pluck=9)

        rows = self.get_player_records(self.players[0])

        rows_by_level = {row['level']: row for row in rows}
        self.assertEqual(rows_by_level[LEVEL]['video_id'], cached_record.video_id)
        self.assertEqual(rows_by_level[LEVEL]['pluck'], cached_record.pluck)
        self.assertNotIn(SECOND_LEVEL, rows_by_level)
        self.assertTrue(CustomPluckRecord.objects.filter(id=db_record.id).exists())

    def test_player_records_returns_empty_list_for_player_without_records(self):
        rows = self.get_player_records(self.players[4])

        self.assertEqual(rows, [])


class PluckRankingServiceTests(CustomRankingTestCase):
    def test_refresh_all_uses_timems_and_upload_time_tiebreakers(self):
        slower = self.create_video(
            self.players[0],
            pluck=1,
            timems=1001,
            seconds=0,
            state=MS_TextChoices.State.OFFICIAL,
        )
        later = self.create_video(
            self.players[0],
            pluck=1,
            timems=1000,
            seconds=1,
            state=MS_TextChoices.State.OFFICIAL,
        )
        earlier = self.create_video(
            self.players[0],
            pluck=1,
            timems=1000,
            seconds=0,
            state=MS_TextChoices.State.OFFICIAL,
        )

        count = refresh_all_custom_pluck_ranks()

        record = CustomPluckRecord.objects.get(player=self.players[0], level=LEVEL)
        self.assertEqual(count, 1)
        self.assertEqual(record.video_id, earlier.id)
        self.assertNotEqual(record.video_id, slower.id)
        self.assertNotEqual(record.video_id, later.id)

    def test_refresh_all_deletes_records_not_confirmed_in_current_run(self):
        valid_video = self.create_video(
            self.players[0],
            pluck=1,
            timems=1000,
            state=MS_TextChoices.State.OFFICIAL,
        )
        stale_record = self.create_record(self.players[1], pluck=2, timems=1000)
        CustomPluckRecord.objects.filter(id=stale_record.id).update(updated_at=self.now - timedelta(days=1))

        count = refresh_all_custom_pluck_ranks()

        self.assertEqual(count, 1)
        self.assertTrue(CustomPluckRecord.objects.filter(video=valid_video).exists())
        self.assertFalse(CustomPluckRecord.objects.filter(id=stale_record.id).exists())

    def test_refresh_all_touches_existing_valid_records(self):
        video = self.create_video(
            self.players[0],
            pluck=1,
            timems=1000,
            state=MS_TextChoices.State.OFFICIAL,
        )
        record = CustomPluckRecord.objects.create(
            player=self.players[0],
            video=video,
            level=LEVEL,
            pluck=video.pluck,
            timems=video.timems,
            upload_time=video.upload_time,
        )
        old_updated_at = self.now - timedelta(days=1)
        CustomPluckRecord.objects.filter(id=record.id).update(updated_at=old_updated_at)

        refresh_all_custom_pluck_ranks()

        record.refresh_from_db()
        self.assertEqual(record.video_id, video.id)
        self.assertGreater(record.updated_at, old_updated_at)

    def test_refresh_all_scans_players_by_id_range(self):
        for index, player in enumerate(self.players):
            self.create_video(
                player,
                pluck=index + 1,
                timems=1000,
                state=MS_TextChoices.State.OFFICIAL,
            )

        count = refresh_all_custom_pluck_ranks(player_batch_size=2)

        self.assertEqual(count, len(self.players))
        self.assertEqual(CustomPluckRecord.objects.count(), len(self.players))

    def test_refresh_range_only_deletes_stale_records_inside_range(self):
        valid_video = self.create_video(
            self.players[0],
            pluck=1,
            timems=1000,
            state=MS_TextChoices.State.OFFICIAL,
        )
        inside_stale = self.create_record(self.players[1], pluck=2, timems=1000)
        outside_stale = self.create_record(self.players[4], pluck=3, timems=1000)
        CustomPluckRecord.objects.filter(
            id__in=[inside_stale.id, outside_stale.id],
        ).update(updated_at=self.now - timedelta(days=1))

        result = refresh_custom_pluck_rank_range(self.players[0].id, self.players[1].id)

        self.assertEqual(result, {'errorList': [], 'successCount': 1})
        self.assertTrue(CustomPluckRecord.objects.filter(video=valid_video).exists())
        self.assertFalse(CustomPluckRecord.objects.filter(id=inside_stale.id).exists())
        self.assertTrue(CustomPluckRecord.objects.filter(id=outside_stale.id).exists())

    def test_rank_cache_reads_without_database_fallback(self):
        records = [
            self.create_record(self.players[0], pluck=1, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=2, timems=1000, seconds=0),
            self.create_record(self.players[2], pluck=3, timems=1000, seconds=0),
        ]
        self.cache.flush()
        self.cache.add_record(records[0])

        rows = self.cache.get_rank_range(0, 3)

        self.assertEqual([row['player_id'] for row in rows], [
            records[0].player_id,
        ])
        self.assertEqual(len(self.cache), 1)

    def test_rank_cache_can_start_inside_cache(self):
        records = [
            self.create_record(self.players[0], pluck=1, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=2, timems=1000, seconds=0),
            self.create_record(self.players[2], pluck=3, timems=1000, seconds=0),
        ]

        rows = self.cache.get_rank_range(1, 3)

        self.assertEqual([row['player_id'] for row in rows], [
            records[1].player_id,
            records[2].player_id,
        ])
        self.assertEqual(len(self.cache), 3)
        self.assertEqual([row['player_id'] for row in self.cache.get_rank_range(0, 3)], [
            records[0].player_id,
            records[1].player_id,
            records[2].player_id,
        ])

    def test_rank_cache_returns_empty_when_cache_is_empty(self):
        records = [
            self.create_record(self.players[0], pluck=1, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=2, timems=1000, seconds=0),
            self.create_record(self.players[2], pluck=3, timems=1000, seconds=0),
        ]
        self.cache.flush()

        rows = self.cache.get_rank_range(1, 3)

        self.assertEqual(rows, [])
        self.assertEqual(CustomPluckRecord.objects.count(), len(records))

    def test_rebuild_custom_pluck_cache_command_loads_database_records(self):
        records = [
            self.create_record(self.players[0], pluck=1, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=2, timems=1000, seconds=0),
            self.create_record(self.players[2], pluck=3, timems=1000, seconds=0),
        ]
        self.cache.flush()

        call_command('rebuild_custom_pluck_cache', level=LEVEL, stdout=StringIO())

        self.assertEqual([row['player_id'] for row in self.cache.get_rank_range(0, 3)], [
            records[0].player_id,
            records[1].player_id,
            records[2].player_id,
        ])

    def test_update_cache_adds_record_without_cache_size_limit(self):
        records = [
            self.create_record(self.players[0], pluck=1, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=2, timems=1000, seconds=0),
        ]
        weaker = self.create_record(self.players[2], pluck=3, timems=1000, seconds=0)

        update_custom_pluck_top_cache(weaker, LEVEL, weaker.player_id)

        self.assertEqual([row['player_id'] for row in self.cache.get_rank_range(0, 3)], [
            records[0].player_id,
            records[1].player_id,
            weaker.player_id,
        ])

    def test_update_cache_keeps_score_order(self):
        records = [
            self.create_record(self.players[0], pluck=2, timems=1000, seconds=0),
            self.create_record(self.players[1], pluck=3, timems=1000, seconds=0),
        ]
        better = self.create_record(self.players[2], pluck=1, timems=1000, seconds=0)

        update_custom_pluck_top_cache(better, LEVEL, better.player_id)

        self.assertEqual([row['player_id'] for row in self.cache.get_rank_range(0, 3)], [
            better.player_id,
            records[0].player_id,
            records[1].player_id,
        ])
