# -*- coding: utf-8 -*-
from utils.db_util import Base
from sqlalchemy import Column, String, BigInteger, Integer, Float, SmallInteger, TIMESTAMP
"""
用户信息表
"""


class User(Base):
    __tablename__ = "t_user_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户id")
    openid = Column(String(32), unique=True, comment="用户openid")
    phone = Column(String(16), default="", comment="用户手机号")
    name = Column(String(64), default="", comment="用户名称")
    nick_name = Column(String(64), default="", comment="用户昵称")
    address_list = Column(String(1024), default="[]", comment="收货地址列表")
    vip_level = Column(SmallInteger, default=0, comment="会员等级, 0表示不是会员")
    vip_score = Column(Integer, default=0, comment="会员积分")
    account_balance = Column(Float, default=0.00, comment="账户余额")
    create_time = Column(TIMESTAMP, comment="创建时间")

