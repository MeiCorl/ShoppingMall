# -*- coding: utf-8 -*-
"""
管理员模块
"""
import json
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

from decorators import log_filter
from utils.redis_util import redis_client
from utils.security_util import get_login_merchant
from utils.json_encoder import JsonEncoder
from utils import app_logger as logger
from consts import MerchantTypeDesc, DealStatusDesc
from handlers import make_response
from utils.db_util import create_session
from models.merchant import Merchant
from models.deal import Deal
from models.evaluation import Evaluation

router = APIRouter()


@router.get("/merchant_list")
@log_filter
def get_merchant_list(page_no: int = Query(1, gt=-1), page_size: int = Query(20, gt=-1),
                      merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
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

        # 查评价星级 evaluation_stars存储商户得星总数  evaluation_times被评星次数
        evaluation_stars = redis_client.hmget("evaluation_stars", [merchant.id for merchant in merchants])
        evaluation_times = redis_client.hmget("evaluation_times", [merchant.id for merchant in merchants])
        merchant_list = []
        for i in range(merchants.count()):
            merchant = merchants[i]
            merchant_detail = merchant.to_dict()
            merchant_detail.pop("password")
            merchant_detail.pop("status")
            merchant_detail["merchant_type"] = MerchantTypeDesc.get(merchant_detail["merchant_type"])

            stars = evaluation_stars[i]
            times = evaluation_times[i]
            if stars is None:
                merchant_detail["stars"] = 4   # 初始星级默认为4
            else:
                merchant_detail["stars"] = float(stars) / int(times)
            merchant_list.append(merchant_detail)
        ret_data["merchant_list"] = merchant_list
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.get("/merchant_detail")
@log_filter
def get_merchant_detail(target_merchant_id: int, merchant_id: int = Depends(get_login_merchant),
                        session: Session = Depends(create_session)):
    """
    查看商户详情\n
    :param target_merchant_id: 商户id\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {}
    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")
        merchant = session.query(Merchant).filter(Merchant.id == target_merchant_id).one_or_none()
        if merchant is None:
            session.commit()
            return make_response(-1, "商户存在!")
        merchant_detail = merchant.to_dict()
        merchant_detail.pop("password")
        merchant_detail.pop("status")
        merchant_detail["merchant_type"] = MerchantTypeDesc.get(merchant_detail["merchant_type"])

        # todo 从redis获取商户评分星级
        stars = redis_client.hget("evaluation_stars", merchant.id)
        times = redis_client.hmget("evaluation_times", merchant.id)
        if stars is None:
            merchant_detail["stars"] = 4   # 初始星级默认为4
        else:
            merchant_detail["stars"] = float(stars) / int(times)
        ret_data["merchant_detail"] = merchant_detail
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
        merchant = session.query(Merchant).filter(Merchant.id == target_merchant_id)
        session.delete(merchant)
        redis_client.hdel("merchants", merchant.id)
        # todo 删除商户下商品、商户对应评价信息
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.get("/apply_list")
@log_filter
def get_apply_list(page_no: int = Query(1, gt=-1), page_size: int = Query(20, gt=-1),
                   apply_status: int = Query(..., gt=-1, lt=3), merchant_id: int = Depends(get_login_merchant),
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
def handle_apply(target_merchant_id: int, handle_status: int = Query(..., gt=0, lt=3),
                 merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    处理商户接入申请
    :param target_merchant_id: 待接入
    :param handle_status: 通过: 1  拒绝: 2
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")
        merchant = session.query(Merchant).filter(Merchant.id == target_merchant_id).one_or_none()
        if merchant is None:
            session.commit()
            return make_response(-1, "申请不存在!")
        merchant.status = handle_status
        if handle_status == 1:
            redis_client.hset("merchants", merchant.id, json.dumps(merchant.to_dict(), cls=JsonEncoder))
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.get("/deal_list")
@log_filter
def get_total_deal_list(begin_time: datetime, end_time: datetime, deal_status: int = Query(None, gt=-1, lt=5),
                        page_no: int = Query(1, gt=-1), page_size: int = Query(20, gt=-1),
                        merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    查询商城begin_time到end_time时间段内全部订单列表(仅管理员可见)\n
    :param page_no: 当前页码 （不传默认为1）\n
    :param page_size: 页面大小 （不传默认为20）\n
    :param begin_time: 起始时间\n
    :param end_time: 结束时间\n
    :param deal_status: 订单状态 0: 待支付  1: 待派送 2: 待上门领取 3: 派送中 4: 已完成， 不传则拉取全部\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_count": 0,
        "deal_list": []
    }
    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")
        if deal_status is None:
            deals = session.query(Deal).filter(Deal.create_time.between(begin_time, end_time))
        else:
            deals = session.query(Deal).filter(Deal.create_time.between(begin_time, end_time),
                                               Deal.deal_status == deal_status)

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


@router.get("/sale_statistics")
@log_filter
def get_sale_statistics(begin_time: datetime, end_time: datetime, merchant_id: int = Depends(get_login_merchant),
                        session: Session = Depends(create_session)):
    """
    获取商城begin_time到end_time时间段内销量统计，含商城订单总数量、总金额，及各商户订单数量、金额分布(仅管理员有权限)\n
    :param begin_time: 开始时间\n
    :param end_time: 结束时间\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_deal_amount": 0,
        "total_deal_money": 0,
        "distributions": []
    }

    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")
        statistics = session.query(
            Deal.merchant_id.label("merchant_id"),
            func.count(Deal.deal_no).label("deal_amount"),
            func.sum(Deal.money).label("total_money"),
        ).filter(
            Deal.create_time.between(begin_time, end_time)
        ).group_by(Deal.merchant_id)

        merchant_infos = redis_client.hgetall("merchants")
        logger.info(f"商户列表: {merchant_infos}")

        distributions = []
        total_deal_amount = 0
        total_deal_money = 0
        for statistic in statistics:
            total_deal_amount += statistic.deal_amount
            total_deal_money += statistic.total_money
            merchant_info = json.loads(merchant_infos[str(statistic.merchant_id)])
            distributions.append({
                "merchant_id": statistic.merchant_id,
                "merchant_name": merchant_info["merchant_name"],
                "deal_amount": statistic.deal_amount,
                "total_money": statistic.total_money
            })
        ret_data["total_deal_amount"] = total_deal_amount
        ret_data["total_deal_money"] = total_deal_money
        ret_data["distributions"] = distributions
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.get("/merchnant_evaluations")
@log_filter
def get_merchant_evaluations(target_merchant_id: int, page_no: int = Query(1, gt=-1), page_size: int = Query(20, gt=-1),
                             merchant_id: int = Depends(get_login_merchant),
                             session: Session = Depends(create_session)):
    """
    拉取目标商户的评价列表(仅管理员有权限) \n
    :param target_merchant_id:\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_amount": 0,
        "evaluation_list": []
    }
    try:
        cur_merchant = json.loads(redis_client.hget("merchants", merchant_id))
        if cur_merchant["merchant_type"] != 0:
            session.commit()
            return make_response(-1, "权限不足!")
        evaluations = session.query(Evaluation).filter(Evaluation.merchant_id == target_merchant_id)
        ret_data["total_amount"] = evaluations.count()
        evaluations = evaluations.order_by(-Evaluation.create_time).offset((page_no - 1) * page_size).limit(page_size)
        ret_data["evaluation_list"] = [evaluation.to_dict() for evaluation in evaluations]
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


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
        session.query(Deal).filter(Deal.deal_no == deal_no, Deal.merchant_id == merchant_id).update({
            Deal.deal_status: 5
        })
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)
