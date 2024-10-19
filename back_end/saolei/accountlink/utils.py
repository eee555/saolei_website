import re
from .models import AccountSaolei, AccountMinesweeperGames, AccountWorldOfMinesweeper, Platform
from datetime import datetime
from userprofile.models import UserProfile
import requests
from lxml import etree

def update_account(platform: Platform, id, user: UserProfile | None):
    if platform == Platform.SAOLEI:
        update_saolei_account(id, user)
    elif platform == Platform.MSGAMES:
        update_msgames_account(id, user)
    elif platform == Platform.WOM:
        update_wom_account(id, user)
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

def update_saolei_account(id, user: UserProfile | None):
    account = AccountSaolei.objects.filter(id=id).first()
    if not account:
        account = AccountSaolei.objects.create(id=id, parent=user)
    elif user:
        account.parent=user
    account.update_time = datetime.now()
    InfoHtmlStr = None
    VideoHtmlStr = None
    try:
        url = f'http://saolei.wang/Player/Info.asp?Id={id}'
        response = requests.get(url=url, timeout=5)
        response.encoding = 'GB2312'
        InfoHtmlStr = response.text

        url = f'http://saolei.wang/Video/Satus.asp?Id={id}'
        response = requests.get(url=url, timeout=5)
        response.encoding = 'GB2312'
        VideoHtmlStr = response.text

    except requests.exceptions.Timeout as e:
        # 请求超时
        pass
    except IndexError as e:
        # 解析html时超出索引
        pass
    except requests.exceptions.RequestException as e:
        # 其他错误
        pass
    # 给account的各attribute赋值
    if not InfoHtmlStr or not VideoHtmlStr:
        # 这两个都没有爬取到信息
        return
    tree = etree.HTML(InfoHtmlStr)
    values = tree.xpath('//span[@class="Sign"]/text()')
    account.name = values[0] if values else None
    
    values = tree.xpath('//td[@class="Text"]/span[@class="Highest"]/text()')
    account.total_views = int(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[1]/text()')
    account.b_t_ms = float(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[3]/text()')
    account.i_t_ms = float(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[5]/text()')
    account.e_t_ms = float(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/span[8]/text()')
    account.s_t_ms = float(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[2]/text()')
    account.b_b_cent = float(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[4]/text()')
    account.i_b_cent = float(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/a[6]/text()')
    account.e_b_cent = float(values[0]) if values else None
    
    values = tree.xpath('//tr/td[2]/span[9]/text()')
    account.s_b_cent = float(values[0]) if values else None
    
    tree = etree.HTML(VideoHtmlStr)
    values = tree.xpath('(//td[@class="Counters"])[1]/text()')
    account.beg_count = int(values[0]) if values else None
    
    values = tree.xpath('(//td[@class="Counters"])[2]/text()')
    account.int_count = int(values[0]) if values else None
    
    values = tree.xpath('(//td[@class="Counters"])[3]/text()')
    account.exp_count = int(values[0]) if values else None
    
    account.save()

def update_msgames_account(id, user: UserProfile | None):
    account = AccountMinesweeperGames.objects.filter(id=id).first()
    url = f'https://minesweepergame.com/profile.php?pid={id}'
    if not account:
        account = AccountMinesweeperGames.objects.create(id=id, parent=user)
    elif user:
        account.parent=user
    account.update_time = datetime.now()
    # 给account的各attribute赋值
    htmlStr = None
    try:
        url = f'https://minesweepergame.com/profile.php?pid={id}'
        response = requests.get(url=url, timeout=5)
        htmlStr = response.text
    except requests.exceptions.Timeout as e:
        # 请求超时
        pass
    except requests.exceptions.RequestException as e:
        # 其他错误
        pass
    if not htmlStr:
        # 没有爬取到信息
        return
    tree = etree.HTML(htmlStr)
    def getValue(text):
        values = tree.xpath(f'//td[text()="{text}"]/../td[2]/text()')
        return values[0] if values else None
    account.name = getValue('Name')
    account.local_name = getValue('Local Name')
    account.joined = getValue('Joined')
    account.save()

def update_wom_account(id, user: UserProfile | None):
    print(user)
    account = AccountWorldOfMinesweeper.objects.filter(id=id).first()
    url = f'https://minesweeper.online/player/{id}'
    if not account:
        account = AccountWorldOfMinesweeper.objects.create(id=id, parent=user)
    elif user:
        account.parent=user
    account.update_time = datetime.now()
    htmlStr = None
    try:
        response = requests.get(url=url, timeout=5)
        htmlStr = response.text
    except requests.exceptions.Timeout as e:
        # 请求超时
        pass
    except requests.exceptions.RequestException as e:
        # 其他错误
        pass
    if not htmlStr:
        # 没有爬取到信息
        return
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
    
    values = tree.xpath('//div[6]/div[2]/table/tbody/tr/td[11]/span/span/span/span/text()')
    account.equipment = ''.join(values) if values else None
    
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
    account.b_t_ms = stringToFloat(values)
    
    values = tree.xpath(formatSpanXpath("Intermediate",1))
    account.i_t_ms = stringToFloat(values)
    
    values = tree.xpath(formatSpanXpath("Expert",1))
    account.e_t_ms = stringToFloat(values)
    
    account.s_t_ms = account.b_t_ms + account.i_t_ms + account.e_t_ms
    
    values = tree.xpath(formatIXpath("Efficiency:","fa fa-dot-circle-o eff-icon level1","/../text()"))
    account.b_ioe = stringToFloat(values) / 100
    
    values = tree.xpath(formatIXpath("Efficiency:","fa fa-dot-circle-o eff-icon level2","/../text()"))
    account.i_ioe = stringToFloat(values) / 100
    
    values = tree.xpath(formatIXpath("Efficiency:","fa fa-dot-circle-o eff-icon level3","/../text()"))
    account.e_ioe = stringToFloat(values) / 100
    
    account.s_ioe = account.b_ioe + account.i_ioe + account.e_ioe
    
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
    # 给account的各attribute赋值
    account.save()
    