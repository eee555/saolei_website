from unittest.mock import patch

from .base import (
    GSCParticipant,
    Identifier,
    timedelta,
    timezone,
    Tournament_TextChoices,
    TournamentTestCaseBase,
)


class TestGscRegistration(TournamentTestCaseBase):
    def setUp(self):
        super().setUp()
        self.user.realname = 'GSC Player'
        self.user.save(update_fields=['realname', 'date_updated'])
        self.client.force_login(self.user)

    def test_registration_before_start_preserves_private_token_and_disallows_arbiter_binding(self):
        self.tournament.start_time = timezone.now() + timedelta(minutes=30)
        with self.captureOnCommitCallbacks(execute=True):
            self.tournament.save(update_fields=['start_time'])
            response = self.client.post('/api/tournament/gsc/participant', {'order': self.tournament.order})
        self.assertEqual(response.status_code, 200)
        participant = GSCParticipant.objects.get(tournament=self.tournament, user=self.user)
        self.assertEqual(participant.token, self.tournament._token)
        self.assertEqual(participant.start_time, self.tournament.start_time)
        self.assertEqual(participant.end_time, self.tournament.end_time)
        self.assertEqual(self.tournament_cache.get_participant_list(self.user.id)[0].token, self.tournament._token)

        for user in (self.user, None):
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)
                response = self.client.get('/api/tournament/participants', {'tournament_id': self.tournament.id})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()[0]['token'], '')
                self.assertNotIn(self.tournament._token, response.content.decode())
        participant.refresh_from_db()
        self.assertEqual(participant.token, self.tournament._token)

        self.client.force_login(self.user)
        identifier = f'Player {self.tournament._token}'
        response = self.client.post('/api/tournament/gsc/participant/identifier', {'order': self.tournament.order, 'identifier': identifier})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Identifier.objects.filter(identifier=identifier).exists())
        participant.refresh_from_db()
        self.assertIsNone(participant.arbiter_identifier_id)

        self.tournament.start_time = timezone.now() - timedelta(minutes=1)
        self.tournament.save(update_fields=['start_time'])
        participant.start_time = self.tournament.start_time
        participant.save(update_fields=['start_time'])
        response = self.client.get('/api/tournament/participants', {'tournament_id': self.tournament.id})
        self.assertEqual(response.json()[0]['token'], self.tournament._token)
        Identifier.objects.create(identifier=identifier, safe=True)
        response = self.client.post('/api/tournament/gsc/participant/identifier', {'order': self.tournament.order, 'identifier': identifier})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'success')

    def test_registration_requires_normal_state_and_an_unexpired_window(self):
        now = timezone.now()
        cases = [
            (Tournament_TextChoices.State.PENDING, now + timedelta(hours=1)),
            (Tournament_TextChoices.State.CANCELLED, now + timedelta(hours=1)),
            (Tournament_TextChoices.State.AWARDED, now - timedelta(hours=1)),
            (Tournament_TextChoices.State.NORMAL, now),
            (Tournament_TextChoices.State.NORMAL, now - timedelta(seconds=1)),
        ]
        for state, end_time in cases:
            with self.subTest(state=state, end_time=end_time):
                type(self.tournament).objects.filter(pk=self.tournament.pk).update(state=state, end_time=end_time)
                with patch('tournament.gsc.api.timezone.now', return_value=now):
                    response = self.client.post('/api/tournament/gsc/participant', {'order': self.tournament.order})
                self.assertEqual(response.status_code, 403)
                self.assertFalse(GSCParticipant.objects.filter(tournament=self.tournament).exists())

    def test_is_ongoing_uses_normal_state_and_a_half_open_window(self):
        for now, expected in [
            (self.tournament.start_time - timedelta(seconds=1), False),
            (self.tournament.start_time, True),
            (self.tournament.end_time - timedelta(seconds=1), True),
            (self.tournament.end_time, False),
        ]:
            with self.subTest(now=now), patch('tournament.models.timezone.now', return_value=now):
                self.assertEqual(self.tournament.is_ongoing(), expected)
        self.tournament.state = Tournament_TextChoices.State.CANCELLED
        self.assertFalse(self.tournament.is_ongoing())
