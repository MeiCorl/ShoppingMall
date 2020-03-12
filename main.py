# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer

import config
from handlers import register_handler, login_handler, admin_handler
from utils import logger

app = FastAPI(
    title="我的商城",
    description="小程序购物商城",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


# 导入路由模块
app.include_router(register_handler.router)
app.include_router(login_handler.router)
app.include_router(admin_handler.router, dependencies=[Depends(get_token_header)])

if __name__ == "__main__":
    logger.info("----- App Start ----")
    uvicorn.run("main:app", **config.app_config)
