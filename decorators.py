# -*- coding: utf-8 -*-
import time
from functools import wraps

from utils import logger


def log_filter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = 1000 * time.time()
        logger.info(f"===========  Begin: {func.__name__}  ===========")
        logger.info(f"Args: {kwargs}")
        rsp = func(*args, **kwargs)
        logger.info(f"Response: {rsp}")
        end = 1000 * time.time()
        logger.info(f"Time consuming: {end - start}ms")
        logger.info(f"===========   End: {func.__name__}   ===========\n")
        return rsp
    return wrapper

