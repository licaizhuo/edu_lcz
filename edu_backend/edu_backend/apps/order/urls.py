from django.urls import path

from order import views

urlpatterns = [
    path("option/", views.OrderApiView.as_view()),
]
