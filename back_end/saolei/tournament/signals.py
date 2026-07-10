from typing import Type

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from config.text_choices import Tournament_TextChoices
from videomanager.models import VideoModel
from .models import GSCTournament, Tournament
from .tasks import task_gsc_finish
from .utils import add_video_to_checked_tournaments, video_checkin


def handle_tournament_pre_save(sender: Type[Tournament], instance: Tournament, **kwargs):
    """处理 Tournament 及其子类的 pre_save 信号"""
    update_fields = kwargs.get('update_fields')
    if not update_fields:
        old_instance = sender.objects.filter(pk=instance.pk).first()
        update_fields: list[str] = []
        if old_instance:
            if instance.state != old_instance.state:
                update_fields.append('state')

    if 'state' in update_fields and instance.state == Tournament_TextChoices.State.FINISHED:
        actual_instance = sender.objects.get_subclass(pk=instance.pk)
        if isinstance(actual_instance, GSCTournament):
            task_gsc_finish.enqueue(actual_instance.order)


# 为 Tournament 及其所有子类注册接收器
receiver(pre_save, sender=Tournament)(handle_tournament_pre_save)
receiver(pre_save, sender=GSCTournament)(handle_tournament_pre_save)


@receiver(pre_save, sender=VideoModel, dispatch_uid='tournament.checkin_video_before_create')
def checkin_video_before_create(sender, instance: VideoModel, **kwargs):
    if instance.pk is not None:
        return
    video_checkin(instance, getattr(instance, '_tournament_identifiers', []))


@receiver(post_save, sender=VideoModel, dispatch_uid='tournament.add_created_video_to_checked_tournaments')
def add_created_video_to_checked_tournaments(sender, instance: VideoModel, created: bool, **kwargs):
    if not created:
        return
    add_video_to_checked_tournaments(instance)
