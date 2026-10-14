from tournament.services import ensure_tournament_users
from .base import (
    _task_award_tournament_impl,
    _task_gsc_refresh_best_impl,
    _task_weekly_refresh_best_impl,
    GSCParticipant,
    MAX_TOURNAMENT_BEST,
    Tournament_TextChoices,
    TournamentTestCaseBase,
    TournamentUser,
    WeeklyParticipant,
)


class TestTaskUsers(TournamentTestCaseBase):
    def test_ensure_tournament_users_only_creates_missing_records_for_this_tournament(self):
        existing_user = self.create_user('existing_tournament_user')
        unrelated_user = self.create_user('unrelated_tournament_user')
        self.create_cached_gsc_participant()
        self.create_cached_gsc_participant(user=existing_user)
        GSCParticipant.objects.create(user=None, tournament=self.tournament)
        WeeklyParticipant.objects.create(user=unrelated_user, tournament=self.create_weekly_tournament())
        TournamentUser.objects.filter(user_id__in=[self.user.id, unrelated_user.id]).delete()
        TournamentUser.objects.filter(user=existing_user).update(score_current=42, score_total=100, gsc_best=123456001)
        existing_values = TournamentUser.objects.filter(user=existing_user).values().get()

        self.assertEqual(ensure_tournament_users(self.tournament), 1)
        self.assertEqual(ensure_tournament_users(self.tournament), 0)

        tournament_user = TournamentUser.objects.get(user=self.user)
        for field in ['score_current', 'score_total', 'gsc_total', 'weekly_total', 'weekly_classic_total']:
            self.assertEqual(getattr(tournament_user, field), 0)
        self.assertEqual(tournament_user.gsc_best, MAX_TOURNAMENT_BEST)
        self.assertEqual(tournament_user.weekly_classic_best, MAX_TOURNAMENT_BEST)
        self.assertEqual(TournamentUser.objects.filter(user=existing_user).values().get(), existing_values)
        self.assertFalse(TournamentUser.objects.filter(user=unrelated_user).exists())
        self.assertEqual(TournamentUser.objects.count(), 2)

    def test_independent_award_task_creates_missing_tournament_users(self):
        weekly = self.create_weekly_tournament()
        self.tournament.weight = 1000
        self.tournament.save(update_fields=['weight'])
        for model, tournament in [(GSCParticipant, self.tournament), (WeeklyParticipant, weekly)]:
            with self.subTest(model=model.__name__):
                user = self.create_user(f'award_{model.__name__}')
                participant = model.objects.create(user=user, tournament=tournament, rank=1)
                TournamentUser.objects.filter(user=user).delete()

                self.assertEqual(_task_award_tournament_impl(tournament.id), 1)

                participant.refresh_from_db()
                tournament_user = TournamentUser.objects.get(user=user)
                self.assertEqual(participant.rank_score, tournament.weight)
                self.assertEqual(tournament_user.score_current, tournament.weight)
                self.assertEqual(tournament_user.score_total, tournament.weight)

    def test_independent_best_tasks_create_missing_tournament_users(self):
        weekly = self.create_weekly_tournament()
        cases = [
            (GSCParticipant, self.tournament, _task_gsc_refresh_best_impl, self.tournament.order, 'gsc_best'),
            (WeeklyParticipant, weekly, _task_weekly_refresh_best_impl, weekly.id, 'weekly_classic_best'),
        ]
        for model, tournament, task_impl, task_arg, best_field in cases:
            with self.subTest(model=model.__name__):
                tournament.state = Tournament_TextChoices.State.AWARDED
                tournament.save(update_fields=['state'])
                user = self.create_user(f'best_{model.__name__}')
                model.objects.create(user=user, tournament=tournament)
                TournamentUser.objects.filter(user=user).delete()

                self.assertEqual(task_impl(task_arg), 1)

                tournament_user = TournamentUser.objects.get(user=user)
                self.assertLess(getattr(tournament_user, best_field), MAX_TOURNAMENT_BEST)
                self.assertEqual(tournament_user.score_current, 0)
                self.assertEqual(tournament_user.score_total, 0)
