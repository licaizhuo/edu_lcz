from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from user import views

urlpatterns = [
    path('login/', obtain_jwt_token),
    path('captcha/', views.CaptchaAPIView.as_view()),
    path('register/', views.UserRegisterAPIView.as_view()),
    path('check_phone/', views.CheckPhoneAPIView.as_view()),
    path('sms/', views.SendMessageAPIView.as_view()),
]
