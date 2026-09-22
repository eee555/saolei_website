from .base import (
    GSCParticipant,
    Tournament,
    TournamentParticipant,
    TournamentTestCaseBase,
    TournamentUser,
    VideoModel,
    WeeklyParticipant,
)


class TestDeleteParticipant(TournamentTestCaseBase):
    def setUp(self):
        super().setUp()
        self.host = self.create_user('participant_host')
        Tournament.objects.filter(pk=self.tournament.id).update(host=self.host)
        self.participant = self.create_cached_gsc_participant()
        self.url = f'/api/tournament/participant/{self.participant.pk}'

    def test_host_deletes_gsc_participant_and_cache_but_preserves_videos(self):
        video = self.create_video()
        self.assertTrue(self.tournament.videos.filter(pk=video.pk).exists())
        self.client.force_login(self.host)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(TournamentParticipant.objects.filter(pk=self.participant.pk).exists())
        self.assertFalse(GSCParticipant.objects.filter(pk=self.participant.pk).exists())
        self.assertEqual(self.tournament_cache.get_participant_list(self.user.id), [])
        self.assertTrue(TournamentUser.objects.filter(user=self.user).exists())
        self.assertTrue(VideoModel.objects.filter(pk=video.pk).exists())
        self.assertTrue(self.tournament.videos.filter(pk=video.pk).exists())

    def test_host_deletes_weekly_participant_without_removing_other_registration(self):
        tournament = self.create_weekly_tournament(host=self.host)
        participant = WeeklyParticipant.objects.create(
            tournament=tournament, user=self.user, end_time=tournament.end_time,
        )
        self.tournament_cache.update_participant(participant)
        self.client.force_login(self.host)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(f'/api/tournament/participant/{participant.pk}')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(TournamentParticipant.objects.filter(pk=participant.pk).exists())
        self.assertFalse(WeeklyParticipant.objects.filter(pk=participant.pk).exists())
        self.assertTrue(GSCParticipant.objects.filter(pk=self.participant.pk).exists())
        self.assertEqual(
            [item.tournament for item in self.tournament_cache.get_participant_list(self.user.id)],
            [self.tournament.id],
        )

    def test_anonymous_and_non_hosts_cannot_delete_participant(self):
        other_host = self.create_user('other_host')
        self.create_weekly_tournament(host=other_host)
        for user in (None, self.user, other_host):
            with self.subTest(user=user):
                self.client.logout()
                if user is not None:
                    self.client.force_login(user)

                response = self.client.delete(self.url)

                self.assertEqual(response.status_code, 403)
                self.assertTrue(GSCParticipant.objects.filter(pk=self.participant.pk).exists())
                self.assertEqual(len(self.tournament_cache.get_participant_list(self.user.id)), 1)

    def test_staff_can_delete_participant(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.client.force_login(self.user)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(TournamentParticipant.objects.filter(pk=self.participant.pk).exists())

    def test_host_can_delete_non_site_participant(self):
        # Non-site participants are not present in the per-user Redis cache.
        with self.captureOnCommitCallbacks():
            participant = GSCParticipant.objects.create(tournament=self.tournament)
        self.client.force_login(self.host)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(f'/api/tournament/participant/{participant.pk}')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(TournamentParticipant.objects.filter(pk=participant.pk).exists())
        self.assertEqual(len(self.tournament_cache.get_participant_list(self.user.id)), 1)

    def test_missing_participant_returns_not_found(self):
        self.client.force_login(self.host)

        response = self.client.delete('/api/tournament/participant/0')

        self.assertEqual(response.status_code, 404)
