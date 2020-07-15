import re

from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from user.models import UserInfo
from user.utils import get_user_by_account


class UserRegisterModelSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=1024, read_only=True, help_text="用户token")
    sms_code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text="短信验证码")

    class Meta:
        model = UserInfo
        fields = ('id', 'username', 'phone', 'password', 'token', 'sms_code')
        extra_kwargs = {
            "id": {
                "read_only": True
            },
            "username": {
                "read_only": True
            },
            "password": {
                "write_only": True
            },
            "mobile": {
                "write_only": True
            },

        }

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        sms_code = attrs.get('sms_code')
        redis_connection = get_redis_connection("sms_code")
        phone_number = redis_connection.get("1_mobile_number_%s" % phone)
        if not phone_number or (int(phone_number.decode()) < 1):
            raise serializers.ValidationError("输入次数过多，请重新申请验证码")
        redis_connection.decr("1_mobile_number_%s" % phone)
        phone_code = redis_connection.get("1_mobile_%s" % phone)
        if not phone_code or (phone_code.decode() != sms_code):
            raise serializers.ValidationError("验证码输入错误")
        if not re.match(r'^1[3-9][0-9]{9}$', phone):
            raise serializers.ValidationError("手机号格式错误")
        try:
            user = get_user_by_account(phone)
        except:
            user = None

        if user:
            raise serializers.ValidationError("当前用户已被注册")

        return attrs

    def create(self, validated_data):
        password = validated_data.get('password')
        new_password = make_password(password)
        username = validated_data.get('phone')

        user = UserInfo.objects.create(
            username=username,
            phone=username,
            password=new_password
        )
        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)
        return user
