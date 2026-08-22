from .base import (
    cache,
    CachedNormalParticipant,
    call_command,
    GSCParticipant,
    GSCTournament,
    Identifier,
    json,
    MS_TextChoices,
    NORMAL_PARTICIPANT_CACHE_KEY,
    NORMAL_TOURNAMENT_CACHE_KEY,
    StringIO,
    timedelta,
    timezone,
    Tournament,
    Tournament_TextChoices,
    TournamentParticipant,
    TournamentTestCaseBase,
)


class TestCheckinCache(TournamentTestCaseBase):
    def test_video_create_checkin_requires_explicit_participant(self):
        self.tournament_cache.update_tournament(self.tournament)

        video = self.create_video()

        video.refresh_from_db()
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())
        self.assertFalse(GSCParticipant.objects.filter(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
        ).exists())

    def test_video_create_checkin_uses_cached_participant(self):
        self.create_cached_gsc_participant()
        self.tournament_cache.update_tournament(self.tournament)

        video = self.create_video()

        video.refresh_from_db()
        self.assertTrue(video.ongoing_tournament)
        self.assertTrue(self.tournament.videos.filter(pk=video.pk).exists())
        self.assertEqual(GSCParticipant.objects.filter(user=self.user, tournament=self.tournament).count(), 1)

    def test_non_avf_video_create_checkin_uses_tournament_identifier(self):
        self.create_cached_gsc_participant()
        self.tournament_cache.update_tournament(self.tournament)

        video = self.create_video(software=MS_TextChoices.Software.MVF)

        video.refresh_from_db()
        self.assertTrue(video.ongoing_tournament)
        self.assertTrue(self.tournament.videos.filter(pk=video.pk).exists())

    def test_video_without_tournament_identifier_does_not_checkin(self):
        video = self.create_video(tournament_identifier=[])

        video.refresh_from_db()
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())

    def test_video_create_checkin_does_not_fallback_to_db_when_normal_cache_misses(self):
        GSCTournament.objects.filter(pk=self.tournament.pk).update(state=Tournament_TextChoices.State.PENDING)
        cache.delete(NORMAL_TOURNAMENT_CACHE_KEY, NORMAL_PARTICIPANT_CACHE_KEY)

        video = self.create_video()

        video.refresh_from_db()
        self.tournament.refresh_from_db()
        self.assertEqual(self.tournament.state, Tournament_TextChoices.State.PENDING)
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())

    def test_video_create_checkin_rejects_by_time_window_after_end_time(self):
        now = timezone.now()
        GSCTournament.objects.filter(pk=self.tournament.pk).update(
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            state=Tournament_TextChoices.State.NORMAL,
        )
        self.tournament.refresh_from_db()
        self.tournament_cache.update_tournament(self.tournament)
        self.create_cached_gsc_participant()

        video = self.create_video()

        video.refresh_from_db()
        self.assertEqual(self.tournament.state, Tournament_TextChoices.State.NORMAL)
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())

    def test_normal_tournament_cache_reads_redis_hash(self):
        self.tournament_cache.update_tournament(self.tournament)

        tournaments = self.tournament_cache.get_tournament_all()

        self.assertEqual(len(tournaments), 1)
        self.assertEqual(tournaments[0].id, self.tournament.id)
        self.assertEqual(tournaments[0].state, Tournament_TextChoices.State.NORMAL)
        self.assertEqual(tournaments[0].subclass, Tournament_TextChoices.Subclass.GSC)
        self.assertIsNone(tournaments[0].host_id)
        self.assertEqual(tournaments[0].data.order, self.tournament.order)
        self.assertEqual(tournaments[0].data.token, self.tournament.token)
        self.assertIsNotNone(cache.hget(NORMAL_TOURNAMENT_CACHE_KEY, self.tournament.id))

    def test_parent_tournament_can_select_subclass_before_cache_update(self):
        parent_tournament = Tournament.objects.get(id=self.tournament.id)

        self.assertEqual(parent_tournament.subclass, Tournament_TextChoices.Subclass.GSC)
        self.tournament_cache.update_tournament(parent_tournament)

        tournaments = self.tournament_cache.get_tournament_all()
        self.assertEqual(tournaments[0].id, self.tournament.id)
        self.assertEqual(tournaments[0].data.order, self.tournament.order)

    def test_normal_participant_cache_rebuilds_user_field(self):
        identifier = Identifier.objects.create(identifier='cached-arbiter')
        participant = GSCParticipant.objects.create(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
            arbiter_identifier=identifier,
            start_time=self.tournament.start_time,
            end_time=self.tournament.end_time,
        )
        self.tournament_cache.update_participant(participant)

        participants = self.tournament_cache.get_participant_list(self.user.id)
        cached_data = json.loads(cache.hget(NORMAL_PARTICIPANT_CACHE_KEY, self.user.id))

        self.assertEqual(len(participants), 1)
        self.assertEqual(cached_data[0]['id'], participant.id)
        self.assertEqual(participants[0].id, participant.id)
        self.assertEqual(participants[0].token, self.tournament.token)
        self.assertEqual(participants[0].arbiter_identifier, identifier.identifier)
        self.assertEqual(participants[0].tournament, self.tournament.id)
        self.assertEqual(participants[0].start_time, participant.start_time)
        self.assertEqual(participants[0].end_time, participant.end_time)

    def test_tournament_participant_create_updates_cache_through_participant_save(self):
        with self.captureOnCommitCallbacks(execute=True):
            participant = TournamentParticipant.objects.create(
                user=self.user,
                tournament=self.tournament,
                token=self.tournament.token,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            )

        participants = self.tournament_cache.get_participant_list(self.user.id)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0].id, participant.id)
        self.assertEqual(participants[0].tournament, self.tournament.id)

    def test_tournament_participant_create_generates_token_on_save(self):
        with self.captureOnCommitCallbacks(execute=True):
            participant = TournamentParticipant.objects.create(
                user=self.user,
                tournament=self.tournament,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            )

        self.assertTrue(participant.token)
        self.assertEqual(TournamentParticipant.objects.get(id=participant.id).token, participant.token)
        participants = self.tournament_cache.get_participant_list(self.user.id)
        self.assertEqual(participants[0].token, participant.token)

    def test_remove_tournament_removes_matching_participants_from_cache(self):
        self.tournament_cache.set_participant_list(self.user.id, [
            CachedNormalParticipant(
                id=1,
                token=self.tournament.token,
                arbiter_identifier=None,
                tournament=self.tournament.id,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            ),
            CachedNormalParticipant(
                id=2,
                token='OTHER',
                arbiter_identifier=None,
                tournament=999,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            ),
        ])
        other_user = self.create_user('other_cached_user')
        self.tournament_cache.set_participant_list(other_user.id, [
            CachedNormalParticipant(
                id=3,
                token=self.tournament.token,
                arbiter_identifier=None,
                tournament=self.tournament.id,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            ),
        ])

        self.tournament_cache.remove_tournament(self.tournament.id)

        participants = self.tournament_cache.get_participant_list(self.user.id)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0].id, 2)
        self.assertEqual(participants[0].token, 'OTHER')
        self.assertIsNone(participants[0].arbiter_identifier)
        self.assertEqual(participants[0].tournament, 999)
        self.assertEqual(self.tournament_cache.get_participant_list(other_user.id), [])

    def test_gsc_delete_updates_cache_through_parent_tournament_delete(self):
        participant = GSCParticipant.objects.create(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
            start_time=self.tournament.start_time,
            end_time=self.tournament.end_time,
        )
        self.tournament_cache.update_tournament(self.tournament)
        self.tournament_cache.update_participant(participant)
        tournament_id = self.tournament.id

        with self.captureOnCommitCallbacks(execute=True):
            self.tournament.delete()

        self.assertIsNone(self.tournament_cache.get_tournament(tournament_id))
        self.assertEqual(self.tournament_cache.get_participant_list(self.user.id), [])

    def test_gsc_participant_delete_updates_cache_through_parent_participant_delete(self):
        participant = GSCParticipant.objects.create(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
            start_time=self.tournament.start_time,
            end_time=self.tournament.end_time,
        )
        self.tournament_cache.update_participant(participant)

        with self.captureOnCommitCallbacks(execute=True):
            participant.delete()

        self.assertEqual(self.tournament_cache.get_participant_list(self.user.id), [])

    def test_gsc_participant_create_updates_cache_through_gsc_participant_save(self):
        with self.captureOnCommitCallbacks(execute=True):
            participant = GSCParticipant.objects.create(
                user=self.user,
                tournament=self.tournament,
                token=self.tournament.token,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            )

        participants = self.tournament_cache.get_participant_list(self.user.id)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0].id, participant.id)
        self.assertEqual(participants[0].tournament, self.tournament.id)

    def test_gsc_participant_child_field_save_does_not_update_participant_cache(self):
        participant = GSCParticipant.objects.create(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
            start_time=self.tournament.start_time,
            end_time=self.tournament.end_time,
        )
        self.tournament_cache.set_participant_list(self.user.id, [
            CachedNormalParticipant(
                id=participant.id,
                token='STALE',
                arbiter_identifier=None,
                tournament=self.tournament.id,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            ),
        ])

        participant.bt1st += 1
        with self.captureOnCommitCallbacks(execute=True):
            participant.save(update_fields=['bt1st'])

        participants = self.tournament_cache.get_participant_list(self.user.id)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0].token, 'STALE')

    def test_rebuild_tournament_cache_command_rebuilds_both_hashes(self):
        participant = GSCParticipant.objects.create(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
            start_time=self.tournament.start_time,
            end_time=self.tournament.end_time,
        )
        cache.delete(NORMAL_TOURNAMENT_CACHE_KEY, NORMAL_PARTICIPANT_CACHE_KEY)

        stdout = StringIO()
        call_command('rebuild_tournament_cache', stdout=stdout)

        tournaments = self.tournament_cache.get_tournament_all()
        participants = self.tournament_cache.get_participant_list(self.user.id)
        self.assertEqual(tournaments[0].id, self.tournament.id)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0].id, participant.id)
        self.assertEqual(participants[0].token, participant.token)
        self.assertIsNone(participants[0].arbiter_identifier)
        self.assertEqual(participants[0].tournament, self.tournament.id)
        self.assertEqual(participants[0].start_time, participant.start_time)
        self.assertEqual(participants[0].end_time, participant.end_time)
        self.assertIn('rebuilt 1 normal tournaments', stdout.getvalue())
        self.assertIn('rebuilt 1 normal participants', stdout.getvalue())
