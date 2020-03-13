# -*- coding: utf-8 -*-
import uvicorn

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

import config
from handlers import register_handler, login_handler, logout_handler, admin_handler
from utils import logger

app = FastAPI(
    title="我的商城",
    description="小程序购物商城",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# 导入路由模块
app.include_router(register_handler.router)
app.include_router(login_handler.router)
app.include_router(logout_handler.router)
app.include_router(admin_handler.router, prefix="/admin", tags=["admin"])

if __name__ == "__main__":
    logger.info("----- App Start ----")
    uvicorn.run("main:app", **config.app_config)
