# -*- coding: utf-8 -*-
"""
商户注册模块
"""
import datetime

import sqlalchemy.exc
from fastapi import APIRouter
from pydantic import BaseModel, Field

from handlers import make_response
from decorators import log_filter
from utils import validation_utils, security_util, db_util, logger
from models.merchant import Merchant

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
def register(request: RegisterModel):
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
    session = db_util.create_session()
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
    finally:
        session.close()
    return make_response(ret_code, ret_msg, ret_data)
