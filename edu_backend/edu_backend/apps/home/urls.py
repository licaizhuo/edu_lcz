from django.urls import path

from home import views

urlpatterns = [
    path("banner/", views.BannerListAPIView.as_view()),
    path("header/", views.HeaderNavListAPIView.as_view()),
    path("footer/", views.FooterNavListAPIView.as_view()),
]
