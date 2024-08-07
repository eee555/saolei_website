from userprofile.models import UserProfile
from videomanager.models import VideoModel
from videomanager.view_utils import update_personal_record_stock, update_state
from utils import verify_text

from .models import Designator

# 审查标识
# 若未记录该标识则创建条目
def verify_designator(designator: str):
    collision = Designator.objects.filter(designator=designator).first()
    if collision:
        return collision.safe
    new_designator = Designator.objects.create(designator=designator, safe=verify_text(designator))
    return new_designator.safe
