# -*- coding: utf-8 -*-
"""
公共模块
"""
import json
import datetime
import sqlalchemy.exc
from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import config
from utils.json_encoder import JsonEncoder
from handlers import make_response
from models.merchant import Merchant
from decorators import log_filter
from utils import app_logger as logger
from utils import security_util, validation_utils
from utils.db_util import create_session
from utils.security_util import get_login_merchant
from consts import MerchantTypeDesc
from utils.redis_util import redis_client

router = APIRouter()


class RegisterModel(BaseModel):
    merchant_name: str = Field(..., title="商户名称", max_length=128)
    merchant_type: int = Field(..., title="商户类型, 1: 普通商户 2: 快递商户")
    logo: str = Field("", title="商户logo, 普调商户需要传", max_length=256)
    description: str = Field("", title="商户简介, 普调商户需要传", max_length=1024)
    building: str = Field("", title="商户所在楼栋, 普调商户需要传", max_length=1)
    floor: int = Field(0, title="商户所在楼层, 普调商户需要传")
    owner_name: str = Field(..., title="户主名称", max_length=32)
    phone: str = Field(..., title="联系人手机号", max_length=11)
    password: str = Field(..., title="登录密码", min_length=8, max_length=16)


@router.post("/register")
@log_filter
def register(request: RegisterModel, session: Session = Depends(create_session)):
    """
    注册商户 \n
    :param request: 商户注册请求体\n
    :return: 提交成功返回0
    """
    ret_code = 0
    ret_data = None

    # 检查手机号合法性
    if not validation_utils.is_valid_phone_number(request.phone):
        return make_response(-1, "请输入合法手机号!")

    # 检查商户类型是否合法, 只允许注册为普通商户和快递商户
    if request.merchant_type not in [1, 2]:
        return make_response(-1, "请选择合法商户类型!")

    # 对于普通商户, 检查楼栋（只有A、B、C）
    if request.merchant_type == 1 and request.building not in ["A", "B", "C"]:
        return make_response(-1, "请选择正确的楼栋!")

    hashed_password = security_util.get_password_hash(request.password)
    try:
        now = datetime.datetime.now()
        merchant = Merchant(request.merchant_name, request.merchant_type, request.logo, request.description,
                            request.building, request.floor, request.owner_name, request.phone, hashed_password,
                            now, now)
        session.add(merchant)
        session.commit()
        ret_msg = "申请已提交，请耐心等待审核结果!"
    except sqlalchemy.exc.IntegrityError as e:
        logger.error(f"重复注册: {str(e)}")
        ret_code = -1
        ret_msg = "请勿重复注册!"
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.post("/login")
@log_filter
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(create_session)):
    """
     用户登录，提交方式采用Form表单提交\n
    :param form_data: 表单数据，包含username和password(本系统中username为手机号）\n
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
        if merchant.status == 0:
            session.commit()
            return make_response(-1, f"您的账号({phone})正在审批中, 请耐心等待审核或联系商城管理员审核!")
        elif merchant.status == 2:
            session.commit()
            return make_response(-1, "sorry, 您的商户接入申请已被驳回, 具体原因请联系商城管理员!")
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
        redis_client.hset("merchants", merchant.id, json.dumps(merchant.to_dict(), cls=JsonEncoder))

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.post("/logout")
@log_filter
def logout(response: Response):
    """
    退出登录\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    try:
        response.delete_cookie("x_token")
        response.delete_cookie("merchant_type")
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.get("/me")
@log_filter
def show_me(merchant_id: int = Depends(get_login_merchant)):
    """
    获取我的账号信息\n
    :return: 商户基本信息
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {}
    try:
        merchant = json.loads(redis_client.hget("merchants", merchant_id))
        merchant.pop("password")
        merchant.pop("status")
        merchant["merchant_type"] = MerchantTypeDesc.get(merchant["merchant_type"])

        # todo 从redis获取商户评分星级
        evaluation_star = redis_client.hget("evaluation_stars", merchant["id"])
        if evaluation_star is None:
            merchant["stars"] = 4   # 初始星级默认为4
        else:
            stars, num_of_evaluations = evaluation_star.split("*")
            merchant["stars"] = float(stars) / int(num_of_evaluations)
        ret_data["merchant_info"] = merchant
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)
