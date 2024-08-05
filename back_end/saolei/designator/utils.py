from userprofile.models import UserProfile
from videomanager.models import VideoModel
from videomanager.views import approve_single
from videomanager.view_utils import freeze_single, update_personal_record_stock

# 增加标识后扫描所有该标识的录像，返回操作的录像数量
def add_designator_aftermath(user: UserProfile, designator: str):
    video_list = VideoModel.objects.filter(player=user, video__designator=designator)
    for video in video_list:
        if video.state == VideoModel.State.DESIGNATOR:
            approve_single(video, False)
    return len(video_list)

# 删除标识后扫描所有该标识的录像，返回操作的录像数量
def del_designator_aftermath(user: UserProfile, designator: str):
    video_list = VideoModel.objects.filter(player=user, video__designator=designator)
    for video in video_list:
        if video.state == VideoModel.State.OFFICIAL:
            freeze_single(video, state=VideoModel.State.DESIGNATOR, update_ranking=False)
    update_personal_record_stock(user)
    return len(video_list)
