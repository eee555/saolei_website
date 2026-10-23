from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import MiniGameBestScore
from .services import remove_cached_score


@receiver(post_delete, sender=MiniGameBestScore)
def delete_cached_score(sender, instance, **kwargs):
    ranking_key, player_id = instance.ranking_key, instance.player_id
    transaction.on_commit(lambda: remove_cached_score(ranking_key, player_id))
