import logging
import requests

from django.core.files.base import ContentFile

from config.text_choices import MS_TextChoices, Saolei_TextChoices
from identifier.models import Identifier
from msuser.models import UserMS
from tournament.utils import video_checkin
from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from utils.parser import MSVideoParser
from utils.saolei import SaoleiUserInfo, SaoleiUtils
from videomanager.models import VideoModel

from .models import AccountSaolei, VideoSaolei, Platform
from .utils import fetch_saolei_profile, fetch_saolei_video_download_and_state, update_msgames_account, update_wom_account

logger = logging.getLogger('accountlink')


def update_account(platform: Platform, user: UserProfile):
    if platform == Platform.SAOLEI:
        update_saolei_account_info(user.account_saolei)
    elif platform == Platform.MSGAMES:
        update_msgames_account(user.account_msgames)
    elif platform == Platform.WOM:
        update_wom_account(user.account_wom)


def update_saolei_account_info(account: AccountSaolei):
    try:
        profile = fetch_saolei_profile(account.id)
        print(profile)
    except requests.exceptions.Timeout:  # 请求超时
        logger.error(f"雷网 用户#{account.id} 信息获取失败：请求超时")
        raise ExceptionToResponse(obj='import', category='timeout')
    except IndexError:  # 解析html时超出索引
        logger.error(f"雷网 用户#{account.id} 信息获取失败：解析错误")
        raise ExceptionToResponse(obj='import', category='indexerror')
    except requests.exceptions.RequestException:  # 其他请求异常
        raise ExceptionToResponse(obj='import', category='requestexception')

    account.name = profile['name']
    account.total_views = profile['total_views']

    account.b_t_ms = profile['timems']['b']
    account.i_t_ms = profile['timems']['i']
    account.e_t_ms = profile['timems']['e']
    account.s_t_ms = profile['timems']['s']

    account.b_b_cent = profile['bvs_cent']['b']
    account.i_b_cent = profile['bvs_cent']['i']
    account.e_b_cent = profile['bvs_cent']['e']
    account.s_b_cent = profile['bvs_cent']['s']

    account.beg_count = profile['count']['b']
    account.int_count = profile['count']['i']
    account.exp_count = profile['count']['e']

    account.save()


# 扫描一页扫雷网用户录像，返回新录像列表
def update_saolei_user_video_one_page(account: AccountSaolei, page: int):
    logger.info(f"开始扫描扫雷网用户#{account.id}的第{page}页录像列表")
    saolei_user = SaoleiUserInfo(saolei_id=account.id)
    try:
        video_list = SaoleiUtils.get_video_list(saolei_user.videos_url(page=page))
    except requests.exceptions.ConnectionError:
        logger.error(f"扫雷网用户#{account.id}的第{page}页录像列表获取失败：连接失败")
        raise ExceptionToResponse(obj='import', category='connection')

    if not video_list:
        logger.warning(f"扫雷网用户#{account.id}的第{page}页录像列表为空")
        raise ExceptionToResponse(obj='saolei', category='page_empty')
    existing_video_ids = list(VideoSaolei.objects.filter(id__in=[info.id for info in video_list]).values_list('id', flat=True))

    new_video_list: list[VideoSaolei] = []
    for video_info in video_list:
        if video_info.id not in existing_video_ids:
            new_video = VideoSaolei.objects.create(id=video_info.id, user=account, upload_time=video_info.upload_time, level=video_info.level, bv=video_info.bv, timems=video_info.timems, nf=video_info.nf)
            new_video_list.append(new_video)

    logger.info(f"扫雷网用户#{account.id}的第{page}页扫描完成，共{len(video_list)}个录像，其中{len(new_video_list)}个新录像")
    return new_video_list


# 导入一个扫雷网录像
def saolei_video_import_one(saolei_video: VideoSaolei):
    logger.info(f"开始导入扫雷网录像#{saolei_video.id}")

    try:
        download_url, state = fetch_saolei_video_download_and_state(saolei_video.id)
        saolei_video.state = state
        saolei_video.save(update_fields=['state'])

        if state == Saolei_TextChoices.SaoleiVideoState.NOTEXIST:
            logger.warning(f"扫雷网 录像#{saolei_video.id} 不存在，可能已被删除")
            return

        file_name = download_url.split('/')[-1]
        response = requests.get(url=download_url, timeout=5)
        file_size = response.headers.get('Content-Length')
        if file_size is None:
            logger.error(f"雷网 录像#{saolei_video.id} 下载失败：无法获取文件大小")
            raise ExceptionToResponse(obj='import', category='unknown')

        collisions = VideoModel.objects.filter(file_size=file_size)
        for collision in collisions:
            if collision.file.read() == response.content:
                if collision.upload_time > saolei_video.upload_time:
                    collision.upload_time = saolei_video.upload_time
                collision.save()
                saolei_video.import_video = collision
                saolei_video.save()
                return

        parser = MSVideoParser(ContentFile(response.content, file_name))
        user = saolei_video.user.parent

        if not user.userms:
            user.userms = UserMS.objects.create()
        if not Identifier.verify(parser.identifier, user.userms) and parser.state == MS_TextChoices.State.OFFICIAL:
            parser.state = MS_TextChoices.State.IDENTIFIER

        video = VideoModel.create_from_parser(parser, user)
        video.upload_time = saolei_video.upload_time
        video_checkin(video, parser.tournament_identifiers)
        video.update_redis()
        saolei_video.import_video = video
        saolei_video.save()
    except requests.exceptions.ConnectionError:
        logger.error(f"雷网 录像#{video.id} 下载失败：连接错误")
        raise ExceptionToResponse(obj='import', category='connection')
    except requests.exceptions.ReadTimeout:
        logger.error(f"雷网 录像#{video.id} 下载失败：请求超时")
        raise ExceptionToResponse(obj='import', category='timeout')
    except BaseException as e:
        logger.error(f"雷网 录像#{video.id} 下载失败：未知错误")
        raise e
