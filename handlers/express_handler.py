# -*- coding: utf-8 -*-
"""
快递员模块
"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from consts import DealStatusDesc
from handlers import make_response
from utils import logger
from utils.security_util import get_login_merchant
from utils.db_util import create_session
from utils.redis_util import redis_client
from decorators import log_filter
from models.deal import Deal

router = APIRouter()


@router.put("/accept_deal")
@log_filter
def accept_deal(deal_no: int, merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    接收订单
    :param deal_no:
    :return:
    """
    merchant = json.loads(redis_client.hget("merchants", merchant_id))
    if merchant["merchant_type"] != 2:
        return make_response(-1, "sorry, 您没有此操作权限!")
    ret_code = 0
    ret_msg = "success"
    try:
        merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if merchant["merchant_type"] != 2:
            return make_response(-1, "sorry, 您没有此操作权限!")
        session.query(Deal).filter(Deal.deal_no == deal_no).update({
            Deal.deal_status: 3
        })
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.put("/refuse_deal")
@log_filter
def refuse_deal(deal_no: int, merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    拒收订单
    :param deal_no:
    :return:
    """
    merchant = json.loads(redis_client.hget("merchants", merchant_id))
    if merchant["merchant_type"] != 2:
        return make_response(-1, "sorry, 您没有此操作权限!")
    ret_code = 0
    ret_msg = "success"
    try:
        merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if merchant["merchant_type"] != 2:
            return make_response(-1, "sorry, 您没有此操作权限!")
        session.query(Deal).filter(Deal.deal_no == deal_no).update({
            Deal.deal_status: 4
        })
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.put("/complete_deal")
@log_filter
def complete_deal(deal_no: int, merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    完成订单
    :param deal_no: 订单号
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    try:
        merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if merchant["merchant_type"] != 2:
            return make_response(-1, "sorry, 您没有此操作权限!")
        session.query(Deal).filter(Deal.deal_no == deal_no).update({
            Deal.deal_status: 5
        })
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.get("/deal_list")
@log_filter
def get_deals_to_delivery(begin_time: datetime, end_time: datetime, deal_status: int = Query(None, gt=2, lt=6),
                          page_no: int = Query(1, gt=-1), page_size: int = Query(20, gt=-1),
                          merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    拉取需要派送的订单
    :param begin_time: 开始时间
    :param end_time: 结束时间
    :param deal_status: 订单状态 3:派送中 4:已拒收 5:已完成(快递公司只能看到需要派送的订单信息), 不传则拉取全部
    :param page_no: 当前页码
    :param page_size: 页面大小
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_count": 0,
        "deal_list": []
    }
    try:
        merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if merchant["merchant_type"] != 2:
            return make_response(-1, "sorry, 您没有此操作权限!")

        if deal_status is None:
            deals = session.query(Deal).filter(Deal.create_time.between(begin_time, end_time), Deal.deal_status.in_([3, 4, 5]))
        else:
            deals = session.query(Deal).filter(Deal.create_time.between(begin_time, end_time), Deal.deal_status == deal_status)
        ret_data["total_count"] = deals.count()
        deals = deals.order_by(-Deal.create_time).offset((page_no - 1) * page_size).limit(page_size)
        deal_list = []
        for deal in deals:
            deal_info = deal.to_dict()
            deal_info["need_delivery"] = "是" if deal_info["need_delivery"] == 1 else "否"
            deal_info["deal_status"] = DealStatusDesc.get(deal_info["deal_status"])
            deal_list.append(deal_info)
        ret_data["deal_list"] = deal_list
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)
