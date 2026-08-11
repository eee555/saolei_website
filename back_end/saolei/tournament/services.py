from datetime import timedelta

from django.db.models import Q, Sum
from django.utils import timezone

from config.text_choices import MS_TextChoices, Tournament_TextChoices
from customranking.services import add_videos_to_custom_pluck_ranks
from msuser.services import update_personal_records_from_video_queryset
from tournament.cache import TournamentCache
from tournament.gsc.services import calculate_gsc_best_score
from tournament.gsc.utils import gsc_encode_best
from tournament.utils import encode_tournament_best
from tournament.weekly.services import calculate_weekly_best_score
from videomanager.cache import add_videos_to_state_queues_bulk
from videomanager.models import VideoModel
from .models import (
    GSCParticipant,
    GSCTournament,
    Tournament,
    TournamentParticipant,
    TournamentUser,
    WeeklyParticipant,
    WeeklyTournament,
)

cache = TournamentCache()
TOURNAMENT_SCORE_HALF_LIFE = timedelta(days=365 * 2)


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


def tournament_score_decay_factor(start_time, end_time):
    if end_time <= start_time:
        return 1
    elapsed_seconds = (end_time - start_time).total_seconds()
    half_life_seconds = TOURNAMENT_SCORE_HALF_LIFE.total_seconds()
    return 1 / (2 ** (elapsed_seconds / half_life_seconds))


def decay_tournament_user_scores(now=None, *, batch_size=1000):
    now = now or timezone.now()
    tournament_users = list(TournamentUser.objects.all())
    for tournament_user in tournament_users:
        tournament_user.score_current *= tournament_score_decay_factor(tournament_user.last_updated, now)
        tournament_user.last_updated = now
    if tournament_users:
        TournamentUser.objects.bulk_update(tournament_users, ['score_current', 'last_updated'], batch_size=batch_size)
    return len(tournament_users)


def refresh_tournament_user_best_scores(user_id: int, *, update_gsc=True, update_weekly=True):
    update_fields = []
    tournament_user = TournamentUser.objects.filter(user_id=user_id).first()
    if tournament_user is None:
        if not TournamentParticipant.objects.filter(user_id=user_id, rank_score__gt=0).exists():
            return 0
        tournament_user = TournamentUser.objects.create(user_id=user_id)

    if update_gsc:
        tournament_user.gsc_best = calculate_gsc_best_score(user_id)
        update_fields.append('gsc_best')
    if update_weekly:
        tournament_user.weekly_best = calculate_weekly_best_score(user_id)
        update_fields.append('weekly_best')
    if not update_fields:
        return 0
    tournament_user.save(update_fields=update_fields)
    return 1


def _get_score_total_by_user(queryset):
    return {
        item['user_id']: item['score_total'] or 0
        for item in (
            queryset
            .filter(user_id__isnull=False, rank_score__gt=0)
            .values('user_id')
            .annotate(score_total=Sum('rank_score'))
        )
    }


def refresh_tournament_user_total_and_best_fields(*, batch_size=1000):
    score_total_by_user = _get_score_total_by_user(TournamentParticipant.objects)
    gsc_total_by_user = _get_score_total_by_user(GSCParticipant.objects)
    weekly_total_by_user = _get_score_total_by_user(WeeklyParticipant.objects)

    user_ids = (
        set(TournamentUser.objects.values_list('user_id', flat=True))
        | set(score_total_by_user)
        | set(gsc_total_by_user)
        | set(weekly_total_by_user)
    )
    existing_user_ids = set(TournamentUser.objects.filter(user_id__in=user_ids).values_list('user_id', flat=True))
    missing_user_ids = user_ids - existing_user_ids
    if missing_user_ids:
        TournamentUser.objects.bulk_create(
            [TournamentUser(user_id=user_id) for user_id in missing_user_ids],
            batch_size=batch_size,
        )

    tournament_users = list(TournamentUser.objects.filter(user_id__in=user_ids))
    for tournament_user in tournament_users:
        user_id = tournament_user.user_id
        tournament_user.score_total = score_total_by_user.get(user_id, 0)
        tournament_user.gsc_total = gsc_total_by_user.get(user_id, 0)
        tournament_user.weekly_total = weekly_total_by_user.get(user_id, 0)
        tournament_user.gsc_best = calculate_gsc_best_score(user_id)
        tournament_user.weekly_best = calculate_weekly_best_score(user_id)

    if tournament_users:
        TournamentUser.objects.bulk_update(
            tournament_users,
            ['score_total', 'gsc_total', 'weekly_total', 'gsc_best', 'weekly_best'],
            batch_size=batch_size,
        )

    return len(tournament_users)


def award_tournament_rank_scores(tournament: Tournament, *, batch_size=1000):
    award_time = tournament.end_time or timezone.now()
    decay_tournament_user_scores(award_time, batch_size=batch_size)

    participants = list(
        TournamentParticipant.objects
        .filter(tournament=tournament, user_id__isnull=False, rank__isnull=False)
        .select_related('user', 'gscparticipant', 'weeklyparticipant')
        .order_by('rank'),
    )
    if not participants:
        return 0

    tournament_users_by_user_id = {
        tournament_user.user_id: tournament_user
        for tournament_user in TournamentUser.objects.filter(user_id__in=[participant.user_id for participant in participants])
    }
    tournament_users_to_create = []
    for participant in participants:
        if participant.user_id not in tournament_users_by_user_id:
            tournament_user = TournamentUser(user_id=participant.user_id, last_updated=award_time)
            tournament_users_by_user_id[participant.user_id] = tournament_user
            tournament_users_to_create.append(tournament_user)
    if tournament_users_to_create:
        TournamentUser.objects.bulk_create(tournament_users_to_create, batch_size=batch_size)

    changed_participants = []
    changed_tournament_users = []
    best_score_user_ids = set()
    for participant in participants:
        target_rank_score = round(tournament.weight / participant.rank)
        score_delta = target_rank_score - participant.rank_score
        if score_delta == 0:
            continue

        tournament_user = tournament_users_by_user_id[participant.user_id]
        tournament_user.score_current = max(tournament_user.score_current + score_delta, 0)
        tournament_user.score_total = max(tournament_user.score_total + score_delta, 0)

        if isinstance(tournament, GSCTournament):
            tournament_user.gsc_total = max(tournament_user.gsc_total + score_delta, 0)
        elif isinstance(tournament, WeeklyTournament):
            tournament_user.weekly_total = max(tournament_user.weekly_total + score_delta, 0)

        participant.rank_score = target_rank_score
        changed_participants.append(participant)
        changed_tournament_users.append(tournament_user)
        best_score_user_ids.add(participant.user_id)

    if changed_tournament_users:
        TournamentUser.objects.bulk_update(
            changed_tournament_users,
            ['score_current', 'score_total', 'gsc_total', 'weekly_total'],
            batch_size=batch_size,
        )
    if changed_participants:
        TournamentParticipant.objects.bulk_update(changed_participants, ['rank_score'], batch_size=batch_size)
        for user_id in best_score_user_ids:
            refresh_tournament_user_best_scores(
                user_id,
                update_gsc=isinstance(tournament, GSCTournament),
                update_weekly=isinstance(tournament, WeeklyTournament),
            )

    return len(changed_participants)


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
