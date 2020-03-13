# -*- coding: utf-8 -*-
import datetime
import decimal
import json

"""
    自定义JSON序列化器，解决Decimal、datetime类型无法序列化问题
"""


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        super(JsonEncoder, self).default(o)
