# -*- coding: utf-8 -*-
"""
消息即时通讯模块: 通过WebSocket和Redis消息订阅实现小程序端用户与Web端商户间多对多实时通讯
"""
from starlette import status
from starlette.websockets import WebSocket
from fastapi import APIRouter, Cookie

from utils.security_util import verify_token
from utils import logger

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, x_token: str = Cookie(...)):
    # 验证用户是否登录
    try:
        cur_merchant_id = verify_token(x_token)
    except Exception as e:
        # WebSocket中抛HTTP异常无效，因此当用户登录态验证失败时直接关闭websocket
        logger.error(str(e))
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    logger.info(f"{cur_merchant_id}发来一条消息")
    await websocket.accept()
    logger.info(f"客户端已连接")
    # while True:
    data = websocket.receive_text()
    logger.info(f"消息已接收: {data}")
    await websocket.send_text(f"you send")

