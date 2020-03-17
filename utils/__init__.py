# -*- coding: utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler
from config import app_log_path, msg_log_path

# 定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

# Web应用日志
app_logger = logging.getLogger("App Logger")
app_logger.setLevel(logging.DEBUG)
app_fh = TimedRotatingFileHandler(filename=app_log_path, when='midnight', backupCount=30)
app_fh.setLevel(logging.DEBUG)
app_fh.setFormatter(formatter)
app_logger.addHandler(app_fh)


# WebSocket Server日志
msg_logger = logging.getLogger("Message Logger")
msg_logger.setLevel(logging.DEBUG)
msg_fh = TimedRotatingFileHandler(filename=msg_log_path, when='midnight', backupCount=30)
msg_fh.setLevel(logging.DEBUG)
msg_fh.setFormatter(formatter)
msg_logger.addHandler(msg_fh)
