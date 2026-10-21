import re

from bilibili_api import sync
from bilibili_api.user import User
from lxml import etree
import requests

from config.text_choices import Saolei_TextChoices
from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from .models import AccountBilibili, Platform, PLATFORM_CONFIG

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
}
private_platforms = [Platform.QQ]


def isPrivate(platform) -> bool:
    return platform in private_platforms


def link_account(platform: Platform, linkid, user: UserProfile):
    model = PLATFORM_CONFIG[platform]['model']
    linkid = model._meta.pk.to_python(linkid)
    account = model.objects.select_for_update().filter(id=linkid).first()
    if not account:
        account = model.objects.create(id=linkid, parent=user)
    else:
        if account.parent_id != user.pk:
            raise ExceptionToResponse('accountlink', 'collision', status_code=409)
        account.parent = user
        account.save(update_fields=['parent'])
    return account


def delete_account(user: UserProfile, platform: Platform):
    if platform == Platform.SAOLEI:
        user.account_saolei.delete()
    elif platform == Platform.MSGAMES:
        user.account_msgames.delete()
    elif platform == Platform.WOM:
        user.account_wom.delete()
    elif platform == Platform.BILIBILI:
        user.account_bilibili.delete()
    elif platform == Platform.MINERACER:
        raise ExceptionToResponse('mineracer', 'unlink_not_supported', status_code=409)


def fetch_saolei_profile(saolei_id: int):
    def timeparser(t):
        return round(float(t) * 1000)

    def bvsparser(b):
        return round(float(b) * 100)
    InfoHtmlStr = None
    VideoHtmlStr = None

    url = f'http://saolei.wang/Player/Info.asp?Id={saolei_id}'
    response = requests.get(url=url, timeout=5)
    response.encoding = 'GB2312'
    InfoHtmlStr = response.text

    url = f'http://saolei.wang/Video/Satus.asp?Id={saolei_id}'
    response = requests.get(url=url, timeout=5)
    response.encoding = 'GB2312'
    VideoHtmlStr = response.text

    if not InfoHtmlStr or not VideoHtmlStr:
        raise ValueError('Failed to fetch profile or video page')  # 没有爬取到信息

    tree = etree.HTML(InfoHtmlStr)
    values = tree.xpath('//span[@class="Sign"]/text()')
    name = values[0] if values else None

    values = tree.xpath('//td[@class="Text"]/span[@class="Highest"]/text()')
    total_views = int(values[0]) if values else None

    values = tree.xpath('//tr/td[2]/a[1]/text()')
    b_t_ms = timeparser(values[0]) - 1000 if values else None

    values = tree.xpath('//tr/td[2]/a[3]/text()')
    i_t_ms = timeparser(values[0]) - 1000 if values else None

    values = tree.xpath('//tr/td[2]/a[5]/text()')
    e_t_ms = timeparser(values[0]) - 1000 if values else None

    values = tree.xpath('//tr/td[2]/span[8]/text()')
    s_t_ms = timeparser(values[0]) - 3000 if values else None

    timems = {
        'b': b_t_ms,
        'i': i_t_ms,
        'e': e_t_ms,
        's': s_t_ms,
    }

    values = tree.xpath('//tr/td[2]/a[2]/text()')
    b_b_cent = bvsparser(values[0]) if values else None

    values = tree.xpath('//tr/td[2]/a[4]/text()')
    i_b_cent = bvsparser(values[0]) if values else None

    values = tree.xpath('//tr/td[2]/a[6]/text()')
    e_b_cent = bvsparser(values[0]) if values else None

    values = tree.xpath('//tr/td[2]/span[9]/text()')
    s_b_cent = bvsparser(values[0]) if values else None

    bvs_cent = {
        'b': b_b_cent,
        'i': i_b_cent,
        'e': e_b_cent,
        's': s_b_cent,
    }

    tree = etree.HTML(VideoHtmlStr)
    values = tree.xpath('(//td[@class="Counters"])[1]/text()')
    beg_count = int(values[0]) if values else None

    values = tree.xpath('(//td[@class="Counters"])[2]/text()')
    int_count = int(values[0]) if values else None

    values = tree.xpath('(//td[@class="Counters"])[3]/text()')
    exp_count = int(values[0]) if values else None

    count = {
        'b': beg_count,
        'i': int_count,
        'e': exp_count,
    }

    return {'name': name, 'total_views': total_views, 'timems': timems, 'bvs_cent': bvs_cent, 'count': count}


def fetch_saolei_video_download_and_state(video_id: int) -> tuple[str, ]:
    response = requests.get(url=f'http://saolei.wang/Video/Show.asp?Id={video_id}', timeout=5)
    response.encoding = 'GB2312'
    if response.text == """<script language="JavaScript">alert('此录象不存在!');</script><script language=JavaScript>top.location=top.location</script>""":
        return '', Saolei_TextChoices.SaoleiVideoState.NOTEXIST
    if '此录像尚未通过审核！' in response.text:
        state = Saolei_TextChoices.SaoleiVideoState.PENDING
    elif '为什么冻结？' in response.text:
        state = Saolei_TextChoices.SaoleiVideoState.FROZEN
    else:
        state = Saolei_TextChoices.SaoleiVideoState.OFFICIAL
    return 'http://saolei.wang/' + re.search(r"PlayVideo\('([^']+)'\)", response.text).group(1), state


def update_bilibili_account(account: AccountBilibili):
    bili_user = User(uid=account.id)
    try:
        info = sync(bili_user.get_user_info())
        relation = sync(bili_user.get_relation_info())
        overview = sync(bili_user.get_overview_stat())
    except TimeoutError:
        raise ExceptionToResponse(obj='import', category='timeout')
    except Exception:
        raise ExceptionToResponse(obj='import', category='requestexception')

    official = info.get('official', {})
    account.name = info.get('name', '') or ''
    account.face = info.get('face', '') or ''
    account.sign = info.get('sign', '') or ''
    account.level = info.get('level', 0) or 0
    account.following = relation.get('following', 0) or 0
    account.follower = relation.get('follower', 0) or 0
    account.video_count = overview.get('video', 0) or 0
    account.article_count = overview.get('article', 0) or 0
    account.opus_count = overview.get('opus', 0) or 0
    account.official_title = official.get('title', '') or ''
    account.save(update_fields=[
        'name', 'face', 'sign', 'level',
        'following', 'follower',
        'video_count', 'article_count', 'opus_count',
        'official_title',
    ])
