import re
from .models import AccountSaolei, AccountMinesweeperGames, AccountWorldOfMinesweeper, Platform
from userprofile.models import UserProfile
import requests
from lxml import etree
from datetime import timedelta
from django.utils import timezone
headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'}
def link_account(platform: Platform, id, user: UserProfile):
    if platform == Platform.SAOLEI:
        link_saolei_account(id, user)
    elif platform == Platform.MSGAMES:
        link_msgames_account(id, user)
    elif platform == Platform.WOM:
        link_wom_account(id, user)
    else:
        ValueError()

def delete_account(user: UserProfile, platform: Platform):
    if platform == Platform.SAOLEI:
        user.account_saolei.delete()
    elif platform == Platform.MSGAMES:
        user.account_msgames.delete()
    elif platform == Platform.WOM:
        user.account_wom.delete()
    else:
        ValueError()

def link_saolei_account(id, user: UserProfile):
    account = AccountSaolei.objects.filter(id=id).first()
    if not account:
        account = AccountSaolei.objects.create(id=id, parent=user)
    else:
        account.parent = user
    return account

def link_msgames_account(id, user: UserProfile):
    account = AccountMinesweeperGames.objects.filter(id=id).first()
    if not account:
        account = AccountMinesweeperGames.objects.create(id=id, parent=user)
    else:
        account.parent = user
    return account

def link_wom_account(id, user: UserProfile):
    account = AccountWorldOfMinesweeper.objects.filter(id=id).first()
    if not account:
        account = AccountWorldOfMinesweeper.objects.create(id=id, parent=user)
    else:
        account.parent = user
    return account

def update_account(platform: Platform, user: UserProfile, cooldown = 12):
    if platform == Platform.SAOLEI:
        return update_saolei_account(user.account_saolei, cooldown)
    elif platform == Platform.MSGAMES:
        return update_msgames_account(user.account_msgames, cooldown)
    elif platform == Platform.WOM:
        return update_wom_account(user.account_wom, cooldown)
    else:
        return 'unsupported'

def update_saolei_account(account: AccountSaolei, cooldown):
    if timezone.now() - account.update_time < timedelta(hours=cooldown):
        return "cooldown"
    def timeparser(t):
        return round(float(t)*1000)
    def bvsparser(b):
        return round(float(b)*100)
    InfoHtmlStr = None
    VideoHtmlStr = None
    id = account.id
    try:
        url = f'http://saolei.wang/Player/Info.asp?Id={id}'
        response = requests.get(url=url, timeout=5,headers=headers)
        response.encoding = 'GB2312'
        InfoHtmlStr = response.text

        url = f'http://saolei.wang/Video/Satus.asp?Id={id}'
        response = requests.get(url=url, timeout=5,headers=headers)
        response.encoding = 'GB2312'
        VideoHtmlStr = response.text
    except requests.exceptions.Timeout as e:
        return "timeout" # 请求超时
    except IndexError as e:
        return "indexerror" # 解析html时超出索引
    except requests.exceptions.RequestException as e:
        return "unknown"
    if not InfoHtmlStr or not VideoHtmlStr:
        return "empty" # 没有爬取到信息
    tree = etree.HTML(InfoHtmlStr)
    values = tree.xpath('//span[@class="Sign"]/text()')
    account.name = values[0] if values else None
    
    values = tree.xpath('//td[@class="Text"]/span[@class="Highest"]/text()')
    account.total_views = int(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[1]/text()')
    account.b_t_ms = timeparser(values[0])-1000 if values else None
    
    values = tree.xpath('//tr/td[2]/a[3]/text()')
    account.i_t_ms = timeparser(values[0])-1000 if values else None
    
    values = tree.xpath('//tr/td[2]/a[5]/text()')
    account.e_t_ms = timeparser(values[0])-1000 if values else None
    
    values = tree.xpath('//tr/td[2]/span[8]/text()')
    account.s_t_ms = timeparser(values[0])-3000 if values else None
    
    values = tree.xpath('//tr/td[2]/a[2]/text()')
    account.b_b_cent = bvsparser(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[4]/text()')
    account.i_b_cent = bvsparser(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[6]/text()')
    account.e_b_cent = bvsparser(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/span[9]/text()')
    account.s_b_cent = bvsparser(values[0]) if values else None
    
    tree = etree.HTML(VideoHtmlStr)
    values = tree.xpath('(//td[@class="Counters"])[1]/text()')
    account.beg_count = int(values[0]) if values else None
    
    values = tree.xpath('(//td[@class="Counters"])[2]/text()')
    account.int_count = int(values[0]) if values else None
    
    values = tree.xpath('(//td[@class="Counters"])[3]/text()')
    account.exp_count = int(values[0]) if values else None
    
    account.save()
    return ""

def update_msgames_account(account: AccountMinesweeperGames, cooldown):
    if timezone.now() - account.update_time < timedelta(hours=cooldown):
        return "cooldown"
    id = account.id
    htmlStr = None
    try:
        url = f'https://minesweepergame.com/profile.php?pid={id}'
        response = requests.get(url=url, timeout=5,headers=headers)
        htmlStr = response.text
    except requests.exceptions.Timeout as e:
        return "timeout" # 请求超时
    except requests.exceptions.RequestException as e:
        return "unknown"
    if not htmlStr:
        return "empty" # 没有爬取到信息
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
    id = account.id
    url = f'https://minesweeper.online/player/{id}'
    htmlStr = None
    try:
        response = requests.get(url=url, timeout=5,headers=headers)
        htmlStr = response.text
    except requests.exceptions.Timeout as e:
        return "timeout" # 请求超时
    except requests.exceptions.RequestException as e:
        return "unknown"
    if not htmlStr:
        return "empty" # 没有爬取到信息
    tree = etree.HTML(htmlStr)
    tree = tree.xpath('/html/body/div[3]/div[2]/div/div[1]/div[2]/div/div[4]/div/div[1]')[0]
    def formatXpath(text):
        return f'//strong[text()="{text}"]/../following-sibling::div/span/text()'
    def formatImgXpath(text,img,last):
        return f'//strong[text()="{text}"]/../following-sibling::div//img[@class="{img}"]{last}'
    def formatIXpath(text,i,last):
        return f'//strong[text()="{text}"]/../following-sibling::div//i[@class="{i}"]{last}'
    def stringToInt(values) -> int:
        return int(str(values[0]).replace(" ", "").replace("%", "")) if values else None
    def stringToFloat(values) -> float:
        return float(str(values[0]).replace(" ", "").replace("%", "")) if values else None
    values = tree.xpath(formatXpath("Trophies:"))
    account.trophy = int(values[0]) if values else None
    
    values = tree.xpath(formatImgXpath("Experience:","exp-icon icon-right", "/../text()"))
    account.experience = stringToInt(values)
    
    values = tree.xpath(formatImgXpath("Experience:","hp-icon icon-right", "/../../text()"))
    account.honour = stringToInt(values)
    
    values = tree.xpath(formatImgXpath("Resources:","coin-icon icon-right", "/../../text()"))
    account.minecoin = stringToInt(values)
    
    values = tree.xpath(formatImgXpath("Resources:","gem gem0 icon-right", "/../span/text()"))
    account.gem = stringToInt(values)
    
    values = tree.xpath(formatImgXpath("Resources:","arena-coin-icon icon-right", "/../span/text()"))
    account.coin = stringToInt(values)

    values = tree.xpath(formatIXpath("Resources:","fa fa-ticket ticket-right ticket0", "/../span/text()"))
    account.arena_ticket = stringToInt(values)
    
    values = tree.xpath(formatImgXpath("Resources:","parts-icon ", "/preceding-sibling::text()"))
    account.part = stringToInt(values)
    
    values = tree.xpath(formatImgXpath("Resources:","eq-icon", "/../span/text()"))
    account.equipment = stringToInt(values)
    
    values = tree.xpath(formatImgXpath("Arena points:","arena-icon ","/../text()"))
    account.arena_point = stringToInt(values)
    
    values = tree.xpath(formatImgXpath("Max difficulty:","diff-icon ","/../a/text()"))
    account.max_difficulty = stringToInt(values)
    
    values = tree.xpath(formatIXpath("Wins:","fa fa-flag wins-icon ","/../text()"))
    account.win = stringToInt(values)
    values = tree.xpath('//strong[text()="Last season:"]/../following-sibling::div//text()')
    if not values:
        values = tree.xpath('//strong[contains(text(),"Season")]/../..//text()')
    account.last_season = re.search(r'S(\d+)', ' '.join(values)).group(1) if values else None
    def formatSpanXpath(text,index):
        return f'//span[text()="{text}"]/../following-sibling::div[{index}]//text()'
    values = tree.xpath(formatSpanXpath("Beginner",1))
    account.b_t_ms = round(stringToFloat(values)*1000)
    
    values = tree.xpath(formatSpanXpath("Intermediate",1))
    account.i_t_ms = round(stringToFloat(values)*1000)
    
    values = tree.xpath(formatSpanXpath("Expert",1))
    account.e_t_ms = round(stringToFloat(values)*1000)
    
    values = tree.xpath(formatIXpath("Efficiency:","fa fa-dot-circle-o eff-icon level1","/../text()"))
    account.b_ioe = stringToFloat(values) / 100
    
    values = tree.xpath(formatIXpath("Efficiency:","fa fa-dot-circle-o eff-icon level2","/../text()"))
    account.i_ioe = stringToFloat(values) / 100
    
    values = tree.xpath(formatIXpath("Efficiency:","fa fa-dot-circle-o eff-icon level3","/../text()"))
    account.e_ioe = stringToFloat(values) / 100

    values = tree.xpath(formatIXpath("Mastery:","glyphicon glyphicon-flash mastery-icon mastery1","/../text()"))
    account.b_mastery = stringToInt(values)
    
    values = tree.xpath(formatIXpath("Mastery:","glyphicon glyphicon-flash mastery-icon mastery2","/../text()"))
    account.i_mastery = stringToInt(values)
    
    values = tree.xpath(formatIXpath("Mastery:","glyphicon glyphicon-flash mastery-icon mastery3","/../text()"))
    account.e_mastery = stringToInt(values)
    
    values = tree.xpath(formatIXpath("Win streak:","fa fa-crosshairs ws-icon ws1","/../text()"))
    account.b_winstreak = stringToInt(values)
    
    values = tree.xpath(formatIXpath("Win streak:","fa fa-crosshairs ws-icon ws2","/../text()"))
    account.i_winstreak = stringToInt(values)
    
    values = tree.xpath(formatIXpath("Win streak:","fa fa-crosshairs ws-icon ws3","/../text()"))
    account.e_winstreak = stringToInt(values)

    account.save()
    return ""
