from django.db import models
import logging

from msuser.models import UserMS
from utils.exceptions import ExceptionToResponse
from utils import verify_text

logger = logging.getLogger('videomanager')


class Identifier(models.Model):
    identifier = models.CharField(max_length=128, unique=True, db_collation='utf8mb4_0900_as_cs')
    userms = models.ForeignKey(UserMS, null=True, on_delete=models.CASCADE, db_index=True)
    safe = models.BooleanField(default=False)

    @staticmethod
    def verify(identifier_text: str, userms: UserMS):
        collision = Identifier.objects.filter(identifier=identifier_text).first()
        if collision:
            if not collision.safe:
                raise ExceptionToResponse(obj='identifier', category='verify')
            if collision.userms != userms:
                return False
            return True
        identifier = Identifier.objects.create(identifier=identifier_text, safe=verify_text(identifier_text))
        logger.info(f'新标识 "{identifier}" 审查 {identifier.safe}')
        return False
            