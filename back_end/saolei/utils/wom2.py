from abc import ABC, abstractmethod
import json
import queue
import re
import threading
import time
from typing import Any, Callable, List, Optional, Tuple, Union

import requests
import websocket


class WOM2Exception(Exception):
    pass


# ============ 示例数据类 ============

class WOM2Data(ABC):
    """数据帧基类"""
    _data_name: str = ''
    """数据帧名称"""
    _seq: int = 1000
    """数据帧序号"""
    _data_type_num: int = 0
    """数据帧类型"""

    @abstractmethod
    def from_string(self, data: str):
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

    @property
    def seq(self) -> int:
        """数据帧序号"""
        return self._seq

    @property
    def data_name(self) -> str:
        """数据帧名称"""
        return self._data_name

    @property
    def data_type_num(self) -> int:
        """数据帧类型"""
        return self._data_type_num


class IWOM2Request(WOM2Data):
    """请求基类"""
    _data_name: str = 'request'
    _request_num: int = None


class IWOM2Response(WOM2Data):
    """响应基类"""
    _data_name: str = 'response'
    _request_num: int = None


class WOM2Request_42(IWOM2Request):
    """42 类型请求示例"""
    _request_type: str = ''
    _params: List[Any] = []
    _unknown_num: int = 0
    _data_type_num: int = 42

    def __init__(self, request_type: str, params: List[Any], unknown_num: int = 0) -> None:
        super().__init__()
        self._request_type = request_type
        self._params = params
        self._unknown_num = unknown_num

    @property
    def request_type(self) -> str:
        return self._request_type

    @property
    def params(self) -> List[Any]:
        return self._params

    @property
    def unknown_num(self) -> int:
        return self._unknown_num

    def to_json(self) -> List[Any]:
        return [self._data_name, [self._request_type, self._params, self._seq, self._unknown_num]]

    def to_string(self) -> str:
        return str(self._data_type_num) + json.dumps(self.to_json())

    def from_string(self, data: str):
        reStr = r'^(\d+)(.*)$'
        result = re.findall(reStr, data)[0]
        if result:
            if self._data_type_num != 42:
                raise ValueError("Invalid data type number")
            self._data_type_num = int(result[0])
            self.from_json(json.loads(result[1]))
        else:
            raise ValueError("Invalid data")

    def from_json(self, json_data: List[Any]):
        self._request_type = json_data[1][0]
        self._params = json_data[1][1]
        self._seq = json_data[1][2]
        self._unknown_num = json_data[1][3]


class WOM2Response_42(IWOM2Response):
    """42 类型响应示例"""
    _unknown_num: int = 0
    _data: Any = None
    _data_type_num: int = 42

    def __init__(self) -> None:
        super().__init__()

    def from_string(self, data: str):
        reStr = r'^(\d+)(.*)$'
        result = re.findall(reStr, data)[0]
        if result:
            self._data_type_num = int(result[0])
            self.from_json(json.loads(result[1]))
            if self._data_type_num != 42:
                raise ValueError("Invalid data type number")
        else:
            raise ValueError("Invalid data")

    def from_json(self, json_data: List[Any]):
        self._seq = json_data[1][0]
        self._unknown_num = json_data[1][1]
        self._data = json_data[1][2]

    def to_json(self) -> List[Any]:
        return [self._data_name, [self._seq, self._unknown_num, self._data]]

    def to_string(self) -> str:
        return str(self._data_type_num) + json.dumps(self.to_json())

    @property
    def data(self) -> Any:
        return self._data

# ============ WOM2 客户端 ============


class WOM2:
    """同步 WebSocket 客户端，用于与 WOM 服务器通信"""

    def __init__(self, disconnect_time: int = 10, reconnect_time: int = 60, error_callback: Callable[[Exception], None] = None):
        """
        初始化 WOM2 类

        Args:
            disconnect_time: 最后一次请求后的空闲断开时间
            reconnect_time: 连接错误后的重试间隔
            error_callback: 错误回调函数
        """
        self.__disconnect_time = disconnect_time
        self.__reconnect_time = reconnect_time
        self.__error_callback = error_callback

        self.__ws = None
        self.__last_time = time.time()
        self.__is_connected = False
        self.__is_authenticated = False
        self.__lock = threading.Lock()
        self.__connected_lock = threading.Lock()

        # 响应队列：存放原始消息字符串
        self.__response_queue: queue.Queue[str] = queue.Queue()

        # 接收线程（daemon 线程，主线程退出时自动终止）
        self.__stop_flag = threading.Event()
        self.__receive_thread = threading.Thread(
            target=self.__receive_thread_func, daemon=True)

    def __enter__(self):
        self.start()
        if self.wait_for_connection():
            return self
        self.stop()
        raise WOM2Exception("Failed to connect to WOM server")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        # 返回 False 让异常继续向上传播
        return False

    def start(self):
        """启动客户端"""
        self.__stop_flag.clear()
        self.__receive_thread.start()

    def stop(self):
        """停止客户端"""
        self.__stop_flag.set()
        if self.__ws:
            self.__ws.close()
            self.__ws = None
        with self.__connected_lock:
            self.__is_connected = False
        self.__is_authenticated = False

    def __receive_thread_func(self):
        """接收消息的线程"""
        while not self.__stop_flag.is_set():
            try:
                if self.__ws is None:
                    if time.time() - self.__last_time > self.__disconnect_time:
                        time.sleep(0.1)
                        continue

                    # 建立连接
                    self.__connect()
                    time.sleep(0.1)
                    continue

                # 接收消息
                message = self.__ws.recv()
                data_type_num, raw_data = self.__parse_message(message)

                if data_type_num == '2':
                    self.__ws.send('3')
                elif data_type_num == '0':
                    self.__ws.send('40')
                elif data_type_num == '40':
                    pass
                elif data_type_num == '42':
                    if raw_data == '["authorized",[]]':
                        self.__is_authenticated = True
                        with self.__connected_lock:
                            self.__is_connected = True
                    else:
                        # 将原始消息放入队列
                        self.__response_queue.put(message)

                # 检查空闲断开
                if time.time() - self.__last_time > self.__disconnect_time:
                    self.__ws.close()
                    self.__ws = None
                    with self.__connected_lock:
                        self.__is_connected = False
                    self.__is_authenticated = False

            except Exception as e:
                self.__ws = None
                with self.__connected_lock:
                    self.__is_connected = False
                self.__is_authenticated = False
                if self.__error_callback:
                    self.__error_callback(e)
                time.sleep(self.__reconnect_time)

    def __connect(self):
        """建立 WebSocket 连接"""
        try:
            response = requests.get(
                'https://minesweeper.online/authorize?session=')
            data = response.json()
            ws_url = f"wss://main{int(data['userId']) % 10 + 1}.minesweeper.online/mine-websocket/?authKey={data['authKey']}&session={data['session']}&userId={data['userId']}&EIO=4&transport=websocket"
            self.__ws = websocket.create_connection(ws_url)
            with self.__connected_lock:
                self.__is_connected = True
        except Exception as e:
            self.__ws = None
            if self.__error_callback:
                self.__error_callback(e)
            raise

    def __parse_message(self, message: str) -> Tuple[str, str]:
        """解析消息，返回 (data_type_num, raw_data)"""
        if message == '':
            return '', ''
        re_str = r'^(\d+)(.*)$'
        result = re.findall(re_str, message)
        if result:
            return result[0][0], result[0][1]
        return '', ''

    def request(self, request: Union[str, IWOM2Request], seq: int = None, timeout: int = 10) -> List[str]:
        """
        同步发送请求并等待响应

        Args:
            request: 请求字符串或请求对象
            seq: 序列号（如果 request 是字符串则需要提供）
            timeout: 超时时间（秒）

        Returns:
            原始响应字符串，超时返回 None。用户需要根据数据类型自行解析。
        """
        if request is None:
            raise ValueError("request is None")
        responses = []
        # 处理不同类型的请求
        if isinstance(request, str):
            message = request
            target_seq = seq
            if target_seq is None:
                raise ValueError("seq is required when request is a string")
        else:
            message = request.to_string()
            target_seq = request.seq

        # 发送请求
        if self.__ws is None:
            self.__connect()

        self.__ws.send(message)

        with self.__lock:
            self.__last_time = time.time()

        # 等待响应
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                remaining_time = timeout - (time.time() - start_time)
                if remaining_time <= 0:
                    return None

                response_msg = self.__response_queue.get(
                    timeout=remaining_time)

                # 解析响应获取 seq
                parsed_seq = self.__extract_seq(response_msg)
                responses.append(response_msg)
                # 验证序列号是否一致
                if parsed_seq == target_seq:
                    return responses

            except queue.Empty:
                continue

        raise WOM2Exception("Timeout")

    def __extract_seq(self, message: str) -> Optional[int]:
        """
        从消息中提取序列号

        Args:
            message: 原始消息字符串

        Returns:
            序列号，如果无法解析则返回 None
        """
        try:
            _, raw_data = self.__parse_message(message)
            if not raw_data:
                return None

            # 尝试解析 JSON
            data = json.loads(raw_data)

            # 响应格式: ['response', [seq, unknown_num, data]]
            if isinstance(data, list) and len(data) >= 2 and data[0] == 'response':
                return data[1][0]

            return None
        except (json.JSONDecodeError, IndexError, KeyError, TypeError):
            return None

    def is_connected(self) -> bool:
        """检查是否已连接"""
        with self.__connected_lock:
            return self.__is_connected

    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.__is_authenticated

    def wait_for_connection(self, timeout: int = 30) -> bool:
        """
        等待连接和认证成功

        Args:
            timeout: 超时时间（秒）

        Returns:
            是否在超时时间内连接并认证成功
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.__is_connected and self.__is_authenticated:
                return True
            time.sleep(0.1)
        return False

    def request_video_info(self, video_id: int | str, timeout: int = 10) -> Optional[str]:
        """
        请求视频信息（便捷方法，使用 WOM2Request_42）

        Args:
            video_id: 视频 ID
            timeout: 超时时间（秒）

        Returns:
            原始响应字符串，超时返回 None
        """
        if video_id is None:
            raise ValueError("video_id is None")

        request = WOM2Request_42(
            'EnterGameController.enterGameWsAction',
            [video_id],
            None,
        )

        return self.request(request, timeout=timeout)


if __name__ == '__main__':
    # 使用上下文管理器，会自动等待连接成功
    with WOM2() as wom:

        # 使用自定义请求
        print("获取录像信息")  # noqa: T201
        request = WOM2Request_42(
            'EnterGameController.enterGameWsAction',
            [3],
            683,
        )
        responses = wom.request(request, timeout=50)
        response1 = WOM2Response_42()
        response2 = WOM2Response_42()
        response1.from_string(responses[0])
        response2.from_string(responses[1])
        print(response1.data)  # noqa: T201
        print(response2.data)  # noqa: T201

        request = WOM2Request_42(
            'PlayersOnlineController.getPlayersOnlineCountWsAction',
            [],
            931,
        )
        print("获取在线人数")  # noqa: T201
        responses = wom.request(request, timeout=50)
        response1 = WOM2Response_42()
        response1.from_string(responses[0])
        print(response1.data)  # noqa: T201
