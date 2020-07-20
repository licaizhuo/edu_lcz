from django.urls import path

from course import views

urlpatterns = [
    path("category/", views.CourseCategoryAPIView.as_view()),
    path("list/", views.CourseListAPIView.as_view()),
    path("course_info/<str:id>/", views.CourseInfoAPIView.as_view()),
    path("list_filter/", views.CourseFilterListAPIView.as_view()),
    path("chapter/", views.ChapterListAPIView.as_view()),
    path("comment/", views.UserIssueStorageViewSet.as_view(
        {'post': 'add_comment', 'get': 'list_comment', 'delete': 'delete_comment'})),
]
