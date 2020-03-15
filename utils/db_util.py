# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from config import db_config


def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


db_url = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(db_config["user"], db_config["passwd"],
                                                              db_config["host"],
                                                              db_config["port"], db_config["dbname"])
# 创建实例
engine = create_engine(db_url, convert_unicode=True, poolclass=QueuePool, pool_size=100, echo=False, pool_recycle=3600)

Base = declarative_base()  # 生成orm基类
Base.to_dict = to_dict

# 创建与数据库的会话session class, 注意,这里返回给session的是个class,不是实例
session_class = scoped_session(sessionmaker(bind=engine))  # 实例和engine绑定


def create_session():
    session = session_class()
    yield session
    session.close()


# 创建库表
# from models.merchant import Merchant
# from models.deal import Deal
# from models.evaluatation import Evaluation
# from models.product import Product
Base.metadata.create_all(bind=engine)  # 创建表结构
