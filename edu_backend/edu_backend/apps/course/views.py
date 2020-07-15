from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView

from course.models import CourseCategory, Course, CourseChapter
from course.pagination import CoursePageNumberPagination
from course.serializers import CourseModelCategorySerializer, CourseListModelSerializer, CourseInfoModelSerializer, \
    CourseChapterModelSerializer


class CourseCategoryAPIView(ListAPIView):
    queryset = CourseCategory.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseModelCategorySerializer


class CourseListAPIView(ListAPIView):
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseListModelSerializer


class CourseInfoAPIView(RetrieveAPIView):
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseInfoModelSerializer
    lookup_field = 'id'


class CourseFilterListAPIView(ListAPIView):
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseListModelSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ('course_category',)
    ordering_fields = ('id', 'students', 'price')

    pagination_class = CoursePageNumberPagination


class ChapterListAPIView(ListAPIView):
    queryset = CourseChapter.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseChapterModelSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ("course_id",)
    # filter_fields = ("course",)


# class UserIssueStorageAPIView(APIView):
#
#     def get(self, request, *args, **kwargs):
#         course_id = request.GET.get('course_id')
#         user_id = request.GET.get('user_id')
#         redis_connection = get_redis_connection("user_issue")

# class UserIssueFetchAPIView(APIView):
#
#     def get(self, request, *args, **kwargs):
#         pass
