# -*- coding: utf-8 -*-
from starlette.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

import config
from handlers import common_handler, admin_handler, merchant_handler, express_handler, message_handler
from utils import logger

app = FastAPI(
    title="我的商城",
    description="小程序购物商城",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# 导入路由模块
app.include_router(common_handler.router, tags=["公共模块"])
app.include_router(admin_handler.router, prefix="/admin", tags=["管理员模块"])
app.include_router(merchant_handler.router, prefix="/merchant", tags=["商户模块"])
app.include_router(express_handler.router, prefix="/express", tags=["快递公司模块"])
app.include_router(message_handler.router, tags=["消息实时通讯模块"])


@app.on_event("startup")
def app_start():
    logger.info("******************** App Start ********************")


@app.on_event("shutdown")
def app_shutdown():
    logger.info("******************** App Close ********************\n")


@app.get("/")
def test_websocket():
    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <button onclick="connect(event)">Connect</button>
            <br>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var input = document.getElementById("itemId")
                ws = new WebSocket("ws://localhost:6035/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
    return HTMLResponse(html)


if __name__ == "__main__":
    uvicorn.run("main:app", **config.app_config)
