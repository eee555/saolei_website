import unittest
import time
from .wom import WOM
import json


class TestWOM(unittest.TestCase):

    def test_insert_video_id(self):
        self.count = 0
        # 创建 WOM 实例并传入 mock_callback
        wom = WOM(videoInfoFunc=self.callbackFunc, disConnectTime=10, raiseReConnectTime=60, errorFunc=self.errorFunc)
        wom.start()  # 启动 WOM

        wom.insertVideoId('3071736950')
        wom.insertVideoId('3071736950')
        time.sleep(5)
        # 断言当前是连接状态
        self.assertEqual(wom.isConnected(), True, "Connect")

        # 等待 20 秒
        time.sleep(20)
        # 断言当前是断开状态
        self.assertEqual(wom.isConnected(), False, "Disconnect")
        wom.insertVideoId('3071736950')

        # 再次等待 5 ，等待异步重连
        time.sleep(5)
        # 断言当前是连接状态
        self.assertEqual(wom.isConnected(), True, "Connect")

        time.sleep(20)
        # 确保总共调用了6次 callback
        self.assertEqual(self.count, 6, "Callback")
        wom.stop()
        time.sleep(5)
        # 断言当前是断开状态
        self.assertEqual(wom.isConnected(), False, "Disconnect")

    def callbackFunc(self, message):
        data = json.loads(message)
        if data[0][1] == 203:
            self.assertEqual(data[1][2][0]['id'],
                             3071736950, "Insert video Info 203")
        if data[0][1] == 214:
            self.assertEqual(data[1][2][0], 3071736950,
                             "Insert video Info 214")
        self.count += 1

    def errorFunc(self, e: Exception):
        print(f"Error: {e}")


if __name__ == '__main__':
    unittest.main()
