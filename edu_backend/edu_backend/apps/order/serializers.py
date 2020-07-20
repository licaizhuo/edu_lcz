import random
from datetime import datetime

from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers

from course.models import CourseExpire, Course
from order.models import Order, OrderDetail


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        # pay_type 支付方式
        # order_number 订单号
        fields = ('id', 'order_number', 'pay_type')

        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'order_number': {
                'read_only': True
            },
            'pay_type': {
                'write_only': True
            },
        }

    def validate(self, attrs):
        pay_type = attrs.get('pay_type')
        try:
            Order.pay_choices[pay_type]
        except Order.DoesNotExist:
            raise serializers.ValidationError("您选择的支付方式不被允许")
        return attrs

    def create(self, validated_data):
        """生成订单与订单详情"""
        # user_id = self.context['request'].user.id
        user_id = 1

        # 生成唯一的订单号
        order_number = datetime.now().strftime("%Y%m%d%H%M%S%f") + "%06d" % user_id + "%08d" % random.randint(0, 999999)
        with transaction.atomic():
            rollback = transaction.savepoint()
            try:
                order = Order.objects.create(
                    order_title="百知教育在线课程订单",
                    total_price=0,
                    real_price=0,
                    order_number=order_number,
                    order_status=0,
                    pay_type=validated_data.get('pay_type'),
                    credit=0,
                    coupon=0,
                    order_desc="走上大牛之路",
                    user_id=user_id,
                )
            except:
                transaction.savepoint_commit(rollback)
                raise serializers.ValidationError("订单生成失败")
            redis_connection = get_redis_connection('cart')
            pipeline = redis_connection.pipeline()
            select_list_bytes = redis_connection.smembers('select_%s' % user_id)
            cart_list_bytes = redis_connection.hgetall('cart_%s' % user_id)
            if not select_list_bytes:
                transaction.savepoint_commit(rollback)
                raise serializers.ValidationError("订单生成失败")
            total_price = 0.00
            total_real_price = 0.00
            for course_id_byte, expire_byte in cart_list_bytes.items():
                course_id = int(course_id_byte)
                expire_id = int(expire_byte)
                if course_id_byte in select_list_bytes:
                    try:
                        # 根据课程id获取对应的课程对象
                        course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                    except Course.DoesNotExist:
                        transaction.savepoint_commit(rollback)
                        raise serializers.ValidationError("订单生成失败")

                    expire_text = "永久有效"
                    course_price = str(course.price)
                    try:
                        if expire_id > 0:
                            ce = CourseExpire.objects.get(is_show=True, is_delete=False, pk=expire_id)
                            expire_text = ce.expire_text
                            course_price = ce.price
                    except CourseExpire.DoesNotExist:
                        continue
                    course_real_price = course.real_expire_price(expire_id)
                    try:
                        OrderDetail.objects.create(
                            order=order,
                            course=course,
                            expire=expire_id,
                            price=course_price,
                            real_price=course_real_price,
                            discount_name=course.discount_name
                        )
                    except:
                        transaction.savepoint_commit(rollback)
                        raise serializers.ValidationError("订单生成失败")

                    total_price += float(course_price)
                    total_real_price += float(course_real_price)
                    pipeline.hdel('cart_%s' % user_id, course_id)
                    pipeline.srem('select_%s' % user_id, course_id)
            try:
                order.total_price = total_price
                order.real_price = total_real_price
                order.save()
                pipeline.execute()
            except:
                transaction.savepoint_commit(rollback)
                raise serializers.ValidationError("订单生成失败")

        return order
