# -*- coding: utf-8 -*-
from utils.db_util import Base
from sqlalchemy import Column, String, Integer, SmallInteger, TIMESTAMP, Index, text
"""
商户信息表
"""


class Merchant(Base):
    __tablename__ = "t_merchant_info"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="商户id")
    merchant_name = Column(String(128), nullable=False, comment="商户名称")
    merchant_type = Column(SmallInteger, server_default=text('1'), comment="商户类型, 0: 管理商户  1: 普通商户 2: 快递商户")
    logo = Column(String(256), server_default="", comment="商户logo图标")
    description = Column(String(1024), server_default="", comment="商户简介")
    building = Column(String(2), server_default="", comment="商户所在楼栋, A、B、C")
    floor = Column(SmallInteger, server_default=text('0'), comment="商户所在楼层, 1、2、3、4")
    owner_name = Column(String(32), nullable=False, comment="户主名称")
    phone = Column(String(16), nullable=False, unique=True, comment="联系人手机号")
    password = Column(String(128), nullable=False, comment="登录密码")
    status = Column(SmallInteger, server_default=text('0'), comment="商户状态， 0: 待审核的商户  1: 已审核通过的商户 2: 已拒绝的商户")
    create_time = Column(TIMESTAMP, comment="注册时间")
    update_time = Column(TIMESTAMP, comment="更新时间")

    __table_args__ = (
        Index("building_floor_index", "building", "floor"),
    )

    def __init__(self, merchant_name, merchant_type, logo, description, building, floor, owner_name, phone, password,
                 create_time, update_time):
        self.merchant_name = merchant_name
        self.merchant_type = merchant_type
        self.logo = logo
        self.description = description
        self.building = building
        self.floor = floor
        self.owner_name = owner_name
        self.phone = phone
        self.password = password
        self.create_time = create_time
        self.update_time = update_time



