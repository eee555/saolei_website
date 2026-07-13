
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
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
            state=Tournament_TextChoices.State.ONGOING,
        )

    def test_create_tournament(self):
        # TODO: add tests
        pass

    def create_video(self, *, tournament_identifiers=None):
        expand_video = ExpandVideoModel.objects.create(identifier='gsc-video')
        video = VideoModel(
            player=self.user,
            file='videos/test.evf',
            file_size=1,
            video=expand_video,
            state=MS_TextChoices.State.OFFICIAL,
            software=MS_TextChoices.Software.EVF,
            level=MS_TextChoices.Level.BEGINNER,
            mode=MS_TextChoices.Mode.STD,
            timems=1000,
            bv=10,
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

    def test_reveal_videos_for_tournament_restores_personal_record(self):
        video = self.create_video()
        GSCTournament.objects.filter(pk=self.tournament.pk).update(state=Tournament_TextChoices.State.FINISHED)
        self.tournament.refresh_from_db()

        changed_count = reveal_videos_for_tournament(self.tournament)

        video.refresh_from_db()
        self.user.userms.refresh_from_db()
        self.assertEqual(changed_count, 1)
        self.assertFalse(video.ongoing_tournament)
        self.assertEqual(self.user.userms.b_timems_std, video.timems)
        self.assertEqual(self.user.userms.b_timems_id_std, video.id)

    def test_reveal_videos_for_tournament_keeps_videos_in_other_ongoing_tournament(self):
        video = self.create_video()
        now = timezone.now()
        other_tournament = GSCTournament.objects.create(
            order=2,
            token='G67890',
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            state=Tournament_TextChoices.State.ONGOING,
        )
        other_tournament.videos.add(video)
        GSCTournament.objects.filter(pk=self.tournament.pk).update(state=Tournament_TextChoices.State.FINISHED)
        self.tournament.refresh_from_db()

        changed_count = reveal_videos_for_tournament(self.tournament)

        video.refresh_from_db()
        self.assertEqual(changed_count, 0)
        self.assertTrue(video.ongoing_tournament)
