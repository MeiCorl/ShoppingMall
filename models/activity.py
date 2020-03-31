# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, BigInteger, Integer, TIMESTAMP, Float

from utils.db_util import Base

"""
营销活动信息表
"""


class Activity(Base):
    __tablename__ = "t_activity_info"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="活动id")
    act_name = Column(String(128), nullable=False, comment="活动名称")
    act_cover = Column(String(256), nullable=False, comment="活动封面")
    begin_time = Column(TIMESTAMP, comment="活动开始时间")
    end_time = Column(TIMESTAMP, comment="活动结束时间")
    create_time = Column(TIMESTAMP, comment="活动创建时间")
    update_time = Column(TIMESTAMP, comment="上次修改时间")

    def __init__(self, act_name, act_cover, begin_time, end_time, create_time, update_time):
        self.act_name = act_name
        self.act_cover = act_cover
        self.begin_time = begin_time
        self.end_time = end_time
        self.create_time = create_time
        self.update_time = update_time


