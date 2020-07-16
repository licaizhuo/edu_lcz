import logging

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from course.models import Course

# 获取日志记录器
from edu_backend.settings import constants

log = logging.getLogger('django')


class CartViewSet(ViewSet):
    """"购物车相关的方法"""

    # permission_classes = [IsAuthenticated]

    def add_cart(self, request, *args, **kwargs):
        """
        将用户想要购买的商品存入到购物车
        :param request: 用户id，课程id，勾选状态，有效期
        :return:
        """
        # 前端传输过来的课程id
        course_id = request.data.get("course_id")
        # 从请求里获取到的经过验证的用户的id，如果没有经过验证，是不可以获得user的
        user_id = request.user.id
        # 有效期设置为永久有效
        expire = 0
        try:
            # 判断课程id对应的课程是否存在。课程不存在或存在多个都会报错
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            # 课程不存在，返回的data
            return Response({"message": "参数有误，课程不存在"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # 获取redis连接对象啊
            redis_connection = get_redis_connection('cart')
            # 获取管道
            pipeline = redis_connection.pipeline()
            # 管道开启
            pipeline.multi()
            # 商品的信息以及有效期
            pipeline.hset('cart_%s' % user_id, course_id, expire)
            # 被勾选商品
            pipeline.sadd('select_%s' % user_id, course_id)
            # 执行管道，与redis连接
            pipeline.execute()
            cart_length = redis_connection.hlen('cart_%s' % user_id)
        except:
            log.error('购物车数据存储失败')
            return Response({"message": "参数有误，添加失败"}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

        return Response({"message": "商品添加成功，已在购物车里等候主人", 'cart_length': cart_length}, status=status.HTTP_200_OK)

    def list_cart(self, request, *args, **kwargs):
        """
        展示购物车
        :param request: 用户id，课程id，勾选状态，有效期
        :return:
        """
        # 获取用户id
        user_id = request.user.id
        # user_id = 1
        # 获取redis连接
        redis_connection = get_redis_connection('cart')
        # 获取redis中所有关于购物车的数据的id
        cart_list_bytes = redis_connection.hgetall('cart_%s' % user_id)
        # 获取redis中所有关于购物车的数据的被勾选商品的id
        select_lsi_bytes = redis_connection.smembers('select_%s' % user_id)
        data = []
        for course_id_byte, expire_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            expire = int(expire_byte)
            try:
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except Course.DoesNotExist:
                redis_connection.hdel('cart_%s' % user_id, course_id)
                redis_connection.srem('select_%s' % user_id, course_id)
                continue

            data.append({

                'selected': True if course_id_byte in select_lsi_bytes else False,
                'course_img': constants.IMAGE_SRC + course.course_img.url,
                'id': course.id,
                'name': course.name,
                'expire': expire,
                'course_price': course.price
            })
        return Response(data)

    def change_select(self, request, *args, **kwargs):
        """改变购物车内的商品选择状态"""
        user_id = request.user.id
        selected = request.data.get('selected')
        course_id = request.data.get('course_id')
        try:
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({"message": "当前商品已下架或不存在"}, status=status.HTTP_400_BAD_REQUEST)
        redis_connection = get_redis_connection('cart')
        if selected:
            redis_connection.sadd('select_%s' % user_id, course_id)
            return Response({"message": "商品已成功选中"}, status=status.HTTP_200_OK)
        else:
            redis_connection.srem('select_%s' % user_id, course_id)
            return Response({"message": "商品已取消选中"}, status=status.HTTP_200_OK)

    def delete_cart(self, request, *args, **kwargs):
        """
        将用户想要购买的商品存入到购物车
        :param request: 用户id，课程id，勾选状态，有效期
        :return:
        """

        # 前端传输过来的课程id
        course_id = request.data.get("course_id")
        # 从请求里获取到的经过验证的用户的id，如果没有经过验证，是不可以获得user的
        user_id = request.user.id
        try:
            # 获取redis连接对象啊
            redis_connection = get_redis_connection('cart')
            # 获取管道
            pipeline = redis_connection.pipeline()
            # 管道开启
            pipeline.multi()
            pipeline.hdel('cart_%s' % user_id, course_id)
            pipeline.srem('select_%s' % user_id, course_id)
            # 执行管道，与redis连接
            pipeline.execute()
            cart_length = redis_connection.hlen('cart_%s' % user_id)
        except:
            log.error('购物车数据存储失败')
            return Response({"message": "参数有误，删除失败"}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

        return Response({"message": "商品删除成功", 'cart_length': cart_length}, status=status.HTTP_200_OK)
