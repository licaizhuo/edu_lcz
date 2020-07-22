import logging

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from course.models import Course, CourseExpire

# 获取日志记录器
from edu_backend.settings import constants
from user.models import UserCourse

log = logging.getLogger('django')


class CartViewSet(ViewSet):
    """"购物车相关的方法"""

    permission_classes = [IsAuthenticated]

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
        expire_id = 0
        user_course = UserCourse.objects.filter(user=user_id, course=course_id)
        if user_course:
            return Response({"message": "你已经购买过此课程，请勿重复购买"}, status=status.HTTP_400_BAD_REQUEST)
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
            pipeline.hset('cart_%s' % user_id, course_id, expire_id)
            # 被勾选商品
            pipeline.sadd('select_%s' % user_id, course_id)
            # 执行管道，与redis连接
            pipeline.execute()
            cart_length = redis_connection.hlen('cart_%s' % user_id)
        except:
            log.error('购物车数据存储失败')
            return Response({"message": "参数有误，添加失败"}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

        return Response({"message": "课程添加成功，已在购物车里等候主人", 'cart_length': cart_length}, status=status.HTTP_200_OK)

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
        pipeline = redis_connection.pipeline()
        # 获取redis中所有关于购物车的商品的id和商品对应的有效期
        cart_list_bytes = redis_connection.hgetall('cart_%s' % user_id)
        # 获取redis中所有关于购物车的数据的被勾选商品的id
        select_lsi_bytes = redis_connection.smembers('select_%s' % user_id)
        data = []
        # 遍历cart_list_bytes，获取课程id和有效期
        for course_id_byte, expire_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            # 有效期，如果没有进行修改，初始值是我们增加时候设置的 0
            expire_id = int(expire_byte)
            try:
                # 根据课程id获取对应的课程对象
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except Course.DoesNotExist:
                # 如果课程不存在或下架了，在redis中用户的购物内删除对应的课程id
                pipeline.hdel('cart_%s' % user_id, course_id)
                # 如果课程不存在或下架了，在redis中用户的购物内选中的课程id，在这里删除
                pipeline.srem('select_%s' % user_id, course_id)
                continue

            data.append({
                # 判断购物车内的商品是否是选中状态，如果不修改，默认是勾选
                'selected': True if course_id_byte in select_lsi_bytes else False,
                # 获取图片的路径
                'course_img': constants.IMAGE_SRC + course.course_img.url,
                'id': course.id,
                'name': course.name,
                'expire_id': expire_id,
                'course_real_price': course.real_expire_price(expire_id),
                'expire_list': course.expire_list,
            })
        pipeline.execute()
        return Response(data)

    def change_select(self, request, *args, **kwargs):
        """改变购物车内的商品选择状态"""
        user_id = request.user.id
        selected = request.data.get('selected')
        course_id = request.data.get('course_id')
        try:
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({"message": "当前课程已下架或不存在"}, status=status.HTTP_400_BAD_REQUEST)
        redis_connection = get_redis_connection('cart')
        if selected:
            redis_connection.sadd('select_%s' % user_id, course_id)
            return Response({"message": "课程已成功选中"}, status=status.HTTP_200_OK)
        else:
            redis_connection.srem('select_%s' % user_id, course_id)
            return Response({"message": "课程已取消选中"}, status=status.HTTP_200_OK)

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

        return Response({"message": "课程删除成功", 'cart_length': cart_length}, status=status.HTTP_200_OK)

    def change_expire(self, request):
        """改变redis中的课程的有效期"""
        user_id = request.user.id
        course_id = request.data.get('course_id')
        expire_id = request.data.get('expire_id')
        try:
            course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            if expire_id > 0:
                expire_item = CourseExpire.objects.filter(is_show=True, is_delete=False, pk=expire_id)
                if not expire_item:
                    raise Course.DoesNotExist()
        except Course.DoesNotExist:
            return Response({"message": "当前课程已下架或不存在"}, status=status.HTTP_400_BAD_REQUEST)
        redis_connection = get_redis_connection('cart')
        redis_connection.hset('cart_%s' % user_id, course_id, expire_id)
        course_real_price = course.real_expire_price(expire_id)
        return Response({"message": "切换有效期成功", 'course_real_price': course_real_price}, status=status.HTTP_200_OK)

    def get_select_course(self, request):
        """
        获取购物车中被选择的商品
        """
        user_id = request.user.id
        # user_id = 1
        redis_connection = get_redis_connection('cart')
        pipeline = redis_connection.pipeline()
        select_list_bytes = redis_connection.smembers('select_%s' % user_id)
        cart_list_bytes = redis_connection.hgetall('cart_%s' % user_id)
        data = []
        total_price = 0
        for course_id_byte, expire_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_byte)
            if course_id_byte in select_list_bytes:
                try:
                    # 根据课程id获取对应的课程对象
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    # 如果课程不存在或下架了，在redis中用户的购物内删除对应的课程id
                    pipeline.hdel('cart_%s' % user_id, course_id)
                    # 如果课程不存在或下架了，在redis中用户的购物内选中的课程id，在这里删除
                    pipeline.srem('select_%s' % user_id, course_id)

                    continue
                user_course = UserCourse.objects.filter(user=user_id, course=course_id)
                if user_course:
                    return Response({"message": "您的购物车中，存在已购买的课程" + course.name}, status=status.HTTP_400_BAD_REQUEST)
                course_price = str(course.price)
                expire_text = "永久有效"
                try:
                    if expire_id > 0:
                        ce = CourseExpire.objects.get(is_show=True, is_delete=False, pk=expire_id)
                        expire_text = ce.expire_text
                        course_price = ce.price
                except CourseExpire.DoesNotExist:
                    continue

                course_real_price = course.real_expire_price(expire_id)
                data.append({
                    # 获取图片的路径
                    'course_img': constants.IMAGE_SRC + course.course_img.url,
                    'id': course.id,
                    'name': course.name,
                    # 活动的名称
                    "discount_name": course.discount_name,
                    # 有效期的文本
                    'expire_text': expire_text,
                    # 原价
                    'course_price': course_price,
                    # 经过活动的价格
                    'course_real_price': course_real_price,
                })
                total_price += float(course_real_price)
        pipeline.execute()
        return Response({"course_list": data, 'total_price': total_price}, status=status.HTTP_200_OK)

    def if_select_all(self, request):
        """进行课程的全选和全不选的修改"""
        # 获取用户id
        user_id = request.user.id
        select_all = request.data.get('select_all')
        redis_connection = get_redis_connection('cart')
        if select_all:

            pipeline = redis_connection.pipeline()
            cart_list_bytes = redis_connection.hgetall('cart_%s' % user_id)

            # 遍历cart_list_bytes，获取课程id和有效期
            for course_id_byte, expire_byte in cart_list_bytes.items():
                course_id = int(course_id_byte)
                try:
                    # 根据课程id获取对应的课程对象
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    # 如果课程不存在或下架了，在redis中用户的购物内删除对应的课程id
                    pipeline.hdel('cart_%s' % user_id, course_id)
                    # 如果课程不存在或下架了，在redis中用户的购物内选中的课程id，在这里删除
                    pipeline.srem('select_%s' % user_id, course_id)
                    continue
                pipeline.sadd('select_%s' % user_id, course_id)
            pipeline.execute()
        else:
            # 取消购物车内所有选中
            redis_connection.delete('select_%s' % user_id)
        return Response({"message": "成功"}, status=status.HTTP_200_OK)

    def delete_all_option(self, request):
        """将选择的课程全部删除"""

        user_id = request.user.id
        redis_connection = get_redis_connection('cart')
        pipeline = redis_connection.pipeline()
        select_list_bytes = redis_connection.smembers('select_%s' % user_id)

        # 遍历cart_list_bytes，获取课程id和有效期
        for course_id_byte in select_list_bytes:
            course_id = int(course_id_byte)
            pipeline.hdel('cart_%s' % user_id, course_id)

        pipeline.execute()
        return Response({"message": "删除成功"}, status=status.HTTP_200_OK)
