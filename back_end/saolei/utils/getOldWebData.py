"""
# Author: ljzloser
# Date: 2024-08-11 23:35:28
# LastEditors: ljzloser
# LastEditTime: 2024-08-11 23:35:28
# FilePath: /back_end/saolei/scripts/getOldWebData.py
# Description: 用于获取老网站数据
"""
import requests
from enum import Enum
from abc import ABC, abstractmethod
from lxml import etree
import html
from typing import overload, Callable
import re
from datetime import datetime
import random


class Level(Enum):
    Beg = 0
    Int = 1
    Exp = 2

    def __format__(self, format_spec: str) -> str:
        return f'My_{self.name}.asp'


class Mode(Enum):
    Video = 0

    def __format__(self, format_spec: str) -> str:
        return self.name


class FormatUrl:
    __host: str = "http://saolei.wang"
    __userID: int

    def __init__(self, userID) -> None:
        self.__userID = userID

    @property
    def userID(self) -> int:
        return self.__userID

    @userID.setter
    def userID(self, userID: int):
        self.__userID = userID

    @property
    def host(self) -> str:
        return self.__host

    @host.setter
    def hostUrl(self, hostUrl: str):
        self.__host = hostUrl

    @property
    def BegVideoUrl(self) -> str:
        return self.get(Mode.Video, Level.Beg)

    @property
    def IntVideoUrl(self) -> str:
        return self.get(Mode.Video, Level.Int)

    @property
    def ExpVideoUrl(self) -> str:
        return self.get(Mode.Video, Level.Exp)

    def getShowUrl(self, mode: Mode = None, videoID: int = 0) -> str:
        return f'{self.host}/{mode}/Show.asp?Id={videoID}&tmp={random.randint(10000, 99999)}'

    def get(self, mode: Mode = None, level: Level = None, videoID: int = 0) -> str:
        """
        获取相关URL
        IF mode = Video THEN
            IF level != None THEN 获取指定等级的第一页列表
            ELSE 获取指定ID的录像下载链接
        ELSE
            返回空
        END
        Args:
            mode (Mode, optional): _description_. Defaults to None.
            level (Level, optional): _description_. Defaults to None.
            videoID (int, optional): _description_. Defaults to 0.

        Returns:
            str: _description_
        """
        match mode:
            case Mode.Video:
                if level is not None:
                    return f'{self.host}/{mode}/{level}?Id={self.userID}'
                else:

                    showUrl = self.getShowUrl(mode, videoID)
                    try:
                        response = requests.get(url=showUrl, timeout=5)
                        response.encoding = 'gb2312'
                        VideoUrl = re.search(
                            r"PlayVideo\('(.*?)'\)", response.text).group(1)
                        VideoUrl = f'{self.host}/{VideoUrl}'
                        return VideoUrl
                    except:
                        return ''

            case _:
                return ''


class BasePostData(ABC):
    """
    基类，用于获取数据
    """

    def __init__(self, userID, scheduleFunc: Callable[[any], bool] = None) -> None:
        self.userID = userID
        self.scheduleFunc = scheduleFunc
        self.errorFunc = None

    @abstractmethod
    def getData(self, *args, **kwargs) -> any:
        """
        获取数据

        Returns:
            any: 返回数据
        """
        pass

    def registerSchedule(self, scheduleFunc: Callable[[int], bool]):
        """
        注册回调函数用于更新进度
        Args:
            func (callable): 回调函数 如果返回False则终止并返回已经获取的数据，如果返回True则继续。
        """
        self.scheduleFunc = scheduleFunc

    def registerError(self, errorFunc: Callable[[Exception], None]):
        """
        注册错误函数
        Args:
            errorFunc (callable): 错误函数
        """
        self.errorFunc = errorFunc


class VideoData(BasePostData):
    """
    获取视频信息 BasePostData的子类
    """
    class Info:
        """
        视频信息
        """

        def __init__(self) -> None:
            self.dateTime: str
            self.bv: float
            self.bvs: float
            self.grade: float
            self.videoID: int
            self.level: str
            self.url: str
            self.showUrl: str
            self.mode = 0

    def __init__(self, userID, scheduleFunc: Callable[[int], None] = None) -> None:
        super().__init__(userID, scheduleFunc)

    @overload
    def getData(self, level: Level, lastTime: datetime) -> list[Info]:
        """
        获取视频信息

        Args:
            level (_type_, optional): 等级. Defaults to Level.
            lastTime (datetime, optional): 上次获取的时间. Defaults to datetime.min.

        Returns:
            list[Info]: 视频信息列表
        """
        pass

    def getData(self, *args, **kwargs) -> any:
        formatUrl = FormatUrl(self.userID)
        if isinstance(args[0], Level) and isinstance(args[1], datetime):
            lastTime = args[1]
            flag = True
            page = 1
            url = formatUrl.get(mode=Mode.Video, level=args[0])
            infos = []
            while flag:
                pageUrl = f'{url}&Page={page}&Save=1'
                try:
                    response = requests.get(url=pageUrl, timeout=5)
                    response.encoding = 'GB2312'
                    if response.status_code == 200:
                        match = re.search(r'<html>.*?<\/html>',
                                          response.text, re.DOTALL)
                        text = ''
                        if match:
                            text = match.group(0)
                        # html反转义
                        text = html.unescape(text).replace('\xa0', ' ')
                        tree = etree.HTML(text)
                        button = tree.xpath(
                            '/html/body/table/tr[3]/td/span/@onclick')
                        if button:
                            page += 1
                        else:
                            flag = False
                        videoInfos = tree.xpath(
                            '/html/body/table/tr/td/table/tr')

                        for i, videoInfo in enumerate(videoInfos, start=1):
                            videoUrl = videoInfo.xpath('./td[5]/a/@onclick')
                            if len(videoUrl) == 0:
                                continue
                            videoUrl = videoUrl[0]
                            match = re.search(r"Id=(\d+)", videoUrl)
                            videoID = match.group(1)
                            dataTime = videoInfo.xpath(
                                './td[1]/text()')[0].strip()
                            thisTime = datetime.strptime(
                                dataTime, '%Y年%m月%d日 %H:%M')
                            if thisTime < lastTime:
                                continue
                            if videoInfo.xpath('./td[6]/span/text()')[0] == "未审核!":
                                continue
                            info = self.Info()
                            info.dateTime = thisTime.strftime(
                                '%Y-%m-%d %H:%M:%S')
                            info.bv = float(videoInfo.xpath(
                                f'./td[3]/span[@id="BV_{i}"]/text()')[0])
                            info.bvs = float(videoInfo.xpath(
                                f'./td[4]/span[@id="BVS_{i}"]/text()')[0])
                            info.grade = float(videoInfo.xpath(
                                f'./td[5]/a[@id="Video_{i}"]/text()')[0])
                            info.mode = int('NF' in videoInfo.xpath(
                                './td[5]/span/text()'))
                            info.videoID = int(videoID)
                            info.level = args[0].name
                            info.url = formatUrl.get(
                                mode=Mode.Video, videoID=videoID)
                            info.showUrl = formatUrl.getShowUrl(
                                mode=Mode.Video, videoID=videoID)
                            infos.append(info)
                            if self.scheduleFunc:
                                if not self.scheduleFunc(info):
                                    return infos
                    else:
                        return infos
                except Exception as e:
                    if self.errorFunc:
                        self.errorFunc(e)
                    return infos
            return infos
        return []


if __name__ == '__main__':
    def scheduleFunc(num: int) -> bool:
        print(num)
        return False if num > 10 else True

    def errorFunc(error: Exception):
        print(error)
    data = VideoData(userID=18290, scheduleFunc=scheduleFunc)
    data.registerError(errorFunc=errorFunc)
    BegData = data.getData(Level.Beg, datetime.min)
    print(len(BegData))
