import requests
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django_redis import get_redis_connection
from rest_framework import serializers

from edu_backend.settings import constants
from user.models import UserInfo


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'user_id': user.id,
    }


def get_user_by_account(account):
    try:
        user = UserInfo.objects.filter(Q(username=account) | Q(phone=account)).first()
    except UserInfo.DoesNotExist:
        return None
    else:
        return user


class UserAuthenticate(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        根据账号获取用户对象
        :param request: 请求对象
        :param username:   用户名或手机
        :param password:    密码
        :return: 查询出的用户
        """
        user = get_user_by_account(username)
        if user and user.check_password(password) and user.is_authenticated:
            return user
        redis_connection = get_redis_connection("sms_code")
        phone_number = redis_connection.get("2_mobile_number_%s" % username)
        if (int(phone_number.decode()) < 1) or not phone_number:
            return None
        redis_connection.decr("2_mobile_number_%s" % username)

        phone_code = redis_connection.get("2_mobile_%s" % username)
        if not phone_code or (phone_code.decode() != password):
            return None
        return user


class Message(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.single_send_url = constants.SINGLE_SEND_URL

    def send_message(self, phone, code):
        params = {
            "apikey": self.api_key,
            'mobile': phone,
            'text': "【李才卓test】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }
        req = requests.post(self.single_send_url, data=params)


if __name__ == '__main__':
    message = Message("8646f7218e2cf5606ba1a628c0555bf9")
    message.send_message("15036669116", "123456")
