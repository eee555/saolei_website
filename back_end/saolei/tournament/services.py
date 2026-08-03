from django.db.models import Q

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from customranking.services import add_videos_to_custom_pluck_ranks
from msuser.services import update_personal_records_from_video_queryset
from tournament.cache import TournamentCache
from videomanager.cache import add_videos_to_state_queues_bulk
from videomanager.models import VideoModel
from .models import Tournament, TournamentParticipant

cache = TournamentCache()


def checkin_with_arbiter(video: VideoModel, arbiter_identifier: str):
    participants = cache.checkin_arbiter(video, arbiter_identifier)
    tournament_ids = {participant.tournament for participant in participants}
    if tournament_ids:
        video.ongoing_tournament = True
    return list(Tournament.objects.filter(id__in=tournament_ids))


def checkin_with_token(video: VideoModel, tokens: list[str]):
    participants = cache.checkin_token(video, tokens)
    tournament_ids = {participant.tournament for participant in participants}
    if tournament_ids:
        video.ongoing_tournament = True
    return list(Tournament.objects.filter(id__in=tournament_ids))


def add_existing_videos_to_participant_tournament(participant: TournamentParticipant):
    if participant.user_id is None or participant.start_time is None or participant.end_time is None:
        return 0

    identifier_filter = Q()
    if participant.arbiter_identifier is not None:
        identifier_filter = Q(
            software=MS_TextChoices.Software.AVF,
            video__identifier=participant.arbiter_identifier.identifier,
        )
    token_filter = (
        ~Q(software=MS_TextChoices.Software.AVF)
        & Q(video__tournament_identifier__contains=[participant.token])
    )

    video_ids = list(
        VideoModel.objects
        .filter(
            player_id=participant.user_id,
            upload_time__gte=participant.start_time,
            upload_time__lte=participant.end_time,
        )
        .filter(identifier_filter | token_filter)
        .values_list('id', flat=True),
    )
    if not video_ids:
        return 0

    participant.tournament.videos.add(*video_ids)
    return len(video_ids)


def delete_participants_without_videos(tournament: Tournament):
    video_player_ids = tournament.videos.values('player_id')
    participants = (
        TournamentParticipant.objects
        .filter(tournament=tournament, user_id__isnull=False)
        .exclude(user_id__in=video_player_ids)
    )
    deleted_count = participants.count()
    participants.delete()
    return deleted_count


def reveal_videos_for_tournament(tournament: Tournament):
    """批量恢复已颁奖比赛中不再属于其他未颁奖且未取消比赛的录像。"""
    if tournament.state != Tournament_TextChoices.State.AWARDED:
        return 0

    current_video_ids = set(
        tournament.videos
        .filter(ongoing_tournament=True)
        .values_list('id', flat=True),
    )
    unrevealed_video_ids = set(
        Tournament.objects
        .exclude(state__in=[Tournament_TextChoices.State.AWARDED, Tournament_TextChoices.State.CANCELLED])
        .filter(videos__ongoing_tournament=True)
        .values_list('videos__id', flat=True)
        .distinct(),
    )
    video_ids = list(current_video_ids - unrevealed_video_ids)

    if not video_ids:
        return 0

    VideoModel.objects.filter(id__in=video_ids).update(ongoing_tournament=False)

    videos = (
        VideoModel.objects
        .filter(id__in=video_ids)
        .select_related('player', 'player__userms', 'video')
    )
    add_videos_to_state_queues_bulk(videos)
    update_personal_records_from_video_queryset(videos)
    add_videos_to_custom_pluck_ranks(videos)

    return len(video_ids)
