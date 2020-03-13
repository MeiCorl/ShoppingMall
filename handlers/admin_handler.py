# -*- coding: utf-8 -*-
"""
管理员模块
"""
import json
from fastapi import APIRouter, Depends
from decorators import log_filter
from utils.redis_util import redis_client
from utils.security_util import get_login_merchant

router = APIRouter()


@router.get("/me")
@log_filter
def show_me(merchant_id: int = Depends(get_login_merchant)):
    merchant = json.loads(redis_client.hget("merchants", merchant_id))
    return merchant
