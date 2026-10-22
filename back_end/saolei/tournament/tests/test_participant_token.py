from unittest.mock import patch

from tournament.api import TournamentParticipantOut
from tournament.weekly.api import WeeklyRegisterOut
from .base import GSCParticipant, timedelta, timezone, TournamentParticipant, TournamentTestCaseBase, WeeklyParticipant


class TestParticipantToken(TournamentTestCaseBase):
    def test_schemas_use_participant_start_time_without_mutating_token(self):
        now = timezone.now()
        for model in (TournamentParticipant, GSCParticipant, WeeklyParticipant):
            for offset in (-1, 0, 1):
                participant = model(
                    id=1, tournament_id=self.tournament.id, user_id=self.user.id,
                    token='private-token', start_time=now + timedelta(seconds=offset),
                )
                schemas = [TournamentParticipantOut]
                if model is WeeklyParticipant:
                    schemas.append(WeeklyRegisterOut)
                for schema in schemas:
                    with self.subTest(model=model, offset=offset, schema=schema):
                        with patch('tournament.schema.timezone.now', return_value=now), self.assertNumQueries(0):
                            data = schema.from_orm(participant).model_dump()
                        self.assertEqual(data['token'], '' if offset > 0 else 'private-token')
                        self.assertEqual(participant.token, 'private-token')

    def test_weekly_registration_and_list_hide_future_participant_token(self):
        now = timezone.now()
        weekly = self.create_weekly_tournament()
        self.user.realname = 'Player'
        self.user.save(update_fields=['_realname', 'date_updated'])
        with self.captureOnCommitCallbacks(execute=True):
            participant = WeeklyParticipant.objects.create(
                tournament=weekly, user=self.user, token=f'private-{weekly.id}',
                start_time=now + timedelta(minutes=10), end_time=weekly.end_time,
            )
        for authenticated in (False, True):
            with self.subTest(authenticated=authenticated):
                self.client.logout()
                if authenticated:
                    self.client.force_login(self.user)
                response = self.client.get('/api/tournament/participants', {'tournament_id': weekly.id})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()[0]['token'], '')
        response = self.client.post('/api/tournament/weekly/participant', {'id': weekly.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], '')
        participant.refresh_from_db()
        self.assertEqual(participant.token, f'private-{weekly.id}')
        cached = self.tournament_cache.get_participant_list(self.user.id)[0]
        self.assertEqual(cached.token, participant.token)
        with patch('tournament.schema.timezone.now', return_value=participant.start_time):
            response = self.client.get('/api/tournament/participants', {'tournament_id': weekly.id})
        self.assertEqual(response.json()[0]['token'], participant.token)
