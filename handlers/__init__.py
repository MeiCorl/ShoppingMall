# -*- coding: utf-8 -*-


def make_response(ret_code: int, ret_msg: str, data=None):
    rsp = {
        "ret_code": ret_code,
        "ret_msg": ret_msg,
        "ret_data": data
    }
    return rsp
