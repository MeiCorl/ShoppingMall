# -*- coding: utf-8 -*-
"""
数据校验工具类
"""
import re


def is_valid_phone_number(phone_number):
    reg = "1[3|4|5|7|8][0-9]{9}"
    if re.search(reg, phone_number):
        return True
    else:
        return False


if __name__ == "__main__":
    print(is_valid_phone_number("13349873655"))
