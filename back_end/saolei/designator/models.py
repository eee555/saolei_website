from django.db import models
from msuser.models import UserMS

class Designator(models.Model):
    designator = models.CharField(max_length=128, unique=True)
    userms = models.ForeignKey(UserMS, null=False, on_delete=models.CASCADE, db_index=True)