# -*- coding: utf-8 -*-
from functools import wraps

from utils import logger


def log_filter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"===========  Begin: {func.__name__}  ===========")
        logger.info(f"Args: {kwargs}")
        rsp = func(*args, **kwargs)
        logger.info(f"Response: {rsp}")
        logger.info(f"===========   End: {func.__name__}   ===========\n")
        return rsp
    return wrapper

