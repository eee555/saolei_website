from .base import (
    _task_award_tournament_impl,
    _task_weekly_finish_impl,
    _task_weekly_refresh_best_impl,
    MS_TextChoices,
    refresh_tournament_ranks,
    refresh_weekly_classic_scores,
    timedelta,
    timezone,
    Tournament_TextChoices,
    TournamentTestCaseBase,
    TournamentUser,
    weekly_encode_best,
    WeeklyParticipant,
)


class TestWeekly(TournamentTestCaseBase):
    def test_weekly_participant_create_backfills_and_checkin_uses_token(self):
        tournament = self.create_weekly_tournament()
        existing_video = self.create_video(tournament_identifier=['WEEKLY_TOKEN'])
        WeeklyParticipant.objects.create(
            user=self.user,
            tournament=tournament,
            token='WEEKLY_TOKEN',
            start_time=tournament.start_time,
            end_time=tournament.end_time,
        )
        self.assertTrue(tournament.videos.filter(pk=existing_video.pk).exists())

        other_user = self.create_user('weekly_checkin_user')
        self.client.force_login(other_user)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post('/api/tournament/weekly/participant', {'id': tournament.id})
        participant = WeeklyParticipant.objects.get(tournament=tournament, user=other_user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], participant.token)
        video = self.create_video(user=other_user, tournament_identifier=[participant.token])
        video.refresh_from_db()
        self.assertTrue(video.ongoing_tournament)
        self.assertTrue(tournament.videos.filter(pk=video.pk).exists())

    def test_refresh_weekly_score_rank_and_finish_tournament(self):
        tournament = self.create_weekly_tournament()
        participant = WeeklyParticipant.objects.create(
            user=self.user,
            tournament=tournament,
            start_time=tournament.start_time,
            end_time=tournament.end_time,
        )
        user_without_video = self.create_user('weekly_without_video')
        participant_without_video = WeeklyParticipant.objects.create(
            user=user_without_video,
            tournament=tournament,
            start_time=tournament.start_time,
            end_time=tournament.end_time,
        )

        expert_times = [100000, 120000, 130000]
        intermediate_times = [20000, 21000, 22000, 23000, 24000, 25000]
        for timems in expert_times:
            tournament.videos.add(self.create_video(tournament_identifier=[], level=MS_TextChoices.Level.EXPERT, timems=timems))
        for timems in intermediate_times:
            tournament.videos.add(self.create_video(tournament_identifier=[], level=MS_TextChoices.Level.INTERMEDIATE, timems=timems))

        score_count = refresh_weekly_classic_scores(tournament)
        rank_count = refresh_tournament_ranks(tournament)

        participant.refresh_from_db()
        participant_without_video.refresh_from_db()
        self.assertEqual(score_count, 2)
        self.assertEqual(rank_count, 2)
        self.assertEqual(participant.classic_score, sum(expert_times[:2]) + sum(intermediate_times[:5]))
        self.assertEqual(participant.rank, 1)
        self.assertEqual(participant.rank_score, 0)
        self.assertEqual(participant_without_video.rank, 2)

        tournament.end_time = timezone.now() - timedelta(minutes=1)
        tournament.save(update_fields=['end_time'])
        result = _task_weekly_finish_impl(tournament.id)

        tournament.refresh_from_db()
        participant.refresh_from_db()
        self.assertEqual(result['tournament_users'], 1)
        self.assertEqual(result['deleted_participants'], 1)
        self.assertEqual(result['score_count'], 1)
        self.assertEqual(result['rank_count'], 1)
        self.assertEqual(tournament.state, Tournament_TextChoices.State.AWARDED)
        self.assertEqual(participant.rank_score, 0)
        self.assertTrue(WeeklyParticipant.objects.filter(pk=participant.pk).exists())
        self.assertFalse(WeeklyParticipant.objects.filter(pk=participant_without_video.pk).exists())

        award_count = _task_award_tournament_impl(tournament.id)
        best_count = _task_weekly_refresh_best_impl(tournament.id)
        participant.refresh_from_db()
        tournament_user = TournamentUser.objects.get(user=self.user)
        self.assertEqual(award_count, 1)
        self.assertEqual(best_count, 1)
        self.assertEqual(participant.rank_score, 50)
        self.assertEqual(tournament_user.score_current, 50)
        self.assertEqual(tournament_user.score_total, 50)
        self.assertEqual(tournament_user.weekly_total, 50)
        self.assertEqual(tournament_user.weekly_classic_total, 50)
        self.assertEqual(
            tournament_user.weekly_classic_best,
            weekly_encode_best(participant.classic_score, 2026, 1),
        )
