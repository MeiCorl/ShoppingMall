# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI

import config
from handlers import register_handler, login_handler
from utils import logger

app = FastAPI(
    title="我的商城",
    description="小程序购物商城",
    version="1.0.0"
)
app.include_router(register_handler.router)
app.include_router(login_handler.router)

if __name__ == "__main__":
    # uvicorn.run(app, port=5000, log_level="info")
    logger.info("----- App Start ----")
    uvicorn.run("main:app", **config.app_config)
