from datetime import datetime
from unittest.mock import patch

from tournament.cache import TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY, TournamentCache
from .base import award_tournament_rank_scores, cache, call_command, StringIO, timedelta, timezone, TOURNAMENT_USER_CACHE_KEYS, TournamentTestCaseBase, TournamentUser, WeeklyParticipant


class ScoreCurrentCacheTests(TournamentTestCaseBase):
    def setUp(self):
        super().setUp()
        self.now = timezone.now()
        self.old_time = self.now - timedelta(days=730)
        self.key = TOURNAMENT_USER_CACHE_KEYS['score_current']

    def reference_time(self):
        return datetime.fromisoformat(cache.get(TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY).decode())

    def test_batch_uses_latest_time_and_api_pages_by_decayed_scores(self):
        other = self.create_user('current_score_new')
        older = TournamentUser.objects.create(user=self.user, score_current=100, last_updated=self.old_time)
        newer = TournamentUser.objects.create(user=other, score_current=80, last_updated=self.now)

        self.tournament_cache.update_tournament_users([older, newer])

        self.assertEqual(self.reference_time(), self.now)
        self.assertEqual(cache.zscore(self.key, self.user.id), 50)
        self.assertEqual(cache.zscore(self.key, other.id), 80)
        for start, expected in ((0, newer), (1, older)):
            response = self.client.get('/api/tournament/user-ranking', {'sort_by': 'score_current', 'start': start, 'end': start + 1})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['total'], 2)
            self.assertEqual(response.json()['data'][0]['user_id'], expected.user_id)
            self.assertEqual(response.json()['data'][0]['score_current'], expected.score_current)
        older.refresh_from_db()
        self.assertEqual((older.score_current, older.last_updated), (100, self.old_time))

    def test_advancing_reference_decays_unmodified_members_only_once(self):
        other = self.create_user('current_score_advance')
        older = TournamentUser(user_id=self.user.id, score_current=100, last_updated=self.old_time, score_total=100)
        newer = TournamentUser(user_id=other.id, score_current=80, last_updated=self.now, score_total=80)
        self.tournament_cache.update_tournament_user(older)

        for _ in range(2):
            self.tournament_cache.update_tournament_user(newer)
            self.assertEqual(self.reference_time(), self.now)
            self.assertEqual(cache.zscore(self.key, self.user.id), 50)
            self.assertEqual(cache.zscore(self.key, other.id), 80)
            self.assertEqual(cache.zscore(TOURNAMENT_USER_CACHE_KEYS['score_total'], self.user.id), 100)

    def test_historical_update_keeps_reference_and_converts_incoming_score(self):
        other = self.create_user('current_score_historical')
        newer = TournamentUser(user_id=other.id, score_current=80, last_updated=self.now)
        older = TournamentUser(user_id=self.user.id, score_current=120, last_updated=self.old_time)
        self.tournament_cache.update_tournament_user(newer)

        self.tournament_cache.update_tournament_user(older, fields=['score_current', 'last_updated'])

        self.assertEqual(self.reference_time(), self.now)
        self.assertEqual(cache.zscore(self.key, self.user.id), 60)
        self.assertEqual(cache.zscore(self.key, other.id), 80)

    def test_default_scores_and_unrelated_fields_do_not_advance_reference(self):
        record = TournamentUser(user_id=self.user.id, score_current=100, last_updated=self.old_time)
        self.tournament_cache.update_tournament_user(record)
        record.last_updated = self.now
        record.score_total = 100
        self.tournament_cache.update_tournament_user(record, fields=['score_total'])
        self.assertEqual(self.reference_time(), self.old_time)
        self.assertEqual(cache.zscore(self.key, self.user.id), 100)

        record.score_current = 0
        self.tournament_cache.update_tournament_user(record, fields=['score_current'])
        self.assertEqual(self.reference_time(), self.old_time)
        self.assertIsNone(cache.zscore(self.key, self.user.id))
        self.assertEqual(cache.zscore(TOURNAMENT_USER_CACHE_KEYS['score_total'], self.user.id), 100)

    def test_rebuild_normalizes_batches_and_ignores_default_record_creation_time(self):
        other = self.create_user('current_score_rebuild')
        default = self.create_user('current_score_default')
        TournamentUser.objects.create(user=self.user, score_current=100, last_updated=self.old_time)
        TournamentUser.objects.create(user=other, score_current=80, last_updated=self.now)
        TournamentUser.objects.create(user=default, last_updated=self.now + timedelta(days=1))
        cache.set(TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY, (self.now + timedelta(days=730)).isoformat())
        cache.zadd(self.key, {'999': 500})

        call_command('rebuild_tournament_user_cache', batch_size=1, stdout=StringIO())

        self.assertEqual(self.reference_time(), self.now)
        self.assertEqual(cache.zrevrange(self.key, 0, -1, withscores=True), [(str(other.id).encode(), 80), (str(self.user.id).encode(), 50)])
        self.assertIsNone(cache.zscore(self.key, default.id))
        self.tournament_cache.clear_tournament_user_cache()
        self.assertIsNone(cache.get(TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY))
        self.assertEqual(cache.zcard(self.key), 0)

    def test_awards_advance_reference_and_decay_players_outside_the_tournament(self):
        other = self.create_user('current_score_award')
        older = TournamentUser.objects.create(user=self.user, score_current=120, last_updated=self.old_time, score_total=120)
        self.tournament_cache.update_tournament_user(older)
        tournament = self.create_weekly_tournament(end_time=self.now)
        WeeklyParticipant.objects.create(user=other, tournament=tournament, rank=1)

        award_tournament_rank_scores(tournament)

        self.assertEqual(self.reference_time(), self.now)
        self.assertEqual(cache.zscore(self.key, self.user.id), 60)
        self.assertEqual(cache.zscore(self.key, other.id), 50)
        next_time = self.now + timedelta(days=730)
        next_tournament = self.create_weekly_tournament(week=2, end_time=next_time)
        WeeklyParticipant.objects.create(user=other, tournament=next_tournament, rank=1)
        award_tournament_rank_scores(next_tournament)
        self.assertEqual(self.reference_time(), next_time)
        self.assertEqual(cache.zscore(self.key, self.user.id), 30)
        self.assertEqual(cache.zscore(self.key, other.id), 75)

        award_tournament_rank_scores(tournament)
        self.assertEqual(self.reference_time(), next_time)
        self.assertEqual(cache.zscore(self.key, self.user.id), 30)
        self.assertEqual(cache.zscore(self.key, other.id), 75)
        older.refresh_from_db()
        self.assertEqual((older.score_current, older.last_updated), (120, self.old_time))

    def test_concurrent_reference_change_retries_with_new_time(self):
        other = self.create_user('current_score_concurrent')
        older = TournamentUser(user_id=self.user.id, score_current=100, last_updated=self.old_time)
        newer = TournamentUser(user_id=other.id, score_current=80, last_updated=self.now)
        self.tournament_cache.update_tournament_user(older)
        update = self.tournament_cache._update_tournament_users_in_pipeline
        interrupted = False

        def concurrent_update(pipe, records, fields, **kwargs):
            nonlocal interrupted
            update(pipe, records, fields, **kwargs)
            if not interrupted:
                interrupted = True
                TournamentCache().update_tournament_user(newer, fields=['score_current'])

        with patch.object(self.tournament_cache, '_update_tournament_users_in_pipeline', side_effect=concurrent_update) as mocked:
            self.tournament_cache.update_tournament_users(iter([older]), fields=['score_current'])
            self.assertEqual(mocked.call_count, 2)
        self.assertEqual(self.reference_time(), self.now)
        self.assertEqual(cache.zscore(self.key, self.user.id), 50)
        self.assertEqual(cache.zscore(self.key, other.id), 80)

    def test_nonempty_cache_without_reference_requires_rebuild(self):
        cache.zadd(self.key, {self.user.id: 100})
        record = TournamentUser(user_id=self.user.id, score_current=80, last_updated=self.now)

        with self.assertRaisesMessage(RuntimeError, 'run rebuild_tournament_user_cache'):
            self.tournament_cache.update_tournament_user(record)

        self.assertEqual(cache.zscore(self.key, self.user.id), 100)
        self.assertIsNone(cache.get(TOURNAMENT_USER_SCORE_CURRENT_TIME_KEY))

    def test_updates_each_zset_with_one_bulk_add_and_one_bulk_remove(self):
        records = [
            TournamentUser(user_id=101, score_current=100, last_updated=self.old_time, score_total=100, gsc_total=60),
            TournamentUser(user_id=102, score_current=80, last_updated=self.now, score_total=80, gsc_total=40),
            TournamentUser(user_id=103),
            TournamentUser(user_id=104),
        ]
        for fields, expected_values in (
            (['score_current', 'score_total'], [{101: 50, 102: 80}, {101: 100, 102: 80}]),
            (['score_total', 'gsc_total'], [{101: 100, 102: 80}, {101: 60, 102: 40}]),
        ):
            with self.subTest(fields=fields):
                self.tournament_cache.clear_tournament_user_cache()
                self.tournament_cache.update_tournament_users([
                    TournamentUser(user_id=user_id, score_current=1, last_updated=self.now, score_total=1, gsc_total=1)
                    for user_id in (103, 104)
                ], fields=fields)
                pipe = cache.pipeline()
                with patch.object(cache, 'pipeline', return_value=pipe):
                    with patch.object(pipe, 'zadd', wraps=pipe.zadd) as adds, patch.object(pipe, 'zrem', wraps=pipe.zrem) as removals:
                        self.tournament_cache.update_tournament_users(iter(records), fields=fields)
                self.assertEqual(adds.call_count, len(fields))
                self.assertEqual(removals.call_count, len(fields))
                for field, expected, addition, removal in zip(fields, expected_values, adds.call_args_list, removals.call_args_list):
                    key = TOURNAMENT_USER_CACHE_KEYS[field]
                    self.assertEqual(addition.args, (key, expected))
                    self.assertEqual(removal.args[0], key)
                    self.assertEqual(set(removal.args[1:]), {103, 104})
                    self.assertEqual(cache.zcard(key), 2)
                    for user_id, score in expected.items():
                        self.assertEqual(cache.zscore(key, user_id), score)

    def test_empty_batch_does_not_queue_redis_commands(self):
        with patch.object(cache, 'pipeline') as pipeline:
            self.tournament_cache.update_tournament_users([], fields=['score_current'])
            self.tournament_cache.update_tournament_users(iter([]), fields=['score_total'])
        pipeline.assert_not_called()
