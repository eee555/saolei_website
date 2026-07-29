from config.text_choices import Tournament_TextChoices
from customranking.services import add_videos_to_custom_pluck_ranks
from msuser.services import update_personal_records_from_video_queryset
from videomanager.cache import add_videos_to_state_queues_bulk
from videomanager.models import VideoModel
from .models import Tournament


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
