from django.urls import path

from order import views

urlpatterns = [
    path("option/", views.OrderApiView.as_view()),
    path("list/", views.OrderListViewSet.as_view({'get': 'get_order_list'})),
]
