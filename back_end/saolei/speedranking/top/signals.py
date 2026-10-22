from django.dispatch import receiver

from .events import soft_refresh_requested
from .tasks import task_refresh_soft_ranks


@receiver(soft_refresh_requested, dispatch_uid='speedranking.top.refresh_soft')
def enqueue_soft_refresh(sender, **kwargs):
    task_refresh_soft_ranks.enqueue()
