import json
from collections import defaultdict

from django.core.management.base import BaseCommand

from config.text_choices import Tournament_TextChoices
from tournament.cache import (
    NORMAL_PARTICIPANT_CACHE_KEY,
    NORMAL_TOURNAMENT_CACHE_KEY,
    cache,
    serialize_normal_participant,
    serialize_normal_tournament,
)
from tournament.models import Tournament, TournamentParticipant
from utils import ComplexEncoder


class Command(BaseCommand):
    help = '重建比赛 Redis 缓存，包括 NORMAL 比赛和当前 NORMAL 比赛参赛关系'

    def handle(self, *args, **options):
        tournaments = list(
            Tournament.objects
            .filter(state=Tournament_TextChoices.State.NORMAL)
            .select_subclasses(),
        )
        tournament_mapping = {
            tournament.id: json.dumps(serialize_normal_tournament(tournament), cls=ComplexEncoder)
            for tournament in tournaments
        }

        cache.delete(NORMAL_TOURNAMENT_CACHE_KEY, NORMAL_PARTICIPANT_CACHE_KEY)
        if tournament_mapping:
            cache.hset(NORMAL_TOURNAMENT_CACHE_KEY, mapping=tournament_mapping)

        participant_infos_by_user_id = defaultdict(list)
        participants = (
            TournamentParticipant.objects
            .filter(tournament__state=Tournament_TextChoices.State.NORMAL)
            .select_related('arbiter_identifier')
        )
        participant_count = 0
        for participant in participants.iterator():
            if participant.user_id is None:
                continue
            participant_infos_by_user_id[participant.user_id].append(serialize_normal_participant(participant))
            participant_count += 1

        participant_mapping = {
            user_id: json.dumps(participant_infos, cls=ComplexEncoder)
            for user_id, participant_infos in participant_infos_by_user_id.items()
        }
        if participant_mapping:
            cache.hset(NORMAL_PARTICIPANT_CACHE_KEY, mapping=participant_mapping)

        self.stdout.write(self.style.SUCCESS(
            f'rebuilt {len(tournament_mapping)} normal tournaments',
        ))
        self.stdout.write(self.style.SUCCESS(
            f'rebuilt {participant_count} normal participants',
        ))
