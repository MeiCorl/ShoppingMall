# -*- coding: utf-8 -*-
from utils.db_util import Base
from sqlalchemy import Column, String, BigInteger, Integer, Float, SmallInteger, TIMESTAMP, text
"""
用户信息表
"""


class User(Base):
    __tablename__ = "t_user_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户id")
    openid = Column(String(32), unique=True, comment="用户openid")
    phone = Column(String(16), server_default="", comment="用户手机号")
    nick_name = Column(String(64), server_default="", comment="用户昵称")
    sex = Column(String(2), server_default="", comment="性别")
    head_img = Column(String(256), server_default="", comment="用户头像")
    address_list = Column(String(1024), server_default="", comment="收货地址列表")
    vip_level = Column(SmallInteger, server_default=text('0'), comment="会员等级, 0表示不是会员")
    vip_score = Column(Integer, server_default=text('0'), comment="会员积分")
    account_balance = Column(Float, server_default=text('0.00'), comment="账户余额")
    create_time = Column(TIMESTAMP, comment="创建时间")

