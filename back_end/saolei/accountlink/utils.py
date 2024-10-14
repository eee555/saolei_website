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
        response = requests.get(url=url)
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
    values = tree.xpath('/html/body/div[3]/div/div/div/div[2]/table/tr[1]/td[2]/text()')
    account.name = values[0] if values else None
    
    values = tree.xpath('/html/body/div[3]/div/div/div/div[2]/table/tr[2]/td[2]/text()')
    account.local_name = values[0] if values else None
    
    values = tree.xpath('/html/body/div[3]/div/div/div/div[2]/table/tr[6]/td[2]/text()')
    account.joined = values[0] if values else None
    account.save()

def update_wom_account(id, user: UserProfile | None):
    print(user)
    account = AccountWorldOfMinesweeper.objects.filter(id=id).first()
    url = f'https://minesweeper.online/cn/player/{id}'
    if not account:
        account = AccountWorldOfMinesweeper.objects.create(id=id, parent=user)
    elif user:
        account.parent=user
    account.update_time = datetime.now()
    # 给account的各attribute赋值
    account.save()
    