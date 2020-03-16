# -*- coding: utf-8 -*-
"""
消息即时通讯模块: 从商户WebSocket读取消息并发布到Redis主题
"""
import json
import threading
import asyncio
import websockets
from utils import logger
from utils.redis_util import redis_client


class MessageHandler(threading.Thread):
    def __init__(self, thread_name):
        super().__init__()
        self.name = thread_name
        self.STATE = {'value': 0}
        self.USERS = set()

        self.redis_subscriber = redis_client.pubsub()
        self.redis_subscriber.psubscribe(**{'test': self.callback})

    def run(self):
        # 重新设置事件循环为当前线程，否则get_event_loop会获取主线程事件循环
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        # 启动WebSocket Server
        loop.run_until_complete(websockets.serve(ws_handler=self.socket_listener, host='127.0.0.1', port=6789))
        logger.info("WebSocket Server Started...")

        # 启动redis消息订阅者
        self.redis_subscriber.run_in_thread(sleep_time=0.01)
        logger.info("Redis Subscriber Started...")

        # 启动事件循环
        loop.run_forever()

    def state_event(self):
        return json.dumps({'type': 'state', **self.STATE})

    def users_event(self):
        return json.dumps({'type': 'users', 'count': len(self.USERS)})

    async def notify_state(self):
        if self.USERS:
            message = self.state_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_users(self):
        if self.USERS:
            message = self.users_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def register(self, websocket):
        self.USERS.add(websocket)
        await self.notify_users()

    async def unregister(self, websocket):
        self.USERS.remove(websocket)
        await self.notify_users()

    async def socket_listener(self, websocket, path):
        # 监听商户WebSocket, 读取消息并发布至redis(小程序后端订阅该主题，再将消息发给小程序用户)
        # 消息流动路径: 商户WebSocket->Redis->小程序用户WebSocket
        await self.register(websocket)
        try:
            await websocket.send(self.state_event())
            async for message in websocket:
                data = json.loads(message)
                if data['action'] == 'minus':
                    self.STATE['value'] -= 1
                    await self.notify_state()
                elif data['action'] == 'plus':
                    self.STATE['value'] += 1
                    await self.notify_state()
                else:
                    logger.error(
                        "unsupported event: {}", data)
        finally:
            await self.unregister(websocket)

    @staticmethod
    def callback(message):
        # 订阅redis主题，读取小程序后端发来的消息并转发给具体商户
        # 消息流动路径: 小程序用户WebSocket->Redis->商户WebSocket
        logger.info(f"{message} is expired！")

