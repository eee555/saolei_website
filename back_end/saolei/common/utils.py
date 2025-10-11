import ms_toollib as ms
from userprofile.models import UserProfile, UserMS
from videomanager.models import VideoModel, ExpandVideoModel
from tournament.models import TournamentParticipant, GSCTournament, GSCParticipant
from config.text_choices import MS_TextChoices, Tournament_TextChoices
from django.core.files import File
from datetime import datetime, timezone
from utils.exceptions import ExceptionToResponse
from identifier.utils import verify_identifier
import logging

logger = logging.getLogger('videomanager')

def get_level_from_BaseVideo(v: ms.BaseVideo):
    if v.level == 3:
        return MS_TextChoices.Level.BEGINNER
    elif v.level == 4:
        return MS_TextChoices.Level.INTERMEDIATE
    elif v.level == 5:
        return MS_TextChoices.Level.EXPERT
    else:
        raise ExceptionToResponse(obj='file', category='level')
    
def get_state_from_review_code(review_code: int):
    if review_code == 0:
        return MS_TextChoices.State.OFFICIAL
    elif review_code == 1:
        return MS_TextChoices.State.FROZEN
    elif review_code == 3:
        return MS_TextChoices.State.PLAIN
    else:
        raise ExceptionToResponse(obj='file', category='review')

def new_video_by_file(user: UserProfile, file: File, check_tournament: bool = True) -> VideoModel:
    data = file.read()
    if file.name.endswith('.avf'):
        v = ms.AvfVideo(raw_data=data)
        software = MS_TextChoices.Software.AVF
    elif file.name.endswith('.evf'):
        v = ms.EvfVideo(raw_data=data)
        software = MS_TextChoices.Software.EVF
    elif file.name.endswith('.rmv'):
        v = ms.RmvVideo(raw_data=data)
        software = MS_TextChoices.Software.RMV
    elif file.name.endswith('.mvf'):
        v = ms.MvfVideo(raw_data=data)
        software = MS_TextChoices.Software.MVF
    else:
        raise ExceptionToResponse(obj='file', category='type')

    v.parse_video()
    v.analyse()
    v.current_time = 1e8

    level = get_level_from_BaseVideo(v)

    review_code = v.is_valid()
    state = get_state_from_review_code(review_code)

    if not user.userms:
        user.userms = UserMS.objects.create()

    identifier = v.player_identifier
    if not verify_identifier(identifier):
        raise ExceptionToResponse(obj='identifier', category='verify')
    if identifier not in user.userms.identifiers and state == MS_TextChoices.State.OFFICIAL:
        state = MS_TextChoices.State.IDENTIFIER

    collisions = list(VideoModel.objects.filter(timems=v.rtime_ms, bv=v.bbbv).filter(path=v.path).filter(
        left=v.left, right=v.right, double=v.double, op=v.op, isl=v.isl))
    if collisions:
        raise ExceptionToResponse(obj='file', category='collision')

    mode = str(v.mode).rjust(2, '0')
    if mode == '00' and v.flag == 0:
        mode = '12'

    e_video = ExpandVideoModel.objects.create(
        identifier=identifier,
        stnb=v.stnb,
    )
    video = VideoModel.objects.create(
        player=user,
        file=file,
        file_size=file.size,
        video=e_video,
        end_time=datetime.fromtimestamp(v.end_time / 1000000, tz=timezone.utc),
        state=state,
        software=software,
        level=level,
        mode=mode,
        timems=v.rtime_ms,
        bv=v.bbbv,
        left=v.left,
        right=v.right,
        double=v.double,
        left_ce=v.lce,
        right_ce=v.rce,
        double_ce=v.dce,
        path=v.path,
        flag=v.flag,
        op=v.op,
        isl=v.isl,
        cell0=v.cell0,
        cell1=v.cell1,
        cell2=v.cell2,
        cell3=v.cell3,
        cell4=v.cell4,
        cell5=v.cell5,
        cell6=v.cell6,
        cell7=v.cell7,
        cell8=v.cell8,
    )

    if check_tournament:
        if file.name.endswith('.avf'):
            if participant := TournamentParticipant.objects.filter(user=user, arbiter_identifier__identifier=video.video.identifier).first():
                tournament = participant.tournament
                if tournament.state == Tournament_TextChoices.State.ONGOING:
                    video.ongoing_tournament = True
                    tournament.videos.add(video)
        elif file.name.endswith('.evf'):
            tournament_tokens = v.race_identifier.split(',')
            for token in tournament_tokens:
                if token == '':
                    continue
                gsc_tournament = GSCTournament.objects.filter(token=token).first()
                participant = TournamentParticipant.objects.filter(user=user, tournament=gsc_tournament).first()
                if not gsc_tournament:  # 暂时只支持gsc
                    continue
                if gsc_tournament and gsc_tournament.state == Tournament_TextChoices.State.ONGOING:
                    video.ongoing_tournament = True
                    gsc_tournament.videos.add(video)
                    if not participant:
                        GSCParticipant.objects.create(user=user, tournament=gsc_tournament, token=token)

    video.save()
    video.update_redis()

    return video
