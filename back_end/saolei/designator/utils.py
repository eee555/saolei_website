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

# 增加标识后扫描所有该标识的录像，返回操作的录像数量
def add_designator_aftermath(user: UserProfile, designator: str):
    video_list = VideoModel.objects.filter(player=user, video__designator=designator)
    for video in video_list:
        if video.state == VideoModel.State.DESIGNATOR:
            update_state(video, VideoModel.State.OFFICIAL)
    return len(video_list)

# 删除标识后扫描所有该标识的录像，返回操作的录像数量
def del_designator_aftermath(user: UserProfile, designator: str):
    video_list = VideoModel.objects.filter(player=user, video__designator=designator)
    for video in video_list:
        if video.state == VideoModel.State.OFFICIAL:
            update_state(video, VideoModel.State.DESIGNATOR, update_ranking=False)
    update_personal_record_stock(user)
    return len(video_list)
