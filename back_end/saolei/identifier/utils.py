import logging
from utils import verify_text
from .models import Identifier
logger = logging.getLogger('videomanager')


# 审查标识
# 若未记录该标识则创建条目
def verify_identifier(identifier: str):
    collision = Identifier.objects.filter(identifier=identifier).first()
    if collision:
        return collision.safe
    new_identifier = Identifier.objects.create(identifier=identifier, safe=verify_text(identifier))
    logger.info(f'新标识 "{identifier}" 审查 {new_identifier.safe}')
    return new_identifier.safe
