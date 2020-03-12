# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from config import log_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Log等级总开关

# 创建file_handler
pwd = os.getcwd()
fh = TimedRotatingFileHandler(filename=log_path, when='midnight', backupCount=30)
fh.setLevel(logging.DEBUG)

# 定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)

logger.addHandler(fh)
