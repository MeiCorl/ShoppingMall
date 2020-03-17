# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from starlette.staticfiles import StaticFiles

import config
from handlers import common_handler, admin_handler, merchant_handler, express_handler
from utils import app_logger as logger
from message.message_handler import MessageHandler

app = FastAPI(
    title="我的商城",
    description="小程序购物商城",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")

msg_handler = MessageHandler("WebSocket Server")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# 导入路由模块
app.include_router(common_handler.router, tags=["公共模块"])
app.include_router(admin_handler.router, prefix="/admin", tags=["管理员模块"])
app.include_router(merchant_handler.router, prefix="/merchant", tags=["商户模块"])
app.include_router(express_handler.router, prefix="/express", tags=["快递公司模块"])


@app.on_event("startup")
def app_start():
    logger.info("******************** App Start ********************")


@app.on_event("shutdown")
def app_shutdown():
    logger.info("******************** App Close ********************\n")


if __name__ == "__main__":
    msg_handler.start()
    uvicorn.run("main:app", **config.app_config)
