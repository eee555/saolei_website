
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from msuser.models import UserMS
from userprofile.models import UserProfile
from videomanager.models import ExpandVideoModel, VideoModel
from .models import GSCParticipant, GSCTournament


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

    def create_video(self, *, skip_tournament_checkin=False):
        expand_video = ExpandVideoModel.objects.create(identifier='gsc-video', stnb=0)
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
        video._tournament_identifiers = [self.tournament.token]
        if skip_tournament_checkin:
            video._skip_tournament_checkin = True
        video.save()
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

    def test_video_checkin_can_be_skipped_before_video_create(self):
        video = self.create_video(skip_tournament_checkin=True)

        video.refresh_from_db()
        self.assertFalse(video.ongoing_tournament)
        self.assertFalse(self.tournament.videos.filter(pk=video.pk).exists())
