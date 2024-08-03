from userprofile.models import UserProfile
from videomanager.models import VideoModel
from videomanager.views import approve_single
from videomanager.view_utils import freeze_single

# 增加标识后扫描所有该标识的录像，返回操作的录像数量
def add_designator_aftermath(user: UserProfile, designator: str):
    video_list = VideoModel.objects.filter(player=user, video__designator=designator)
    for video in video_list:
        approve_single(video, False)
    return len(video_list)

# 删除标识后扫描所有该标识的录像，返回操作的录像数量
def del_designator_aftermath(user: UserProfile, designator: str):
    video_list = VideoModel.objects.filter(player=user, video__designator=designator)
    for video in video_list:
        freeze_single(video, VideoModel.State.DESIGNATOR)
    return len(video_list)
