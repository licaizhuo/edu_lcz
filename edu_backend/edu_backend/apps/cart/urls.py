from django.urls import path

from cart import views

urlpatterns = [
    path('option/', views.CartViewSet.as_view({'post': "add_cart",
                                               'get': 'list_cart',
                                               'patch': 'change_select',
                                               'delete': 'delete_cart',
                                               'put': 'change_expire'})),

    path('option_all/', views.CartViewSet.as_view(
        {'delete': 'delete_all_option', 'put': 'if_select_all', 'get': 'get_select_course'})),

]
