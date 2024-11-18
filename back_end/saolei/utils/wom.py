from typing import Callable
import websocket
import threading
import queue
import requests
import re
import time


class WOM:
    def __init__(self, videoInfoFunc: Callable[[str], None], disConnectTime: int = 10, raiseReConnectTime: int = 60, errorFunc: Callable[[Exception], None] = None):
        """
        初始化 WOM 类。

        args:
        - videoInfoFunc (Callable): 当接收到新的视频信息时调用的回调函数.
        - disConnectTime (int): 最后一次回调函数后的等待时间.如果超过这个时间,将断开连接.
        - raiseReConnectTime (int): 连接出现错误后重试的间隔.
        - errorFunc (Callable): 错误回调函数.
        Returns:
        - None
        """
        if videoInfoFunc is None:
            if not isinstance(videoInfoFunc,Callable):
                raise ValueError("videoInfoFunc is not None and type is callable")
        self.__videoIdQueue = queue.Queue()
        self.__videoInfoQueue = queue.Queue()
        self.__callback = videoInfoFunc
        self.__ws = None
        self.__isOver = True
        self.__lastTime = time.time()
        self.__disConnectTime = disConnectTime
        self.__lock = threading.Lock()
        self.__raiseReConnectTime = raiseReConnectTime
        self.__isConnected = False
        self.__isConnectedLock = threading.Lock()
        self.__wsThread = threading.Thread(target=self.__wsThreadFunc)
        self.__callbackThread = threading.Thread(
            target=self.__callBackThreadFunc)
        self.__stopFlag = threading.Event()
        self.__errorCallback = errorFunc

    def registerErrorCallback(self, callback: Callable[[Exception], None]):
        """
        注册错误回调函数,不是必须的，但是推荐使用
        """
        self.__errorCallback = callback

    def __wsThreadFunc(self) -> None:
        while not self.__stopFlag.is_set():
            if self.__ws is None and self.__videoIdQueue.empty():
                time.sleep(0.1)
                continue
            if self.__ws and time.time() - self.__lastTime > self.__disConnectTime and self.__videoIdQueue.empty() and self.__isOver:
                self.__ws.close()
                self.__ws = None
                with self.__isConnectedLock:
                    self.__isConnected = False
                time.sleep(0.1)
                continue
            try:
                if self.__ws:
                    code, message = self.parseMessage(self.__ws.recv())
                    if code == '2':
                        self.__ws.send('3')
                    elif code == '42' and message == '["response",[1000,1,[]]]':
                        self.__isOver = True
                    elif code == '42':
                        self.__videoInfoQueue.put(message)
                    if self.__isOver:
                        if not self.__videoIdQueue.empty():
                            try:
                                videoId: int|str = self.__videoIdQueue.get()
                                message = self.formatMessage(
                                    '42', f'["request",["EnterGameController.enterGameWsAction",[{videoId}],1000,683]]')
                                self.__ws.send(message)
                                self.__isOver = False
                                with self.__lock:
                                    self.__lastTime = time.time()
                            except Exception as e:
                                self.__ws = None
                                self.insertVideoId(videoId)
                                if self.__errorCallback:
                                    self.__errorCallback(e)
                                time.sleep(self.__raiseReconnectTime)
                else:
                    response = requests.get(
                        'https://minesweeper.online/authorize?session=')
                    data = response.json()
                    wsUrl = f"wss://main{int(data['userId'])% 10 + 1}.minesweeper.online/mine-websocket/?authKey={data['authKey']}&session={data['session']}&userId={data['userId']}&EIO=4&transport=websocket"
                    self.__ws = websocket.create_connection(wsUrl)
                    isAuthenticated = False
                    while not isAuthenticated:
                        code, message = self.parseMessage(self.__ws.recv())
                        if code == '2':
                            self.__ws.send('3')
                        elif code == '0':
                            self.__ws.send('40')
                        elif code == '40':
                            pass
                        elif code == '42' and message == '["authorized",[]]':
                            isAuthenticated = True
                            with self.__isConnectedLock:
                                self.__isConnected = True
            except Exception as e:
                self.__ws = None
                if self.__errorCallback:
                    self.__errorCallback(e)
                time.sleep(self.__raiseReConnectTime)

    def __callBackThreadFunc(self):
        while not self.__stopFlag.is_set() or not self.__videoInfoQueue.empty():
            if not self.__videoInfoQueue.empty():
                with self.__lock:
                    self.__lastTime = time.time()
                self.__callback(self.__videoInfoQueue.get())
            else:
                time.sleep(1)

    @staticmethod
    def formatMessage(code, message):
        return f'{code}{message}'

    @staticmethod
    def parseMessage(message) -> tuple[str, str]:
        if message == '':
            return '', ''
        reStr = r'^(\d+)(.*)$'
        # 取出第一部分和第二部分
        result = re.findall(reStr, message)[0]
        if result:
            return result[0], result[1]
        else:
            return '', ''

    def start(self):
        """启动"""
        self.__stopFlag.clear()
        self.__wsThread.start()
        self.__callbackThread.start()

    def insertVideoId(self, videoId: str | int):
        """插入一个请求的视频ID"""
        if videoId is None:
            raise ValueError("videoId is None")
        self.__videoIdQueue.put(videoId)

    def insertVideoIds(self, videoIds: list[str | int]):
        """插入多个请求的视频ID"""
        if videoIds is None:
            raise ValueError("videoIds is None")
        elif not isinstance(videoIds, list):
            raise ValueError("videoIds is not a list")
        for videoId in videoIds:
            self.__videoIdQueue.put(videoId)

    def stop(self):
        """停止，但是会等待已经接收到的数据全部回调完成"""
        self.__isOver = True
        self.__stopFlag.set()
        self.__wsThread.join()
        self.__callbackThread.join()
        with self.__isConnectedLock:
            self.__isConnected = False

    def isConnected(self):
        """检查是否已连接,请求视频信息时，无需判断是否已连接"""
        with self.__isConnectedLock:
            return self.__isConnected


if __name__ == '__main__':
    def callback(message):
        print(message)
    wom = WOM(callback)
    wom.start()
    wom.insertVideoId('1')
    wom.insertVideoId('1')
    import time
    time.sleep(20)
    wom.insertVideoId('1')

    print('over')
    wom.stop()
