
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from config.tournaments import GSC_Defaults
from msuser.models import UserMS
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .gsc.services import refresh_gsc_ranks, refresh_gsc_scores, visible_gsc_token
from .models import GSCParticipant, GSCTournament
from .services import reveal_videos_for_tournament


class TournamentTestCase(TestCase):
    def setUp(self):
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

    def create_video(self, *, user=None, tournament_identifiers=None, level=MS_TextChoices.Level.BEGINNER, timems=1000, bv=10):
        video_index = ExpandVideoModel.objects.count() + 1
        expand_video = ExpandVideoModel.objects.create(identifier=f'gsc-video-{video_index}')
        video = VideoModel(
            player=user or self.user,
            file=f'videos/test-{video_index}.evf',
            file_size=1,
            video=expand_video,
            state=MS_TextChoices.State.OFFICIAL,
            software=MS_TextChoices.Software.EVF,
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
        video._tournament_identifiers = tournament_identifiers if tournament_identifiers is not None else [self.tournament.token]
        video.save()  # noqa: DJM100
        return video

    def test_video_checkin_runs_before_video_create(self):
        video = self.create_video()

        video.refresh_from_db()
        self.assertTrue(video.ongoing_tournament)
        self.assertTrue(self.tournament.videos.filter(pk=video.pk).exists())
        self.assertTrue(GSCParticipant.objects.filter(
            user=self.user,
            tournament=self.tournament,
            token=self.tournament.token,
        ).exists())

    def test_video_without_tournament_identifier_does_not_checkin(self):
        video = self.create_video(tournament_identifiers=[])

        video.refresh_from_db()
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())

    def test_video_checkin_accepts_by_time_window_when_state_is_stale(self):
        GSCTournament.objects.filter(pk=self.tournament.pk).update(state=Tournament_TextChoices.State.PENDING)

        video = self.create_video()

        video.refresh_from_db()
        self.tournament.refresh_from_db()
        self.assertEqual(self.tournament.state, Tournament_TextChoices.State.PENDING)
        self.assertTrue(video.ongoing_tournament)
        self.assertTrue(self.tournament.videos.filter(pk=video.pk).exists())

    def test_video_checkin_rejects_by_time_window_after_end_time(self):
        now = timezone.now()
        GSCTournament.objects.filter(pk=self.tournament.pk).update(
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            state=Tournament_TextChoices.State.NORMAL,
        )

        video = self.create_video()

        video.refresh_from_db()
        self.tournament.refresh_from_db()
        self.assertEqual(self.tournament.state, Tournament_TextChoices.State.NORMAL)
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())

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
        user_without_valid_score = self.create_user('gsc_default_user')
        participant_without_valid_score = GSCParticipant.objects.create(
            user=user_without_valid_score,
            tournament=self.tournament,
            token=self.tournament.token,
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
