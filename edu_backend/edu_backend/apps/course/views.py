import logging
from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status

from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from course.models import CourseCategory, Course, CourseChapter
from course.pagination import CoursePageNumberPagination
from course.serializers import CourseModelCategorySerializer, CourseListModelSerializer, CourseInfoModelSerializer, \
    CourseChapterModelSerializer
from user.models import UserInfo

log = logging.getLogger('django')


class CourseCategoryAPIView(ListAPIView):
    """获取所有的课程分类"""
    queryset = CourseCategory.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseModelCategorySerializer


class CourseListAPIView(ListAPIView):
    """获取所有的课程，没有排序，分页，过滤的条件"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseListModelSerializer


class CourseFilterListAPIView(ListAPIView):
    """获取所有的课程，有排序，分页，过滤的条件"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseListModelSerializer
    # DjangoFilterBackend 过滤器 在django_filters.rest_framework的中
    # OrderingFilter 排序 在rest_framework.filters中
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # 用来过滤的字段
    filter_fields = ('course_category',)
    # 用来排序的字段
    ordering_fields = ('id', 'students', 'price')
    # 分页器
    pagination_class = CoursePageNumberPagination


class CourseInfoAPIView(RetrieveAPIView):
    """获取单个课程的详细信息"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseInfoModelSerializer
    lookup_field = 'id'


class ChapterListAPIView(ListAPIView):
    """获取指定课程的章节信息（章节信息中包含课时信息）"""
    queryset = CourseChapter.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseChapterModelSerializer
    # DjangoFilterBackend 过滤器 在django_filters.rest_framework的中
    filter_backends = [DjangoFilterBackend]
    # 用来过滤的字段
    filter_fields = ("course_id",)
    # filter_fields = ("course",)


class UserIssueStorageViewSet(ViewSet):
    """用户留言和问题的类"""
    # 权限设置，登入，所有的功能都可以访问，未登入只可以读
    permission_classes = [IsAuthenticatedOrReadOnly]

    def add_comment(self, request, *args, **kwargs):
        """
        添加用户留言
        :param request: 请求中包含课程id，用户id，内容
        :return: 返回提示信息，
        """

        # 获取课程的id，当作哈希的集合的名称的一部分
        course_id = request.data.get('course_id')
        # 用户id 集合中key值
        user_id = request.data.get('user_id')
        content = request.data.get('content')

        try:
            # 判断课程id对应的课程是否存在。课程不存在或存在多个都会报错
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            # 课程不存在，返回的data
            return Response({"message": "参数有误，课程不存在"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 获取redis连接
            redis_connection = get_redis_connection("user_comment")
            # 进行存储,course_id 来保证名称唯一
            # 第二个参数，user_id, datetime.now() 来保证key唯一，因为用户可能不是发表一个评论或问题描述，所以使用时间戳来区分
            # 第三个参数就是评论或问题内容
            comment_timestamp = int(datetime.now().timestamp())
            redis_connection.hset("comment_%s" % course_id, "%s_%s" % (user_id, comment_timestamp), content)
        except:
            log.error('评论存储失败')
            return Response({"message": "参数有误，添加失败"}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        return Response({"message": '评论发表成功','comment_timestamp':comment_timestamp}, status=status.HTTP_200_OK)

    def list_comment(self, request, *args, **kwargs):
        """

        :param request:
        :return: 返回一个留言和回复的列表
        """
        # 获取课程的id，当作哈希的集合的名称的一部分
        course_id = request.query_params.get('course_id')
        # course_id = 1

        try:
            # 判断课程id对应的课程是否存在。课程不存在或存在多个都会报错
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            # 课程不存在，返回的data
            return Response({"message": "参数有误，课程不存在"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 获取redis连接
            redis_connection = get_redis_connection("user_comment")
            data = []
            # 获取当前课程的评论的列表
            comment_list = redis_connection.hgetall("comment_%s" % course_id)
            for comment_key, comment_value in comment_list.items():
                user_id, comment_timestamp = (comment_key.decode()).split('_')
                content = comment_value.decode()
                user = UserInfo.objects.filter(pk=user_id)
                # # replay = []
                if user:
                    data.append({
                        'user_id': user_id,
                        'username': user.first().username,
                        'content': content,
                        'comment_timestamp': comment_timestamp
                    })
        except:
            log.error('获取评论列表失败')
            return Response({"message": "参数有误，添加失败"}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        return Response(data=data, status=status.HTTP_200_OK)

    def delete_comment(self, request, *args, **kwargs):
        """

        :param request:
        :return: 删除留言
        """
        # 获取课程的id，当作哈希的集合的名称的一部分
        course_id = request.data.get('course_id')
        user_id = request.data.get('user_id')
        comment_timestamp = request.data.get('comment_timestamp')
        # course_id = 1

        try:
            # 获取redis连接
            redis_connection = get_redis_connection("user_comment")
            redis_connection.hdel("comment_%s" % course_id, "%s_%s" % (user_id, comment_timestamp))

        except:
            log.error('评论删除失败')
            return Response({"message": "参数有误，评论删除失败"}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        return Response({"message": "评论删除成功"}, status=status.HTTP_200_OK)
