# -*- coding: utf-8 -*-
"""
商户登出模块
"""
from fastapi import APIRouter,Depends
from starlette.responses import Response

from handlers import make_response
from utils.redis_util import redis_client
from utils.security_util import get_login_merchant
from utils import logger
from decorators import log_filter

router = APIRouter()


@router.post("/logout")
@log_filter
def logout(response: Response, merchant_id: int = Depends(get_login_merchant)):
    """
    退出登录\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    try:
        response.delete_cookie("x_token")
        response.delete_cookie("merchant_type")
        redis_client.hdel("merchants", merchant_id)
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)
