from typing import Callable
import websocket
import threading
import queue
import requests
import re
import time


class WOM:
    def __init__(self, callback: Callable, timeout: int = 10, reConnectTime: int = 60):
        self.__videoIdQueue = queue.Queue()
        self.__videoInfoQueue = queue.Queue()
        self.__callback = callback
        self.__ws = None
        self.__isOver = True
        self.__lastTime = time.time()
        self.__timeout = timeout
        self.__lock = threading.Lock()
        self.__reConnectTime = 60
        self.__isConnected = False
        self.__isConnectedLock = threading.Lock()
        self.__wsThread = threading.Thread(target=self.__wsThreadFunc)
        self.__callbackThread = threading.Thread(target=self.__callBackThreadFunc)
        self.__stopFlag = threading.Event()

    def __wsThreadFunc(self) -> None:
        while not self.__stopFlag.is_set():
            if self.__ws is None and self.__videoIdQueue.empty():
                time.sleep(0.1)
                continue
            if self.__ws and time.time() - self.__lastTime > self.__timeout and self.__videoIdQueue.empty() and self.__isOver:
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
                            videoId = self.__videoIdQueue.get()
                            message = self.formatMessage(
                                '42', f'["request",["EnterGameController.enterGameWsAction",[{videoId}],1000,683]]')
                            self.__ws.send(message)
                            self.__isOver = False
                            with self.__lock:
                                self.__lastTime = time.time()
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
                        if code == '0':
                            self.__ws.send('40')
                        if code == '40':
                            pass
                        if code == '42' and message == '["authorized",[]]':
                            isAuthenticated = True
                            with self.__isConnectedLock:
                                self.__isConnected = True
            except Exception as e:
                self.__ws = None
                time.sleep(self.__reConnectTime)

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
        self.__stopFlag.clear()
        self.__wsThread.start()
        self.__callbackThread.start()

    def insertVideoId(self, videoId):
        self.__videoIdQueue.put(videoId)
        
    def insertVideoIds(self, videoIds):
        for videoId in videoIds:
            self.__videoIdQueue.put(videoId)

    def stop(self):
        self.__isOver = True
        self.__stopFlag.set()
        self.__wsThread.join()
        self.__callbackThread.join()
        with self.__isConnectedLock:
            self.__isConnected = False

    def isConnected(self):
        with self.__isConnectedLock:
            return self.__isConnected


if __name__ == '__main__':
    def callback(message):
        print(message)
    wom = WOM(callback)
    wom.start()
    wom.insertVideoId('3071736950')
    wom.insertVideoId('3071736950')
    import time
    time.sleep(20)
    wom.insertVideoId('3071736950')

    print('over')
    wom.stop()
