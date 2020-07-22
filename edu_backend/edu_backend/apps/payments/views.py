import json
import logging
from datetime import datetime

from alipay import AliPay
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from course.models import CourseExpire
from order.models import Order
from user.models import UserCourse
from rest_framework.permissions import IsAuthenticated

log = logging.getLogger('django')


class AliPayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取支付宝的链接地址"""

        order_number = request.query_params.get('order_number')
        # 查询订单是否存在
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({'message': "对不起，当前订单不存在"}, status=status.HTTP_400_BAD_REQUEST)
        # 初始化支付宝参数
        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG['appid'],
            app_notify_url=settings.ALIAPY_CONFIG['app_notify_url'],  # 默认回调url
            app_private_key_string=settings.ALIAPY_CONFIG['app_private_key_path'],
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIAPY_CONFIG['alipay_public_key_path'],
            sign_type=settings.ALIAPY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug=settings.ALIAPY_CONFIG['debug'],  # 默认False
        )

        # subject = "测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 生成支付的链接地址
        order_string = alipay.api_alipay_trade_page_pay(
            # 支付宝所接收的订单号
            out_trade_no=order_number,
            # 价钱
            total_amount=float(order.real_price),
            # 主题
            subject=order.order_title,
            return_url=settings.ALIAPY_CONFIG['return_url'],
            notify_url=settings.ALIAPY_CONFIG['notify_url']  # 可选, 不填则使用默认notify url
        )
        # 生成支付的链接地址需要和支付宝网关地址拼接才能使用
        url = settings.ALIAPY_CONFIG['gateway_url'] + order_string
        return Response(url)


class AliPayResultAPIView(APIView):
    """
    支付宝支付成功后的业务
    修改订单状态，生成用户购买记录，展示订单结算成功的页面
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):

        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG['appid'],
            app_notify_url=settings.ALIAPY_CONFIG['app_notify_url'],  # 默认回调url
            app_private_key_string=settings.ALIAPY_CONFIG['app_private_key_path'],
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIAPY_CONFIG['alipay_public_key_path'],
            sign_type=settings.ALIAPY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug=settings.ALIAPY_CONFIG['debug'],  # 默认False
        )
        data = request.query_params.dict()
        # sign = request.data.get('sign')
        # print(sign)
        # data = request.data.get('ali_data')
        # print(data)
        # data.pop("sign")
        # signature = sign
        # signature = data.pop("sign")
        # verification
        # success = alipay.verify(data, signature)
        success = True
        # if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        if success:
            # print("trade succeed", '当前订单支付成功')
            return self.order_result_pay(data)
        return Response({'message': '对不起，当前订单支付失败'}, status=status.HTTP_400_BAD_REQUEST)

    def order_result_pay(self, data):
        """处理订单成功后的业务"""
        # 商户的订单号
        order_number = data.get('out_trade_no')

        try:
            order = Order.objects.get(order_number=order_number, order_status=0)
        except Order.DoesNotExist:
            return Response({'message': '对不起，支付结果查询失败，请检查订单是否存在'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            rollback = transaction.savepoint()
            try:
                order.pay_time = datetime.now()
                order.order_status = 1
                order.save()

                # 订单的所属用户
                user = order.user
                # 订单中的所有课程的订单详情
                order_detail_list = order.order_courses.all()
                # 订单结算所展示的信息
                course_list = []

                for order_detail in order_detail_list:
                    """遍历出当前订单中所有的课程的订单详情"""
                    course = order_detail.course
                    course.students += 1
                    course.save()
                    pay_timestamp = order.pay_time.timestamp()
                    if order_detail.expire > 0:
                        expire = CourseExpire.objects.get(pk=order_detail.expire)
                        expire_timestamp = expire.expire_time * 24 * 60 * 60
                        end_time = datetime.fromtimestamp(pay_timestamp + expire_timestamp)
                    else:
                        end_time = None
                    UserCourse.objects.create(
                        user_id=user.id,
                        course_id=course.id,
                        trade_no=data.get("trade_no"),
                        buy_type=1,
                        pay_time=order.pay_time,
                        out_time=end_time,
                    )
                    course_list.append({
                        'id': course.id,
                        'name': course.name,
                    })
            except:
                log.error('订单处理过程中出现问题')
                transaction.savepoint_rollback(rollback)
                return Response({'message': '对不起，更新订单相关信息失败了'}, status=status.HTTP_400_BAD_REQUEST)
            pay_time = datetime.fromtimestamp(order.pay_time.timestamp()).strftime("%Y-%m-%d %H:%M:%S")
        return Response({'message': '订单支付成功',
                         'success': 'success',
                         'pay_time': pay_time,
                         'course_list': course_list,
                         'real_price': order.real_price}, status=status.HTTP_200_OK)
