# -*- coding: utf-8 -*-
import logging
from functools import wraps
from logging.handlers import TimedRotatingFileHandler
from config import app_log_path, msg_log_path
from asgi_request_id import get_request_id


def process(func):
    """
    自定义日志处理, 往日志中输出额外参数字段(这里为request id)
    """
    @wraps(func)
    def wrapper(msg, *args, **kwargs):
        kwargs["extra"] = {"request_id": get_request_id()}
        func(msg, *args, **kwargs)
    return wrapper


class MyLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def setLevel(self, log_level):
        self.logger.setLevel(log_level)

    def addHandler(self, handler):
        self.logger.addHandler(handler)

    @process
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    @process
    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    @process
    def warn(self, msg, *args, **kwargs):
        self.logger.warn(msg, *args, **kwargs)

    @process
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)


# 定义handler的输出格式(新增自定义的request id)
formatter = logging.Formatter("%(asctime)s %(request_id)s %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

# Web应用日志
app_logger = MyLogger("App Logger")
app_logger.setLevel(logging.DEBUG)
app_fh = TimedRotatingFileHandler(filename=app_log_path, when='midnight', backupCount=30)
app_fh.setLevel(logging.DEBUG)
app_fh.setFormatter(formatter)
app_logger.addHandler(app_fh)


# WebSocket Server日志
msg_logger = MyLogger("Message Logger")
msg_logger.setLevel(logging.DEBUG)
msg_fh = TimedRotatingFileHandler(filename=msg_log_path, when='midnight', backupCount=30)
msg_fh.setLevel(logging.DEBUG)
msg_fh.setFormatter(formatter)
msg_logger.addHandler(msg_fh)
