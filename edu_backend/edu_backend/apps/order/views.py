from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView

from order.models import Order
from order.serializers import OrderModelSerializer


class OrderApiView(CreateAPIView):
    queryset = Order.objects.filter(is_delete=False, is_show=True)
    serializer_class = OrderModelSerializer

    # @transaction.atomic()  #开启事务 当方法完成后，自动提交事务
    # def post(self, request, *args, **kwargs):
