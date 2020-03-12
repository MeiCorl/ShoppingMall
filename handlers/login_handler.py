# -*- coding: utf-8 -*-
"""
商户登录、登出模块
"""
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from config import ACCESS_TOKEN_EXPIRE_HOURS
from handlers import make_response
from models.merchant import Merchant
from decorators import log_filter
from utils import logger, db_util, security_util

router = APIRouter()


@router.post("/login")
@log_filter
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
     用户登录，提交方式采用Form表单提交
    :param form_data: 表单数据，包含username和password(本系统中username为手机号）
    :return: 登录成功返回token和商户类型
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = None

    phone = form_data.username
    password = form_data.password

    session = db_util.create_session()
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
        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = security_util.create_access_token(
            data={"merchant_id": merchant.id}, expires_delta=access_token_expires
        )

        ret_data["access_token"] = access_token
        ret_data["token_type"] = "bearer"
        ret_data["merchant_type"] = merchant.merchant_type
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    finally:
        session.close()
    return make_response(ret_code, ret_msg, ret_data)


@router.post("/logout")
def login():
    return "logout"
