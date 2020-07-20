import xadmin

from order.models import Order, OrderDetail


class OrderModelAdmin(object):
    """订单模型"""
    pass


xadmin.site.register(Order, OrderModelAdmin)


class OrderDetailModelAdmin(object):
    """
    订单详情
    """
    pass


xadmin.site.register(OrderDetail, OrderDetailModelAdmin)
