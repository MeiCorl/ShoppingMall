# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, BigInteger, TIMESTAMP

from utils.db_util import Base

"""
商户评价信息表
"""


class Evaluation(Base):
    __tablename__ = "t_evaluation_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(Integer, index=True, comment="评价商户id")
    comment = Column(String(2048), server_default="", comment="评价内容")
    creator_name = Column(String(64), comment="评价者名称")
    creator_openid = Column(String(32), comment="订单创建者openid")
    create_time = Column(TIMESTAMP, comment="评价时间")
