import json
from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from config.tournaments import GSC_Defaults
from identifier.models import Identifier
from msuser.models import UserMS
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .cache import (
    NORMAL_PARTICIPANT_CACHE_KEY,
    NORMAL_TOURNAMENT_CACHE_KEY,
    TournamentCache,
    cache,
    get_normal_participant_infos_for_user,
    get_normal_tournament_infos,
    set_normal_participant_infos_for_user,
    upsert_normal_participant_cache,
)
from .gsc.services import refresh_gsc_ranks, refresh_gsc_scores, visible_gsc_token
from .models import GSCParticipant, GSCTournament, Tournament, select_tournament_subclass
from .services import reveal_videos_for_tournament


class TournamentTestCase(TestCase):
    def setUp(self):
        cache.delete(NORMAL_TOURNAMENT_CACHE_KEY, NORMAL_PARTICIPANT_CACHE_KEY)
        self.tournament_cache = TournamentCache()
        userms = UserMS.objects.create()
        self.user = UserProfile.objects.create_user(
            username='tournament_user',
            email='tournament@example.com',
            password='password',
            userms=userms,
        )
        now = timezone.now()
        self.tournament = GSCTournament.objects.create(
            order=1,
            token='G12345',
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            state=Tournament_TextChoices.State.NORMAL,
        )
        self.tournament_cache.update_tournament(self.tournament)

    def create_user(self, username):
        return UserProfile.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='password',
            userms=UserMS.objects.create(),
        )

    def test_create_tournament(self):
        # TODO: add tests
        pass

    def create_video(
        self,
        *,
        user=None,
        tournament_identifiers=None,
        identifier=None,
        software=MS_TextChoices.Software.EVF,
        level=MS_TextChoices.Level.BEGINNER,
        timems=1000,
        bv=10,
    ):
        video_index = ExpandVideoModel.objects.count() + 1
        tournament_identifiers = tournament_identifiers if tournament_identifiers is not None else [self.tournament.token]
        expand_video = ExpandVideoModel.objects.create(
            identifier=identifier or f'gsc-video-{video_index}',
            tournament_identifier=tournament_identifiers,
        )
        video = VideoModel(
            player=user or self.user,
            file=f'videos/test-{video_index}.evf',
            file_size=1,
            video=expand_video,
            state=MS_TextChoices.State.OFFICIAL,
            software=software,
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
            path=1.0,
            flag=1,
            op=1,
            isl=1,
        )
        video._tournament_identifiers = tournament_identifiers
        video.save()  # noqa: DJM100
        return video

    def create_cached_gsc_participant(self, *, user=None, tournament=None, token=None):
        tournament = tournament or self.tournament
        participant = GSCParticipant.objects.create(
            user=user or self.user,
            tournament=tournament,
            token=token or tournament.token,
            start_time=tournament.start_time,
            end_time=tournament.end_time,
        )
        upsert_normal_participant_cache(participant)
        return participant

    def test_video_checkin_requires_explicit_participant(self):
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

    def test_video_checkin_runs_before_video_create_with_cached_participant(self):
        self.create_cached_gsc_participant()
        self.tournament_cache.update_tournament(self.tournament)

        video = self.create_video()

        video.refresh_from_db()
        self.assertTrue(video.ongoing_tournament)
        self.assertTrue(self.tournament.videos.filter(pk=video.pk).exists())
        self.assertEqual(GSCParticipant.objects.filter(user=self.user, tournament=self.tournament).count(), 1)

    def test_non_avf_video_checkin_uses_tournament_identifier(self):
        self.create_cached_gsc_participant()
        self.tournament_cache.update_tournament(self.tournament)

        video = self.create_video(software=MS_TextChoices.Software.MVF)

        video.refresh_from_db()
        self.assertTrue(video.ongoing_tournament)
        self.assertTrue(self.tournament.videos.filter(pk=video.pk).exists())

    def test_video_without_tournament_identifier_does_not_checkin(self):
        video = self.create_video(tournament_identifiers=[])

        video.refresh_from_db()
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())

    def test_video_checkin_does_not_fallback_to_db_when_normal_cache_misses(self):
        GSCTournament.objects.filter(pk=self.tournament.pk).update(state=Tournament_TextChoices.State.PENDING)
        cache.delete(NORMAL_TOURNAMENT_CACHE_KEY, NORMAL_PARTICIPANT_CACHE_KEY)

        video = self.create_video()

        video.refresh_from_db()
        self.tournament.refresh_from_db()
        self.assertEqual(self.tournament.state, Tournament_TextChoices.State.PENDING)
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())

    def test_video_checkin_rejects_by_time_window_after_end_time(self):
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

        tournaments = get_normal_tournament_infos()

        self.assertEqual(len(tournaments), 1)
        self.assertEqual(tournaments[0].id, self.tournament.id)
        self.assertEqual(tournaments[0].order, self.tournament.order)
        self.assertEqual(tournaments[0].token, self.tournament.token)
        self.assertIsNotNone(cache.hget(NORMAL_TOURNAMENT_CACHE_KEY, self.tournament.id))

    def test_parent_tournament_can_select_subclass_before_cache_update(self):
        parent_tournament = Tournament.objects.get(id=self.tournament.id)

        self.assertEqual(parent_tournament.subclass, Tournament_TextChoices.Subclass.GSC)
        tournament = select_tournament_subclass(parent_tournament)
        self.tournament_cache.update_tournament(tournament)

        tournaments = get_normal_tournament_infos()
        self.assertEqual(tournaments[0].id, self.tournament.id)
        self.assertEqual(tournaments[0].order, self.tournament.order)

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
        upsert_normal_participant_cache(participant)

        participants = get_normal_participant_infos_for_user(self.user.id)
        cached_data = json.loads(cache.hget(NORMAL_PARTICIPANT_CACHE_KEY, self.user.id))

        self.assertEqual(len(participants), 1)
        self.assertEqual(cached_data[0]['id'], participant.id)
        self.assertEqual(participants[0].id, participant.id)
        self.assertEqual(participants[0].token, self.tournament.token)
        self.assertEqual(participants[0].arbiter_identifier, identifier.identifier)
        self.assertEqual(participants[0].tournament, self.tournament.id)
        self.assertEqual(participants[0].start_time, participant.start_time.replace(microsecond=0))
        self.assertEqual(participants[0].end_time, participant.end_time.replace(microsecond=0))

    def test_remove_tournament_removes_matching_participants_from_cache(self):
        set_normal_participant_infos_for_user(self.user.id, [
            {
                'id': 1,
                'token': self.tournament.token,
                'arbiter_identifier': None,
                'tournament': self.tournament.id,
                'start_time': self.tournament.start_time,
                'end_time': self.tournament.end_time,
            },
            {
                'id': 2,
                'token': 'OTHER',
                'arbiter_identifier': None,
                'tournament': 999,
                'start_time': self.tournament.start_time,
                'end_time': self.tournament.end_time,
            },
        ])
        other_user = self.create_user('other_cached_user')
        set_normal_participant_infos_for_user(other_user.id, [
            {
                'id': 3,
                'token': self.tournament.token,
                'arbiter_identifier': None,
                'tournament': self.tournament.id,
                'start_time': self.tournament.start_time,
                'end_time': self.tournament.end_time,
            },
        ])

        self.tournament_cache.remove_tournament(self.tournament)

        participants = get_normal_participant_infos_for_user(self.user.id)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0].id, 2)
        self.assertEqual(participants[0].token, 'OTHER')
        self.assertIsNone(participants[0].arbiter_identifier)
        self.assertEqual(participants[0].tournament, 999)
        self.assertEqual(get_normal_participant_infos_for_user(other_user.id), [])

    def test_video_checkin_uses_cached_participant_to_avoid_duplicate(self):
        participant = GSCParticipant.objects.create(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
            start_time=self.tournament.start_time,
            end_time=self.tournament.end_time,
        )
        self.tournament_cache.update_tournament(self.tournament)
        upsert_normal_participant_cache(participant)

        video = self.create_video()

        video.refresh_from_db()
        self.assertTrue(video.ongoing_tournament)
        self.assertEqual(GSCParticipant.objects.filter(user=self.user, tournament=self.tournament).count(), 1)

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

        tournaments = get_normal_tournament_infos()
        participants = get_normal_participant_infos_for_user(self.user.id)
        self.assertEqual(tournaments[0].id, self.tournament.id)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0].id, participant.id)
        self.assertEqual(participants[0].token, participant.token)
        self.assertIsNone(participants[0].arbiter_identifier)
        self.assertEqual(participants[0].tournament, self.tournament.id)
        self.assertEqual(participants[0].start_time, participant.start_time.replace(microsecond=0))
        self.assertEqual(participants[0].end_time, participant.end_time.replace(microsecond=0))
        self.assertIn('rebuilt 1 normal tournaments', stdout.getvalue())
        self.assertIn('rebuilt 1 normal participants', stdout.getvalue())

    def test_gsc_validate_generates_token_before_start(self):
        now = timezone.now()
        tournament = GSCTournament.objects.create(
            order=3,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            state=Tournament_TextChoices.State.PENDING,
        )

        tournament.validate()

        tournament.refresh_from_db()
        self.assertEqual(tournament.state, Tournament_TextChoices.State.NORMAL)
        self.assertTrue(tournament.token.startswith('G'))

    def test_gsc_add_participant_uses_tournament_time_window(self):
        self.tournament.add_participant(self.user)

        participant = GSCParticipant.objects.get(tournament=self.tournament, user=self.user)
        self.assertEqual(participant.start_time, self.tournament.start_time)
        self.assertEqual(participant.end_time, self.tournament.end_time)

    def test_creating_participant_adds_existing_videos_in_time_window(self):
        matched_video = self.create_video()
        other_software_video = self.create_video(software=MS_TextChoices.Software.MVF)
        outside_video = self.create_video()
        missing_identifier_video = self.create_video(tournament_identifiers=[])
        avf_with_token_video = self.create_video(
            software=MS_TextChoices.Software.AVF,
            tournament_identifiers=[self.tournament.token],
        )
        VideoModel.objects.filter(pk=outside_video.pk).update(
            upload_time=self.tournament.end_time + timedelta(minutes=1),
        )

        with self.captureOnCommitCallbacks(execute=True):
            GSCParticipant.objects.create(
                user=self.user,
                tournament=self.tournament,
                token=self.tournament.token,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            )

        matched_video.refresh_from_db()
        other_software_video.refresh_from_db()
        outside_video.refresh_from_db()
        missing_identifier_video.refresh_from_db()
        self.assertTrue(self.tournament.videos.filter(pk=matched_video.pk).exists())
        self.assertTrue(self.tournament.videos.filter(pk=other_software_video.pk).exists())
        self.assertFalse(self.tournament.videos.filter(pk=outside_video.pk).exists())
        self.assertFalse(self.tournament.videos.filter(pk=missing_identifier_video.pk).exists())
        self.assertFalse(self.tournament.videos.filter(pk=avf_with_token_video.pk).exists())
        self.assertFalse(matched_video.ongoing_tournament)
        self.assertFalse(other_software_video.ongoing_tournament)
        self.assertFalse(outside_video.ongoing_tournament)
        self.assertFalse(missing_identifier_video.ongoing_tournament)
        self.assertFalse(avf_with_token_video.ongoing_tournament)

    def test_creating_arbiter_participant_adds_matching_avf_videos(self):
        identifier = Identifier.objects.create(identifier='arbiter-id')
        matched_video = self.create_video(
            identifier=identifier.identifier,
            software=MS_TextChoices.Software.AVF,
            tournament_identifiers=[],
        )
        token_only_video = self.create_video(
            software=MS_TextChoices.Software.AVF,
            tournament_identifiers=[self.tournament.token],
        )

        with self.captureOnCommitCallbacks(execute=True):
            GSCParticipant.objects.create(
                user=self.user,
                tournament=self.tournament,
                token=self.tournament.token,
                arbiter_identifier=identifier,
                start_time=self.tournament.start_time,
                end_time=self.tournament.end_time,
            )

        matched_video.refresh_from_db()
        token_only_video.refresh_from_db()
        self.assertTrue(self.tournament.videos.filter(pk=matched_video.pk).exists())
        self.assertFalse(self.tournament.videos.filter(pk=token_only_video.pk).exists())
        self.assertFalse(matched_video.ongoing_tournament)
        self.assertFalse(token_only_video.ongoing_tournament)

    def test_gsc_validate_rejects_missing_time(self):
        tournament = GSCTournament.objects.create(
            order=5,
            start_time=None,
            end_time=None,
            state=Tournament_TextChoices.State.PENDING,
        )

        self.assertFalse(tournament.validate())

        tournament.refresh_from_db()
        self.assertEqual(tournament.state, Tournament_TextChoices.State.PENDING)
        self.assertEqual(tournament.token, '')

    def test_gsc_validate_rejects_invalid_time_range(self):
        now = timezone.now()
        tournament = GSCTournament.objects.create(
            order=6,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=1),
            state=Tournament_TextChoices.State.PENDING,
        )

        self.assertFalse(tournament.validate())

        tournament.refresh_from_db()
        self.assertEqual(tournament.state, Tournament_TextChoices.State.PENDING)
        self.assertEqual(tournament.token, '')

    def test_gsc_token_is_hidden_until_start_time(self):
        now = timezone.now()
        tournament = GSCTournament.objects.create(
            order=4,
            token='G54321',
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            state=Tournament_TextChoices.State.NORMAL,
        )

        self.assertEqual(visible_gsc_token(tournament), '')

        tournament.start_time = now - timedelta(minutes=1)
        self.assertEqual(visible_gsc_token(tournament), tournament.token)

    def test_reveal_videos_for_tournament_restores_personal_record(self):
        self.create_cached_gsc_participant()
        video = self.create_video()
        GSCTournament.objects.filter(pk=self.tournament.pk).update(
            end_time=timezone.now() - timedelta(hours=1),
            state=Tournament_TextChoices.State.AWARDED,
        )
        self.tournament.refresh_from_db()

        changed_count = reveal_videos_for_tournament(self.tournament)

        video.refresh_from_db()
        self.user.userms.refresh_from_db()
        self.assertEqual(changed_count, 1)
        self.assertFalse(video.ongoing_tournament)
        self.assertEqual(self.user.userms.b_timems_std, video.timems)
        self.assertEqual(self.user.userms.b_timems_id_std, video.id)

    def test_reveal_videos_for_tournament_waits_until_awarded(self):
        self.create_cached_gsc_participant()
        video = self.create_video()
        GSCTournament.objects.filter(pk=self.tournament.pk).update(
            end_time=timezone.now() - timedelta(hours=1),
            state=Tournament_TextChoices.State.NORMAL,
        )
        self.tournament.refresh_from_db()

        changed_count = reveal_videos_for_tournament(self.tournament)

        video.refresh_from_db()
        self.assertEqual(changed_count, 0)
        self.assertTrue(video.ongoing_tournament)

    def test_reveal_videos_for_tournament_keeps_videos_in_other_unawarded_tournament(self):
        self.create_cached_gsc_participant()
        video = self.create_video()
        now = timezone.now()
        other_tournament = GSCTournament.objects.create(
            order=2,
            token='G67890',
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            state=Tournament_TextChoices.State.PENDING,
        )
        other_tournament.videos.add(video)
        GSCTournament.objects.filter(pk=self.tournament.pk).update(
            end_time=now - timedelta(minutes=1),
            state=Tournament_TextChoices.State.AWARDED,
        )
        self.tournament.refresh_from_db()

        changed_count = reveal_videos_for_tournament(self.tournament)

        video.refresh_from_db()
        self.assertEqual(changed_count, 0)
        self.assertTrue(video.ongoing_tournament)

    def test_refresh_gsc_score_and_rank_uses_batch_rules(self):
        participant = GSCParticipant.objects.create(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
            start_time=self.tournament.start_time,
            end_time=self.tournament.end_time,
        )
        upsert_normal_participant_cache(participant)
        user_without_valid_score = self.create_user('gsc_default_user')
        participant_without_valid_score = GSCParticipant.objects.create(
            user=user_without_valid_score,
            tournament=self.tournament,
            token=self.tournament.token,
            start_time=self.tournament.start_time,
            end_time=self.tournament.end_time,
        )
        participant_without_valid_score.bt1st = 1
        participant_without_valid_score.bt20th = 1
        participant_without_valid_score.bt20sum = 1
        participant_without_valid_score.it1st = 1
        participant_without_valid_score.it12th = 1
        participant_without_valid_score.it12sum = 1
        participant_without_valid_score.et1st = 1
        participant_without_valid_score.et5th = 1
        participant_without_valid_score.et5sum = 1
        participant_without_valid_score.save(update_fields=[
            'bt1st', 'bt20th', 'bt20sum',
            'it1st', 'it12th', 'it12sum',
            'et1st', 'et5th', 'et5sum',
        ])

        beginner_times = [1000 + index * 100 for index in range(21)]
        intermediate_times = [10000 + index * 1000 for index in range(13)]
        expert_times = [40000 + index * 10000 for index in range(6)]
        for timems in beginner_times:
            self.create_video(level=MS_TextChoices.Level.BEGINNER, timems=timems, bv=GSC_Defaults.B_BV_MIN)
        for timems in intermediate_times:
            self.create_video(level=MS_TextChoices.Level.INTERMEDIATE, timems=timems, bv=GSC_Defaults.I_BV_MIN)
        for timems in expert_times:
            self.create_video(level=MS_TextChoices.Level.EXPERT, timems=timems, bv=GSC_Defaults.E_BV_MIN)

        self.create_video(level=MS_TextChoices.Level.BEGINNER, timems=999, bv=GSC_Defaults.B_BV_MIN - 1)
        self.create_video(level=MS_TextChoices.Level.INTERMEDIATE, timems=GSC_Defaults.IT, bv=GSC_Defaults.I_BV_MIN)
        self.create_video(level=MS_TextChoices.Level.EXPERT, timems=1, bv=GSC_Defaults.E_BV_MIN - 1)

        score_changed = refresh_gsc_scores(self.tournament)
        rank_changed = refresh_gsc_ranks(self.tournament)

        participant = GSCParticipant.objects.get(tournament=self.tournament, user=self.user)
        participant_without_valid_score.refresh_from_db()

        beginner_top = beginner_times[:20]
        intermediate_top = intermediate_times[:12]
        expert_top = expert_times[:5]
        self.assertEqual(score_changed, 2)
        self.assertEqual(rank_changed, 2)
        self.assertEqual(participant.bt1st, beginner_top[0])
        self.assertEqual(participant.bt20th, beginner_top[-1])
        self.assertEqual(participant.bt20sum, sum(beginner_top))
        self.assertEqual(participant.it1st, intermediate_top[0])
        self.assertEqual(participant.it12th, intermediate_top[-1])
        self.assertEqual(participant.it12sum, sum(intermediate_top))
        self.assertEqual(participant.et1st, expert_top[0])
        self.assertEqual(participant.et5th, expert_top[-1])
        self.assertEqual(participant.et5sum, sum(expert_top))
        self.assertEqual(participant.rank, 1)
        self.assertEqual(participant_without_valid_score.bt1st, GSC_Defaults.BT)
        self.assertEqual(participant_without_valid_score.bt20sum, GSC_Defaults.BT * 20)
        self.assertEqual(participant_without_valid_score.it12sum, GSC_Defaults.IT * 12)
        self.assertEqual(participant_without_valid_score.et5sum, GSC_Defaults.ET * 5)
        self.assertEqual(participant_without_valid_score.rank, 2)
