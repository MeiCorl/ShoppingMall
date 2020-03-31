# -*- coding: utf-8 -*-

"""商户类型描述"""
MerchantTypeDesc = {
    0: "管理员",
    1: "普通商户",
    2: "快递商户"
}

"订单状态描述"
DealStatusDesc = {
    0: "待支付",
    1: "待派送",
    2: "待上门领取",
    3: "派送中",
    4: "快递公司已拒绝派送",
    5: "已完成"
}

"商品状态描述"
ProductStatusDesc = {
    0: "售卖中",
    1: "已下架"
}


def get_activity_status_desc(now, begin_time, end_time):
    """
    营销活动状态描述
    :param now: 当前时间
    :param begin_time: 活动开始时间
    :param end_time: 活动结束时间
    :return: 活动状态描述
    """
    if now < begin_time:
        return "未开始"
    elif now > end_time:
        return "已结束"
    else:
        return "进行中"
