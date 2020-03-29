# -*- coding: utf-8 -*-
"""
消息即时通讯模块: 从商户WebSocket读取消息并发布到小程序后台订阅的Redis主题，以及从商户后台订阅的Redis主题读取消息并发送给指定商户
定义通信消息体如下:
{
    "message_type": "消息类型， message: 普通消息   deal: 订单消息",
    "from_id": "发送方id",
    "from_name": "发送方名称",
    "to_id": "接收方id",
    "to_name": "接收方名称",
    "body" : {
        "type": "消息数据类型, text: 普通文本数据  jpg: jpg图片数据  png: png图片数据",
        "content": "消息内容， 如果type为图片类型， 则传图片Base64字符串"
    }
    "timestamp": "消息发送时间"
}
"""
import json
import threading
import asyncio
import websockets
from utils import msg_logger as logger
from utils.redis_util import redis_client
from utils.security_util import verify_token
from config import merchants_listener_topic, miniapp_listener_topic, merchants_message_queue, miniapp_message_queue, socket_config


class MessageHandler(threading.Thread):
    def __init__(self, thread_name):
        super().__init__()
        self.name = thread_name
        self.USERS = {}     # 保存当前在线的商户socket连接

        # 订阅merchants_listener_topic
        self.redis_subscriber = redis_client.pubsub()
        self.redis_subscriber.psubscribe(**{merchants_listener_topic: self.redis_listener})

    def run(self):
        # 重新设置事件循环为当前线程，否则get_event_loop会获取主线程事件循环
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        # 启动WebSocket Server
        loop.run_until_complete(websockets.serve(ws_handler=self.socket_listener, host=socket_config["host"],
                                                 port=socket_config["port"]))
        logger.info("WebSocket Server Started...")

        # 启动redis消息订阅者
        self.redis_subscriber.run_in_thread(sleep_time=0.1)
        logger.info("Redis Subscriber Started...")

        # 启动事件循环
        loop.run_forever()

    def register(self, merchant_id, websocket):
        self.USERS[merchant_id] = websocket

    def unregister(self, merchant_id):
        self.USERS.pop(merchant_id)

    def is_online(self, merchant_id):
        """
        检查商户是否在线
        """
        return merchant_id in self.USERS

    async def socket_listener(self, websocket, path):
        """
        监听商户WebSocket, 读取消息并发布至redis(小程序后端订阅该主题，再将消息发给小程序用户)
        消息流动路径: 商户WebSocket->Redis->小程序用户WebSocket
        :param websocket: 当前接入客户端socket
        :param path:
        """
        # 检查当前用户登录态，不合法的连接直接关闭
        try:
            cookies = websocket.request_headers.get("Cookie", None)
            if not cookies:
                raise Exception("非法连接!")
            logger.info(f"Cookies: {cookies}")
            cookie_arr = cookies.split(";")
            x_token = ""
            for cookie in cookie_arr:
                token_key, token_value = cookie.split("=")
                if token_key == "x_token":
                    x_token = token_value
                    break
            # 获取当前登录商户id
            cur_merchant_id = verify_token(x_token)
        except Exception as e:
            logger.error(str(e))
            return await websocket.close()
        logger.info(f"商户({cur_merchant_id})已连接!")
        self.register(cur_merchant_id, websocket)

        # 检查是否有发往该商户的离线消息
        offline_messages = redis_client.lrange(f"messages_for_merchant_{cur_merchant_id}", 0, -1)
        if len(offline_messages) > 0:
            logger.info(f"get offline messages: {offline_messages}")
            redis_client.ltrim(f"messages_for_merchant_{cur_merchant_id}", len(offline_messages), -1)
            for offline_message in offline_messages:
                await websocket.send(offline_message)

        # 处理socket输入
        try:
            async for message in websocket:
                """ 对于商户发来的消息 直接发往小程序后端即可 """
                # 将消息写入小程序后端消费队列
                redis_client.rpush(miniapp_message_queue, message)
                # 通知小程序后端有新消息到达
                redis_client.publish(miniapp_listener_topic, "message")
                logger.info(f"get a message from merchant_{cur_merchant_id}: {message}, send status: success")
        finally:
            self.unregister(cur_merchant_id)

    def redis_listener(self, msg):
        """
        订阅redis主题，读取小程序后端发来的消息并转发给具体商户
        消息流动路径: 小程序用户WebSocket->Redis->商户WebSocket
        :param msg: redis事件消息
        :return:
        """
        if msg["type"] not in ["message", "pmessage"]:
            return
        # 从消费队列获取新消息
        message = redis_client.lpop(merchants_message_queue)
        if message is None:
            return
        logger.info(f"get a message from miniapp: {message}")
        message_dict = json.loads(message)

        # 解析出消息要发往的商户
        target_merchant_id = int(message_dict["to_id"])

        if self.is_online(target_merchant_id):
            websocket = self.USERS.get(target_merchant_id)
            asyncio.wait(websocket.send(message))
        else:
            # 商户不在线时，通过在redis中为每个商户维护一个接收队列来存储离线消息，待下次商户登录时获取(暂时不做持久化存储)
            redis_client.rpush(f"messages_for_merchant_{target_merchant_id}", message)

