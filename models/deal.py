# -*- coding: utf-8 -*-
from utils.db_util import Base
from sqlalchemy import Column, String, BigInteger, Integer, Float, SmallInteger, TIMESTAMP, Index, text
"""
订单信息表
"""


class Deal(Base):
    __tablename__ = "t_deal_info"

    deal_no = Column(BigInteger, primary_key=True, autoincrement=True, comment="订单号")
    merchant_id = Column(Integer, nullable=False, comment="订单所属商户id")
    origin_money = Column(Float, server_default=text('0'), comment="订单折扣前总金额")
    money = Column(Float, server_default=text('0'), comment="订单折后总金额")
    need_delivery = Column(SmallInteger, server_default=text('0'), comment="订单是否需要配送")
    deal_status = Column(SmallInteger, server_default=text('0'), comment="订单状态, 0: 待支付  1:待派送 2:待上门领取 3:派送中 4:已拒收 5:已完成")
    creator_name = Column(String(64), server_default="", comment="订单创建者名称")
    creator_openid = Column(String(32), index=True, nullable=False, comment="订单创建者openid")
    creator_phone = Column(String(16), server_default="", comment="联系人手机号")
    content = Column(String(4096), server_default="[]", comment="订单内容")
    address = Column(String(128), nullable=False, comment="收货地址")
    create_time = Column(TIMESTAMP, comment="订单创建时间")
    pay_time = Column(TIMESTAMP, comment="订单支付时间")

    __table_args__ = (
        Index("time_merchant_index", "create_time", "merchant_id"),  # 根据时间段查询订单列表
        Index("time_status_index", "create_time", "deal_status")     # 根据时间状态查询订单列表
    )
