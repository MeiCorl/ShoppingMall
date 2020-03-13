# -*- coding: utf-8 -*-
"""
管理员模块
"""
import json
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from decorators import log_filter
from utils.redis_util import redis_client
from utils.security_util import get_login_merchant
from utils import logger
from consts import MerchantTypeDesc
from handlers import make_response
from utils.db_util import create_session
from models.merchant import Merchant

router = APIRouter()


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
        ret_data["merchant_info"] = merchant
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.get("/merchant_list")
@log_filter
def get_merchant_list(page_no: int, page_size: int, merchant_id: int = Depends(get_login_merchant),
                      session: Session = Depends(create_session)):
    """
    拉取已接入商户列表(仅管理员有权限) \n
    :param page_no: 当前页码\n
    :param page_size: 页面大小\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_count": 0,
        "merchant_list": []
    }
    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")

        merchants = session.query(Merchant).filter(Merchant.id != merchant_id, Merchant.status == 1)
        ret_data["total_count"] = merchants.count()
        merchants = merchants.order_by(-Merchant.create_time).offset((page_no - 1) * page_size).limit(page_size)
        merchant_list = []
        for merchant in merchants:
            tmp = merchant.to_dict()
            tmp.pop("password")
            tmp.pop("status")
            tmp["merchant_type"] = MerchantTypeDesc.get(tmp["merchant_type"])
            merchant_list.append(tmp)
        ret_data["merchant_list"] = merchant_list
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.delete("/delete_merchant")
@log_filter
def delete_merchant(target_merchant_id: int, merchant_id: int = Depends(get_login_merchant),
                    session: Session = Depends(create_session)):
    """
    删除商户(仅管理员有权限)\n
    :param target_merchant_id: 待删除商户id\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"

    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")
        session.query(Merchant).filter(Merchant.id == target_merchant_id).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.get("/apply_list")
@log_filter
def get_apply_list(page_no: int, page_size: int, apply_status: int = Query(..., gt = -1, lt = 3),
                   merchant_id: int = Depends(get_login_merchant),
                   session: Session = Depends(create_session)):
    """
    拉取接申请列表\n
    :param apply_status: 申请状态 0: 待审批  1: 已审批  2: 已拒绝\n
    :param page_no: 当前页码 \n
    :param page_size: 页面大小\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_count": 0,
        "apply_list": []
    }
    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")

        applies = session.query(Merchant).filter(Merchant.id != merchant_id, Merchant.status == apply_status)
        ret_data["total_count"] = applies.count()
        applies = applies.order_by(-Merchant.create_time).offset((page_no - 1) * page_size).limit(page_size)
        apply_list = []
        for apply in applies:
            tmp = apply.to_dict()
            tmp.pop("password")
            tmp.pop("status")
            tmp["merchant_type"] = MerchantTypeDesc.get(tmp["merchant_type"])
            apply_list.append(tmp)
        ret_data["merchant_list"] = apply_list
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.put("/handle_apply")
@log_filter
def handle_apply(target_merchant_id: int, handle_status: int = Query(..., gt = 0, lt = 3),
                 merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    处理商户接入申请
    :param target_merchant_id: 待接入
    :param handle_status: 通过: 0   拒绝: 1
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")
        session.query(Merchant).filter(Merchant.id == target_merchant_id).update({
            Merchant.status: handle_status
        })
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)
