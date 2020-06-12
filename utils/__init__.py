# -*- coding: utf-8 -*-
import os
import inspect
import logging
from functools import wraps
from logging.handlers import TimedRotatingFileHandler
from config import app_log_path, msg_log_path
from asgi_request_id import get_request_id


class MyLogger:
    def process(func):
        """
        自定义日志处理, 往日志中输出额外参数字段(这里为request id)
        """
        @wraps(func)
        def wrapper(self, msg, *args, **kwargs):
            # 获取调用方所在栈帧(第2帧，数组下标为1)
            frame = inspect.stack()[1]

            # 获取调用方所文件名，这里只取文件名，不带路径
            file_name = os.path.basename(frame[1])

            # 获取代码行数
            file_no = frame[2]

            kwargs["extra"] = {
                # 当前请求id
                "request_id": get_request_id(),
                # 获取调用方模块文件名
                "file_name": file_name,   # sys._getframe(1).f_code.co_filename,
                # 获取被调用方法被调用时所处代码行数
                "file_no": file_no      # sys._getframe(1).f_lineno
            }
            func(self, msg, *args, **kwargs)
        return wrapper

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
# formatter = logging.Formatter("%(asctime)s %(request_id)s %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
formatter = logging.Formatter("%(asctime)s %(request_id)s %(file_name)s[line:%(file_no)d] - %(levelname)s: %(message)s")

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
