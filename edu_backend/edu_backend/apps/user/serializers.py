import re

from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from user.models import UserInfo
from user.utils import get_user_by_account


class UserRegisterModelSerializer(serializers.ModelSerializer):
    # 自定义字段用来存用户的token和sms验证码
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
        # password = attrs.get('password')
        sms_code = attrs.get('sms_code')

        # 判断手机号是否符合符合格式
        if not re.match(r'^1[3-9][0-9]{9}$', phone):
            raise serializers.ValidationError("手机号格式错误")

        # 获取redis连接
        redis_connection = get_redis_connection("sms_code")
        # 用1来说明是注册的验证码，获取检验的次数
        phone_number = redis_connection.get("1_mobile_number_%s" % phone)
        # 如果验证次数用完，或者不存在验证次数，则直接报错
        if not phone_number or (int(phone_number.decode()) < 1):
            raise serializers.ValidationError("输入次数过多，请重新申请验证码")
        # 如果还有验证次数，将验证次数减少一次
        redis_connection.decr("1_mobile_number_%s" % phone)

        # # 获取验证码
        phone_code = redis_connection.get("1_mobile_%s" % phone)
        # 如果没有获取到验证码或者验证码和前端传来的不一致，则报错
        if not phone_code or (phone_code.decode() != sms_code):
            raise serializers.ValidationError("验证码输入错误")

        try:
            # 检验是否手机号是否已被注册
            user = get_user_by_account(phone)
        except:
            user = None

        # 若已被注册则报错
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
        # 获取用户对用的载荷
        payload = jwt_payload_handler(user)
        # 获取token，并且将token添加到user中
        user.token = jwt_encode_handler(payload)
        return user
