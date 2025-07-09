
from django.dispatch import receiver
from django.db.models.signals import pre_save
from videomanager.models import VideoModel

@receiver(pre_save, sender=VideoModel)
def check_tournament_video(sender, instance, created, **kwargs):
    """
    检查录像是否属于比赛录像，如果是，则设置相关字段。
    """
    