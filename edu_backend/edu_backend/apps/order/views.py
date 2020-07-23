from datetime import datetime

from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from course.models import CourseExpire
from edu_backend.settings import constants
from order.models import Order, OrderDetail
from order.serializers import OrderModelSerializer


class OrderApiView(CreateAPIView):
    pagination_class = [IsAuthenticated]
    queryset = Order.objects.filter(is_delete=False, is_show=True)
    serializer_class = OrderModelSerializer

    # @transaction.atomic()  #开启事务 当方法完成后，自动提交事务
    # def post(self, request, *args, **kwargs):


class OrderListViewSet(ViewSet):
    """获取订单列表"""

    pagination_class = [IsAuthenticated]

    def get_order_list(self, request):
        user_id = request.user.id
        # user_id = 1
        order_list = Order.objects.filter(user=user_id, is_delete=False)
        data = []
        for order in order_list:
            course_list = []
            order_detail_list = OrderDetail.objects.filter(order=order.id)
            for order_detail in order_detail_list:
                expire_text = "永久有效"
                if order_detail.expire > 0:
                    try:
                        course_expire = CourseExpire.objects.get(pk=order_detail.expire)
                        expire_text = course_expire.expire_text
                    except:
                        expire_text = "出现异常，请联系管理员"
                remaining_time = None
                if order.order_status == 0:
                    remaining_time = int(30 * 60 - (datetime.now().timestamp() - order.create_time.timestamp()))
                course_list.append({
                    'course_id': order_detail.course.id,
                    'course_name': order_detail.course.name,
                    'course_img': constants.IMAGE_SRC + order_detail.course.course_img.url,
                    'discount_name': order_detail.discount_name,
                    'expire_text': expire_text,
                    'price': order_detail.price,
                    'real_price': order_detail.real_price,
                    'order_status': order.order_status,
                    'remaining_time': remaining_time
                })
            order_create_time = datetime.fromtimestamp(order.create_time.timestamp()).strftime("%Y-%m-%d %H:%M:%S")
            data.append({
                "order_create_time": order_create_time,
                "order_number": order.order_number,
                "course_list": course_list
            })
        if data:
            return Response(data=data)
        return Response({"message": "空空如也"})
