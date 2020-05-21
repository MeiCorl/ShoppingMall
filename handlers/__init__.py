# -*- coding: utf-8 -*-
from asgi_request_id import get_request_id


def make_response(ret_code: int, ret_msg: str, data=None):
    rsp = {
        "req_id": get_request_id(),
        "ret_code": ret_code,
        "ret_msg": ret_msg,
        "ret_data": data
    }
    return rsp
