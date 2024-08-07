from userprofile.models import UserProfile
from videomanager.models import VideoModel
from videomanager.view_utils import update_personal_record_stock, update_state
from utils import verify_text

from .models import Identifier

# 审查标识
# 若未记录该标识则创建条目
def verify_designator(identifier: str):
    collision = Identifier.objects.filter(identifier=identifier).first()
    if collision:
        return collision.safe
    new_designator = Identifier.objects.create(identifier=identifier, safe=verify_text(identifier))
    return new_designator.safe
