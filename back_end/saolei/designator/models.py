from django.db import models
from msuser.models import UserMS

class Designator(models.Model):
    designator = models.TextField(null=False, unique=True)
    userms = models.ForeignKey(UserMS, null=False, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['userms'], name='userms_idx'),
        ]