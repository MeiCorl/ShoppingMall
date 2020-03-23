# -*- coding: utf-8 -*-
from utils.db_util import Base
from sqlalchemy import Column, String, Integer, SmallInteger, BigInteger, TIMESTAMP, Float
"""
商品信息表
"""


class Product(Base):
    __tablename__ = "t_product_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="商品id")
    merchant_id = Column(Integer, index=True, nullable=False, comment="商品所属商户id")
    product_name = Column(String(128), nullable=False, comment="商品名称")
    product_cover = Column(String(512), nullable=False, comment="商品封面图片地址")
    product_desc = Column(String(512), default="", comment="商品简介")
    detail_pictures = Column(String(2048), default="[]", comment="商品详情图片列表")
    has_stock_limit = Column(SmallInteger, default=1, comment="商品是否有库存数量限制, 0: 没有, 1: 有， 默认有限制")
    init_stock = Column(Integer, default=0, comment="商品初始库存数量")
    remain_stock = Column(Integer, default=0, comment="商品剩余库存数量")
    price = Column(Float, nullable=False, comment="商品单价: 元")
    status = Column(SmallInteger, default=0, comment="商品状态, 0: 售卖中, 1: 已下架")
    create_time = Column(TIMESTAMP, comment="商品上架时间")
    update_time = Column(TIMESTAMP, comment="更新时间")

    def __init__(self, merchant_id, product_name, product_cover, product_desc, detail_pictures, has_stock_limit,
                 init_stock, price, create_time, update_time):
        self.merchant_id = merchant_id
        self.product_name = product_name
        self.product_cover = product_cover
        self.product_desc = product_desc
        self.detail_pictures = detail_pictures
        self.has_stock_limit = has_stock_limit
        self.init_stock = init_stock
        self.remain_stock = init_stock
        self.price = price
        self.create_time = create_time
        self.update_time = update_time

