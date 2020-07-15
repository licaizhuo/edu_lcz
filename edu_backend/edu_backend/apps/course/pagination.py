from rest_framework.pagination import PageNumberPagination


class CoursePageNumberPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size = 3
    max_page_size = 10
    page_size_query_param = 'size'
