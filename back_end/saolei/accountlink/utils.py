from datetime import timedelta
import re

from django.utils import timezone
from lxml import etree
import requests

from config.text_choices import Saolei_TextChoices
from userprofile.models import UserProfile
from .models import AccountMinesweeperGames, AccountWorldOfMinesweeper, Platform, PLATFORM_CONFIG

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'}


def link_account(platform: Platform, linkid, user: UserProfile):
    model = PLATFORM_CONFIG[platform]['model']
    account = model.objects.filter(id=linkid).first()
    if not account:
        account = model.objects.create(id=linkid, parent=user)
    else:
        account.parent = user
    return account


def delete_account(user: UserProfile, platform: Platform):
    if platform == Platform.SAOLEI:
        user.account_saolei.delete()
    elif platform == Platform.MSGAMES:
        user.account_msgames.delete()
    elif platform == Platform.WOM:
        user.account_wom.delete()
    else:
        ValueError()


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
        raise ValueError("Failed to fetch profile or video page")  # 没有爬取到信息

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
        's': s_t_ms
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
        's': s_b_cent
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
        'e': exp_count
    }

    return {"name": name, "total_views": total_views, "timems": timems, "bvs_cent": bvs_cent, "count": count}


def fetch_saolei_video_download_and_state(video_id: int) -> tuple[str, ]:
    response = requests.get(url=f'http://saolei.wang/Video/Show.asp?Id={video_id}', timeout=5)
    response.encoding = 'GB2312'
    if response.text == '''<script language="JavaScript">alert('此录象不存在!');</script><script language=JavaScript>top.location=top.location</script>''':
        return "", Saolei_TextChoices.SaoleiVideoState.NOTEXIST
    if '此录像尚未通过审核！' in response.text:
        state = Saolei_TextChoices.SaoleiVideoState.PENDING
    elif '为什么冻结？' in response.text:
        state = Saolei_TextChoices.SaoleiVideoState.FROZEN
    else:
        state = Saolei_TextChoices.SaoleiVideoState.OFFICIAL
    return 'http://saolei.wang/' + re.search(r"PlayVideo\('([^']+)'\)", response.text).group(1), state


def update_msgames_account(account: AccountMinesweeperGames, cooldown):
    if timezone.now() - account.update_time < timedelta(hours=cooldown):
        return "cooldown"
    msgamesid = account.id
    htmlStr = None
    try:
        url = f'https://minesweepergame.com/profile.php?pid={msgamesid}'
        response = requests.get(url=url, timeout=5, headers=headers)
        htmlStr = response.text
    except requests.exceptions.Timeout:
        return "timeout"  # 请求超时
    except requests.exceptions.RequestException:
        return "unknown"
    if not htmlStr:
        return "empty"  # 没有爬取到信息
    tree = etree.HTML(htmlStr)

    def getValue(text):
        values = tree.xpath(f'//td[text()="{text}"]/../td[2]/text()')
        return values[0] if values else None
    account.name = str(getValue('Name'))
    account.local_name = str(getValue('Local Name'))
    account.joined = getValue('Joined')
    account.save()
    return ""


def update_wom_account(account: AccountWorldOfMinesweeper, cooldown):
    if timezone.now() - account.update_time < timedelta(hours=cooldown):
        return "cooldown"
    womid = account.id
    url = f'https://minesweeper.online/player/{womid}'
    htmlStr = None
    try:
        response = requests.get(url=url, timeout=5)
        htmlStr = response.text
    except requests.exceptions.Timeout:
        return "timeout"  # 请求超时
    except requests.exceptions.RequestException:
        return "unknown"
    if not htmlStr:
        return "empty"  # 没有爬取到信息
    tree = etree.HTML(htmlStr)
    tree = tree.xpath(
        '/html/body/div[3]/div[2]/div/div[1]/div[2]/div/div[4]/div/div[1]')[0]

    def formatXpath(text):
        return f'//strong[text()="{text}"]/../following-sibling::div/span/text()'

    def formatImgXpath(text, img, last):
        return f'//strong[text()="{text}"]/../following-sibling::div//img[@class="{img}"]{last}'

    def formatIXpath(text, i, last):
        return f'//strong[text()="{text}"]/../following-sibling::div//i[@class="{i}"]{last}'

    def stringToInt(values) -> int:
        return int(str(values[0]).replace(" ", "").replace("%", "")) if values else None

    def stringToFloat(values) -> float:
        return float(str(values[0]).replace(" ", "").replace("%", "")) if values else None
    values = tree.xpath(formatXpath("Trophies:"))
    account.trophy = int(values[0]) if values else None

    values = tree.xpath(formatImgXpath(
        "Experience:", "exp-icon icon-right", "/../text()"))
    account.experience = stringToInt(values)

    values = tree.xpath(formatImgXpath(
        "Experience:", "hp-icon icon-right", "/../../text()"))
    account.honour = stringToInt(values)

    values = tree.xpath(formatImgXpath(
        "Resources:", "coin-icon icon-right", "/../../text()"))
    account.minecoin = stringToInt(values)

    values = tree.xpath(formatImgXpath(
        "Resources:", "gem gem0 icon-right", "/../span/text()"))
    account.gem = stringToInt(values)

    values = tree.xpath(formatImgXpath(
        "Resources:", "arena-coin-icon icon-right", "/../span/text()"))
    account.coin = stringToInt(values)

    values = tree.xpath(formatIXpath(
        "Resources:", "fa fa-ticket ticket-right ticket0", "/../span/text()"))
    account.arena_ticket = stringToInt(values)

    values = tree.xpath(formatImgXpath(
        "Resources:", "parts-icon ", "/preceding-sibling::text()"))
    account.part = stringToInt(values)

    values = tree.xpath(formatImgXpath(
        "Resources:", "eq-icon", "/../span/text()"))
    account.equipment = stringToInt(values)

    values = tree.xpath(formatImgXpath(
        "Arena points:", "arena-icon ", "/../text()"))
    account.arena_point = stringToInt(values)

    values = tree.xpath(formatImgXpath(
        "Max difficulty:", "diff-icon ", "/../a/text()"))
    account.max_difficulty = stringToInt(values)

    values = tree.xpath(formatIXpath(
        "Wins:", "fa fa-flag wins-icon ", "/../text()"))
    account.win = stringToInt(values)
    values = tree.xpath(
        '//strong[text()="Last season:"]/../following-sibling::div//text()')
    if not values:
        values = tree.xpath(
            '//strong[contains(text(),"Season")]/../..//text()')
    account.last_season = re.search(
        r'S(\d+)', ' '.join(values)).group(1) if values else None

    def formatSpanXpath(text, index):
        return f'//span[text()="{text}"]/../following-sibling::div[{index}]//text()'
    values = tree.xpath(formatSpanXpath("Beginner", 1))
    account.b_t_ms = round(stringToFloat(values) * 1000)

    values = tree.xpath(formatSpanXpath("Intermediate", 1))
    account.i_t_ms = round(stringToFloat(values) * 1000)

    values = tree.xpath(formatSpanXpath("Expert", 1))
    account.e_t_ms = round(stringToFloat(values) * 1000)

    values = tree.xpath(formatIXpath(
        "Efficiency:", "fa fa-dot-circle-o eff-icon level1", "/../text()"))
    account.b_ioe = stringToFloat(values) / 100

    values = tree.xpath(formatIXpath(
        "Efficiency:", "fa fa-dot-circle-o eff-icon level2", "/../text()"))
    account.i_ioe = stringToFloat(values) / 100

    values = tree.xpath(formatIXpath(
        "Efficiency:", "fa fa-dot-circle-o eff-icon level3", "/../text()"))
    account.e_ioe = stringToFloat(values) / 100

    values = tree.xpath(formatIXpath(
        "Mastery:", "glyphicon glyphicon-flash mastery-icon mastery1", "/../text()"))
    account.b_mastery = stringToInt(values)

    values = tree.xpath(formatIXpath(
        "Mastery:", "glyphicon glyphicon-flash mastery-icon mastery2", "/../text()"))
    account.i_mastery = stringToInt(values)

    values = tree.xpath(formatIXpath(
        "Mastery:", "glyphicon glyphicon-flash mastery-icon mastery3", "/../text()"))
    account.e_mastery = stringToInt(values)

    values = tree.xpath(formatIXpath(
        "Win streak:", "fa fa-crosshairs ws-icon ws1", "/../text()"))
    account.b_winstreak = stringToInt(values)

    values = tree.xpath(formatIXpath(
        "Win streak:", "fa fa-crosshairs ws-icon ws2", "/../text()"))
    account.i_winstreak = stringToInt(values)

    values = tree.xpath(formatIXpath(
        "Win streak:", "fa fa-crosshairs ws-icon ws3", "/../text()"))
    account.e_winstreak = stringToInt(values)

    account.save()
    return ""
