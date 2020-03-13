# -*- coding: utf-8 -*-
"""
商户登录模块
"""
import json
from datetime import timedelta
from starlette.responses import Response
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import config
import utils.json_encoder
from handlers import make_response
from models.merchant import Merchant
from decorators import log_filter
from utils import logger, security_util
from utils.db_util import create_session
from utils.redis_util import redis_client

router = APIRouter()


@router.post("/login")
@log_filter
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(create_session)):
    """
     用户登录，提交方式采用Form表单提交
    :param session:
    :param response:
    :param form_data: 表单数据，包含username和password(本系统中username为手机号）
    :return: 登录成功返回token和商户类型
    """
    ret_code = 0
    ret_msg = "success"
    phone = form_data.username
    password = form_data.password

    try:
        # 查商户是否存在即密码是否正确
        merchant = session.query(Merchant).filter(Merchant.phone == phone).one_or_none()
        if merchant is None:
            session.commit()
            return make_response(-1, f"用户({phone})不存在!")
        if not security_util.verify_password(password, merchant.password):
            session.commit()
            return make_response(-1, "密码错误!")

        # 生成访问token
        access_token_expires = timedelta(hours=config.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = security_util.create_access_token(
            data={"merchant_id": merchant.id}, expires_delta=access_token_expires
        )
        logger.info("token: " + access_token)
        response.set_cookie("x_token", access_token, httponly=True)
        response.set_cookie("merchant_type", merchant.merchant_type)

        # 商户信息存入redis
        redis_client.hset("merchants", merchant.id, json.dumps(merchant.to_dict(), cls=utils.json_encoder.JsonEncoder))

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


