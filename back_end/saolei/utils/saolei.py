from datetime import datetime, timedelta, timezone
from lxml import etree
import requests
from bs4 import BeautifulSoup, element
import re
from .exceptions import ExceptionToResponse


SAOLEI_LEVEL = {
    'b': 'Beg',
    'i': 'Int',
    'e': 'Exp',
}
SAOLEI_TEXT2LEVEL = {
    '初级': 'b',
    '中级': 'i',
    '高级': 'e',
}

class SaoleiVideoInfo:
    id: int
    level: str
    bv: int
    timems: int
    nf: bool
    upload_time: datetime
    verified: bool

    def __init__(self, id: int, level: int, bv: int, timems: int, nf: bool, upload_time: datetime, verified: bool):
        self.id = id
        self.level = level
        self.bv = bv
        self.timems = timems
        self.nf = nf
        self.upload_time = upload_time
        self.verified = verified

    def dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'bv': self.bv,
            'timems': self.timems,
            'nf': self.nf,
            'upload_time': self.upload_time,
            'verified': self.verified
        }

    @property
    def url(self):
        return f'http://saolei.wang/Video/Show.asp?Id={self.id}'

    def get_download_url(self):
        response = requests.get(url=self.url, timeout=5)
        response.encoding = 'GB2312'
        if response.text == '''<script language="JavaScript">alert('此录象不存在!');</script><script language=JavaScript>top.location=top.location</script>''':
            self.verified = False
            return None
        if '此录像尚未通过审核！' in response.text or '为什么冻结？' in response.text:
            self.verified = False
        return 'http://saolei.wang/' + re.search(r"PlayVideo\('([^']+)'\)", response.text).group(1)


class SaoleiUserInfo:
    user_id: int

    def __init__(self, saolei_id: int):
        self.user_id = saolei_id

    @property
    def profile_url(self):
        return f'http://saolei.wang/Player/Index.asp?Id={self.user_id}'
    
    @property
    def info_url(self):
        return f'http://saolei.wang/Player/Info.asp?Id={self.user_id}'
    
    @property
    def stat_url(self):
        return f'http://saolei.wang/Player/Satus.asp?Id={self.user_id}'
    
    @property
    def bio_url(self):
        return f'http://saolei.wang/Player/More.asp?Id={self.user_id}'
    
    @property
    def video_count_url(self):
        return f'http://saolei.wang/Video/Satus.asp?Id={self.user_id}'
    
    @property
    def diary_url(self):
        return f'http://saolei.wang/Player/History_List.asp?Id={self.user_id}'
    
    @property
    def new_post_url(self):
        return f'http://saolei.wang/BBS/My_New.asp?Id={self.user_id}'
    
    @property
    def star_post_url(self):
        return f'http://saolei.wang/BBS/My_Nice.asp?Id={self.user_id}'
    
    @property
    def avatar_url(self):
        return f'http://saolei.wang/Models/Images/Player/{self.user_id}.jpg'
    
    def news_url(self, level: str = '', page: int = 1):
        if level == '':
            return f'http://saolei.wang/News/My.asp?Id={self.user_id}&Page={page}'
        return f'http://saolei.wang/News/My_{level}.asp?Id={self.user_id}&Page={page}'
    
    def videos_url(self, level: str = '', order: str = 'Time', page: int = 1):
        # order in ['Time', 'Score', '3BV', '3BVS', 'Comment']
        if level == '':
            return f'http://saolei.wang/Video/My.asp?Id={self.user_id}&Order={order}&Page={page}'
        return f'http://saolei.wang/Video/My_{level}.asp?Id={self.user_id}&Order={order}&Page={page}'


class SaoleiUtils:
    @staticmethod
    def parse_video_row(row: element.Tag):
        cols = row.find_all('td')

        upload_time = datetime.strptime(cols[0].get_text(strip=True), '%Y年%m月%d日\xa0%H:%M').replace(tzinfo=timezone(timedelta(hours=8)))

        bv = re.search(r"3BV=(\d+)", cols[2].get_text(strip=True)).group(1)

        span_tags = cols[4].find_all('span')
        level = SAOLEI_TEXT2LEVEL[span_tags[0].get_text(strip=True)]
        nf =  len(span_tags) > 1 and span_tags[1].get_text(strip=True) == 'NF'

        a_tag = cols[4].find('a')
        timems = int(a_tag.get_text(strip=True).replace('.', '')) * 10
        video_id = int(re.search(r"/Video/Show\.asp\?Id=(\d+)", a_tag.get('onclick')).group(1))

        verified = cols[5].get_text(strip=True).startswith('评论')

        return SaoleiVideoInfo(
            id=video_id,
            level=level,
            bv=bv,
            timems=timems,
            nf=nf,
            upload_time=upload_time,
            verified=verified
        )


    @staticmethod
    def get_video_list(url: str):
        response = requests.get(url=url, timeout=5)
        response.encoding = 'GB2312'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the inner table that holds all the data rows
        tables = soup.find_all('table')
        if len(tables) < 2:
            return []
        table = tables[1]  # second table (the first is the 575px wrapper)
        rows = table.find_all("tr")

        return [SaoleiUtils.parse_video_row(row) for row in rows]