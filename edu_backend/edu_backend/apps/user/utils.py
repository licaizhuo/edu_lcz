import requests
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django_redis import get_redis_connection

from edu_backend.settings import constants
from user.models import UserInfo


def jwt_response_payload_handler(token, user=None, request=None):
    redis_connection = get_redis_connection('cart')
    # 获取redis中存储的购物车的数目，保证在登入的时候，可以购物车的数量直接显示
    cart_length = redis_connection.hlen('cart_%s' % user.id)
    return {
        # 默认返回一个token
        'token': token,
        'username': user.username,
        'user_id': user.id,
        'cart_length': cart_length,
    }


def get_user_by_account(account):
    """
    自定义一个函数，可以通过手机号和用户名获取对应的用户
    :param account: 手机号或者时用户名
    :return: 返回一个用户
    """
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
        # 调用一个自定义函数，获取用户
        user = get_user_by_account(username)
        # 首先判断用户是否时用密码登入的，如果是使用密码且密码正确，那么返回用户
        if user and user.check_password(password) and user.is_authenticated:
            return user
        # 如果使用的不是密码，说明使用的是验证码
        redis_connection = get_redis_connection("sms_code")

        # 使用手机号获取已经验证的次数，2_mobile_number_%s" % username用2来说明是登入的验证码
        phone_number = redis_connection.get("2_mobile_number_%s" % username)
        # 如果验证次数用完，或者不存在验证次数，就直接返回None，也就是验证不通过
        if (int(phone_number.decode()) < 1) or not phone_number:
            return None
        # 如果还有验证次数，将验证次数减少一次
        redis_connection.decr("2_mobile_number_%s" % username)

        # 获取验证码
        phone_code = redis_connection.get("2_mobile_%s" % username)
        # 如果没有获取到验证码或者验证码和前端传来的不一致，则返回None
        if not phone_code or (phone_code.decode() != password):
            return None
        return user


class Message(object):
    """在SendMessageAPIView中调用，用来发送短信的类"""

    def __init__(self, api_key):
        # 初始配置发送短信所需的key，和单条发送的接口
        self.api_key = api_key
        self.single_send_url = constants.SINGLE_SEND_URL

    def send_message(self, phone, code):
        """
        发送验证码的方法，params的text的格式必须和云片网上设置的模板相同
        :param phone: 手机号
        :param code: 随机的6位验证码
        """
        params = {
            "apikey": self.api_key,
            'mobile': phone,
            'text': "【李才卓test】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }
        req = requests.post(self.single_send_url, data=params)


if __name__ == '__main__':
    message = Message("8646f7218e2cf5606ba1a628c0555bf9")
    message.send_message("15036669116", "123456")
