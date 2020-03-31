# -*- coding: utf-8 -*-
"""
商户模块
"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict

from consts import ProductStatusDesc, DealStatusDesc, get_activity_status_desc
from utils import app_logger as logger
from decorators import log_filter
from handlers import make_response
from utils.json_encoder import JsonEncoder
from utils.db_util import create_session
from utils.security_util import get_login_merchant
from utils.redis_util import redis_client
from models.deal import Deal
from models.evaluation import Evaluation
from models.product import Product
from models.activity import Activity

router = APIRouter()


class ProductModel(BaseModel):
    id: int = Field(None, title="商品id, 新增商品时不传")
    product_name: str = Field(..., title="商品名称", max_length=128)
    product_tag: str = Field(..., title="商品分裂标签")
    product_cover: str = Field(..., title="商品封面图片地址", max_length=512)
    product_desc: str = Field("", title="商品简介", max_length=512)
    detail_pictures: List[str] = Field([], title="商品详情图片列表")
    has_stock_limit: int = Field(1, title="商品是否有库存数量限制, 0: 没有, 1: 有， 默认有限制")
    remain_stock: int = Field(0, title="商品剩余库存数量")
    price: float = Field(..., title="商品单价")


class ActivityProductModel(BaseModel):
    activity_id: int = Field(..., title="活动id")
    product_discount_map: Dict[int, float] = Field(..., title="商品及其折扣对应关系")


@router.get("/evaluation_list")
@log_filter
def get_evaluation_list(page_no: int = Query(1, gt=-1), page_size: int = Query(20, gt=-1),
                        merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    获取我的评价列表 \n
    :param page_no:  当前页码\n
    :param page_size:  页面代销\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_amount": 0,
        "evaluation_list": []
    }
    try:
        evaluations = session.query(Evaluation).filter(Evaluation.merchant_id == merchant_id)
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


@router.get("/product_tags")
@log_filter
def get_product_tags():
    """
    拉取商品分类标签
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "product_tags": ["水果", "食品", "生鲜", "数码", "电器", "洗护", "男装", "女装", "鞋靴", "母婴", "保健", "医药", "百货", "其它"]
    }
    return make_response(ret_code, ret_msg, ret_data)


@router.post("/add_product")
@log_filter
def add_product(product_info: ProductModel, merchant_id: int = Depends(get_login_merchant),
                session: Session = Depends(create_session)):
    """
    新增商品\n
    :param product_info: 商品实体，参见ProductModel \n
    :return: 成功返回商品id
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {}
    try:
        now = datetime.now()
        product = Product(merchant_id, product_info.product_name, product_info.product_tag, product_info.product_cover,
                          product_info.product_desc, json.dumps(product_info.detail_pictures),
                          product_info.has_stock_limit,
                          product_info.remain_stock, product_info.price, now, now)
        session.add(product)
        session.commit()
        logger.info(f"新增商品成功, product_id: {product.id}")

        # 商品信息存入缓存
        redis_client.hset("products", product.id, json.dumps(product.to_dict(), cls=JsonEncoder))

        # 将商品id保存至商户，便于根据商户id查询对应商品
        redis_client.sadd(f"products_of_merchant_{merchant_id}", product.id)

        logger.info("商品存入redis成功!")
        ret_data["product_id"] = product.id
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.post("/modify_product")
@log_filter
def modify_product(product_info: ProductModel, merchant_id: int = Depends(get_login_merchant),
                   session: Session = Depends(create_session)):
    """
    修改商品(只能修改商品名称、商品简介、商品封面图片地址、商品详情图片地址、商品剩余库存、商品价格)\n
    :param product_info: 商品实体，参见ProductModel \n
    :return: 成功返回商品id
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {}
    try:
        if product_info.id is None:
            session.commit()
            return make_response(-1, "商品id不能为空!")
        product = session.query(Product).filter(Product.id == product_info.id).one_or_none()
        if product is None:
            session.commit()
            return make_response(-1, f"商品({product_info.id})不存在!")
        if product.merchant_id != merchant_id:
            session.commit()
            return make_response(-1, f"不允许修改他人账户下的商品!")
        product.product_name = product_info.product_name
        product.product_tag = product_info.product_tag
        product.product_cover = product_info.product_cover
        product.product_desc = product_info.product_desc
        product.detail_pictures = json.dumps(product_info.detail_pictures)
        product.has_stock_limit = product_info.has_stock_limit
        product.remain_stock = product_info.remain_stock
        product.price = product_info.price
        product.update_time = datetime.now()

        session.commit()
        logger.info(f"商品信息修改成功, product_id: {product.id}")

        # 更新缓存
        redis_client.hset("products", product.id, json.dumps(product.to_dict(), cls=JsonEncoder))
        logger.info("更新redis成功!")
        ret_data["product_id"] = product.id
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.put("/offline_product")
@log_filter
def offline_product(product_id: int, merchant_id: int = Depends(get_login_merchant),
                    session: Session = Depends(create_session)):
    """
    下架商品\n
    :param product_id: 商品id\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    try:
        product_info = redis_client.hget("products", product_id)
        if product_info is None:
            session.commit()
            return make_response(-1, "商品不存在!")
        product = json.loads(product_info)
        if product["merchant_id"] != merchant_id:
            session.commit()
            return make_response(-1, "仅能下架自己商户下的商品!")

        # 更新缓存
        product["status"] = 1
        redis_client.hset("products", product_id, json.dumps(product))

        # 更新db
        session.query(Product).filter(Product.id == product_id).update({
            Product.status: 1
        })
        session.commit()
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.get("/product_list")
@log_filter
def get_product_list(merchant_id: int = Depends(get_login_merchant)):
    """
    拉取本商户下全部商品列表\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_amount": 0,
        "product_list": [],
    }
    # 从redis拉取本商户下全部商品信息
    try:
        product_ids = redis_client.smembers(f"products_of_merchant_{merchant_id}")

        products = redis_client.hmget("products", product_ids)

        total_amount = 0
        product_list = []
        for value in products:
            total_amount += 1
            product = json.loads(value)
            product["status"] = ProductStatusDesc[product["status"]]
            product_list.append(product)
        ret_data["total_amount"] = len(products)
        ret_data["product_list"] = product_list
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.delete("/delete_product")
@log_filter
def delete_product(product_id: int, merchant_id: int = Depends(get_login_merchant),
                   session: Session = Depends(create_session)):
    """
    删除商品! \n
    :param product_id: 商品id \n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    try:
        product_info = redis_client.hget("products", product_id)
        if product_info is None:
            session.commit()
            return make_response(-1, "商品不存在!")
        product = json.loads(product_info)
        if product["merchant_id"] != merchant_id:
            session.commit()
            return make_response(-1, "仅能删除自己商户下的商品!")

        # 删除缓存
        redis_client.hdel("products", product_id)
        redis_client.srem(f"products_of_merchant_{merchant_id}", product_id)

        # 删除db
        session.query(Product).filter(Product.id == product_id).delete()
        session.commit()
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


@router.get("/deal_list")
@log_filter
def get_deal_list(begin_time: datetime, end_time: datetime, deal_status: int = Query(None, gt=-1, lt=5),
                  page_no: int = Query(1, gt=-1), page_size: int = Query(20, gt=-1),
                  merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    根据时间段及状态拉取商户下订单列表\n
    :param begin_time: 开始时间\n
    :param end_time: 结束时间\n
    :param deal_status: 订单状态 0: 待支付  1: 待派送 2: 待上门领取 3: 派送中 4: 已完成， 不传则拉取全部\n
    :param page_no: 当前页码（不传默认为1）\n
    :param page_size: 页面大小（不传默认为20）\n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_count": 0,
        "deal_list": []
    }
    try:
        if deal_status is None:
            deals = session.query(Deal).filter(Deal.create_time.between(begin_time, end_time),
                                               Deal.merchant_id == merchant_id)
        else:
            deals = session.query(Deal).filter(Deal.create_time.between(begin_time, end_time),
                                               Deal.deal_status == deal_status,
                                               Deal.merchant_id == merchant_id)
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


@router.get("/activity_list")
@log_filter
def get_activity_list(page_no: int = 1, page_size: int = 10, merchant_id: int = Depends(get_login_merchant), session: Session = Depends(create_session)):
    """
    查询商城营销活动列表\n
    :param: page_no: 当前页码，默认1
    :param: page_size: 页面大小， 默认10
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "total_count": 0,
        "activity_list": []
    }

    try:
        now = datetime.now()
        activities = session.query(Activity).order_by(-Activity.create_time)
        ret_data["total_count"] = activities.count()

        activities = activities.offset((page_no - 1) * page_size).limit(page_size)
        activity_list = []
        for activity in activities:
            activity_list.append({
                "id": activity.id,
                "act_name": activity.act_name,
                "act_cover": activity.act_cover,
                "status": get_activity_status_desc(now, activity.begin_time, activity.end_time),
                "begin_time": activity.begin_time,
                "end_time": activity.end_time,
            })
        ret_data["activity_list"] = activity_list
    except Exception as e:
        session.rollback()
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.get("/get_activity_products")
@log_filter
def get_activity_products(activity_id: int, merchant_id: int = Depends(get_login_merchant)):
    """
    拉取参与某个营销活动的商品列表 \n
    :param activity_id: 活动id \n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    ret_data = {
        "product_list": []
    }

    try:
        # 获取活动商品折扣表
        discount_table = redis_client.hgetall(f"discount_of_activity_{activity_id}")
        if discount_table is not None:
            discount_table.pop("")
            product_ids = discount_table.keys()

            # 查询活动商品信息
            products = redis_client.hmget("products", product_ids)

            # 查询商户信息
            merchants = redis_client.hgetall("merchants")

            product_list = []
            for value in products:
                if value is not None:
                    product = json.loads(value)
                    product_list.append({
                        "product_id": product["id"],
                        "product_name": product["product_name"],
                        "product_cover": product["product_cover"],
                        "discount": discount_table.get(str(product["id"])),
                        "merchant_name": merchants.get(product["merchant_id"]).get("merchant_name")
                    })
            ret_data["product_list"] = product_list
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg, ret_data)


@router.post("/add_products_to_activity")
@log_filter
def add_products_to_activity(actvity_product: ActivityProductModel, merchant_id: int = Depends(get_login_merchant)):
    """
    添加商品到营销活动(必须在活动结束之前) \n
    :param: actvity_product: 活动商品及折扣信息 \n
    :return:
    """
    ret_code = 0
    ret_msg = "success"
    try:
        # 查询活动信息
        activity_key = f"activity_{actvity_product.activity_id}"
        activity = redis_client.get(activity_key)
        if activity is None:
            return make_response(-1, "活动不存在或已结束!")

        # 将商品id添加至活动折扣表
        discount_key = f"discount_of_activity_{actvity_product.activity_id}"
        pipe = redis_client.pipeline(transaction=False)
        for product_id, discount in actvity_product.product_discount_map.items():
            pipe.hset(discount_key, product_id, discount)
        pipe.execute()
        logger.info("新增活动商品成功!")
    except Exception as e:
        logger.error(str(e))
        ret_code = -1
        ret_msg = str(e)
    return make_response(ret_code, ret_msg)


