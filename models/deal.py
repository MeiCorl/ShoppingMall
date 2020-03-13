# -*- coding: utf-8 -*-
from utils.db_util import Base
from sqlalchemy import Column, String, Integer, Float, SmallInteger, TIMESTAMP, Index, Text


class Deal(Base):
    __tablename__ = "t_deal_info"

    deal_no = Column(String(16), primary_key=True, comment="订单号")
    merchant_id = Column(Integer, nullable=False, index=True, comment="订单所属商户id")
    money = Column(Float, default=0, comment="订单总金额")
    need_delivery = Column(SmallInteger, default=0, comment="订单是否需要配送")
    deal_status = Column(SmallInteger, default=0, comment="订单状态, 0: 待支付  1: 已支付未完成 2: 已完成")
    creator_name = Column(String(64), default="", comment="订单创建者名称")
    creator_openid = Column(String(32), nullable=False, comment="订单创建者openid")
    content = Column(Text, default="{}", comment="订单内容")
    create_time = Column(TIMESTAMP, comment="订单创建时间")
    pay_time = Column(TIMESTAMP, comment="订单支付时间")

