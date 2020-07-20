import random
import re
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as http_status, serializers
from edu_backend.libs.geetest import GeetestLib
from edu_backend.settings import constants
from user.models import UserInfo
from user.serializers import UserRegisterModelSerializer
from user.utils import get_user_by_account, Message

pc_geetest_id = "6f91b3d2afe94ed29da03c14988fb4ef"
pc_geetest_key = "7a01b1933685931ef5eaf5dabefd3df2"


# USER_ID = 0
# STATUS = False


class CaptchaAPIView(APIView):
    """极验验证码（图片）"""

    # user_id = 0
    # status = False

    def get(self, request, *args, **kwargs):
        """获取验证码"""

        # 能够实现并发吗？多用户登入，在验证的时候，会错乱吧？？？
        # global USER_ID
        # USER_ID = 0
        # global STATUS
        # STATUS = False
        username = request.query_params.get("username")
        # 通过user下的utils的自定义函数，获取用户，这个自定义函数，可以实现账号和密码登入
        user = get_user_by_account(username)

        # 判断用户是否存在
        if user is None:
            return Response({'message': "用户不存在"}, status=http_status.HTTP_400_BAD_REQUEST)

        # 通过定义的全局的id和key，在极验获取相应的对象和数据
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        # 获取redis连接
        redis_connection = get_redis_connection('ji_yan')
        # 将验证码对应的值，存储在redis中，并且设置存活时间
        redis_connection.setex("jy_%s" % username, constants.JI_YAN_TIME, "%s_%s" % (user.id, gt.pre_process(user.id)))

        # 获取challenge
        # 源码 self._response_str = self._make_response_format(status, challenge, new_captcha)
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self, request, *args, **kwargs):
        """验证验证码"""
        username = request.data.get('username')
        if not username:
            return Response({'message': "出现未知错误"}, status=http_status.HTTP_400_BAD_REQUEST)

        # 获取redis连接
        redis_connection = get_redis_connection('ji_yan')
        # 将验证码对应的值，存储在redis中，并且设置存活时间
        user_id_and_status = redis_connection.get("jy_%s" % username)
        if not user_id_and_status:
            return Response({'message': "验证码已过期"}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 从redis中获取的值，进行解码，然后在进行切割，获得id和status
        user_id_str, status_str = user_id_and_status.decode().split("_")
        user_id = int(user_id_str)
        status = int(status_str)

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)

        # 通过前端传来的数据获取对应的值
        challenge = request.data.get(gt.FN_CHALLENGE, '')
        validate = request.data.get(gt.FN_VALIDATE, '')
        seccode = request.data.get(gt.FN_SECCODE, '')

        # 判断
        if status:
            # print(USER_ID, "---", challenge, validate, seccode)
            # 获取验证结果
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result, status=http_status.HTTP_200_OK)


class UserRegisterAPIView(CreateAPIView):
    """用手机号注册"""
    queryset = UserInfo.objects.all()
    serializer_class = UserRegisterModelSerializer


class CheckPhoneAPIView(APIView):
    """检查手机号是否合法"""

    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone')
        if not re.match(r'^1[3-9][0-9]{9}$', phone):
            raise serializers.ValidationError("手机号不符合规范")
        user = get_user_by_account(phone)
        if user:
            raise serializers.ValidationError("手机号已被注册")

        return Response({"message": "OK"}, status=http_status.HTTP_200_OK)


class SendMessageAPIView(APIView):
    """发送手机号验证码"""

    def get(self, request, *args, **kwargs):
        # 获取手机号
        mobile = request.GET.get('mobile')
        # 用select来区分是注册时的验证码还是登入是的验证码
        select = request.GET.get('select')
        # 若不是登入或注册发送的验证码，则不能进行发送验证码
        if select not in ['1', '2']:
            raise serializers.ValidationError("出现错误，请刷新页面")
        # sms=短信息服务
        redis_connection = get_redis_connection("sms_code")
        # 判断60秒内是否已经存在验证码了，如果存在，则不再发送。
        if redis_connection.get("%s_sms_%s" % (select, mobile)):
            raise serializers.ValidationError("您在60秒内，已发送过验证码")

        # 随机产生一个6位的验证码
        code = "%06d" % random.randint(0, 999999)

        # 不需要判断，会覆盖
        # if redis_connection.get("%s_mobile_%s" % (select, mobile)):
        #     redis_connection.delete("%s_mobile_%s" % (select, mobile))

        # 用来判断60秒内是否已经发送过验证码
        redis_connection.setex("%s_sms_%s" % (select, mobile), constants.SMS_EXPIRE_TIME, code)

        # 用来验证前端传来的验证码是否正确
        redis_connection.setex("%s_mobile_%s" % (select, mobile), constants.MOBILE_EXPIRE_TIME, code)

        # 用来设置验证码校验的有效次数
        redis_connection.setex("%s_mobile_number_%s" % (select, mobile), constants.MOBILE_EXPIRE_TIME,
                               constants.VERIFICATION_NUMBER)

        try:
            message = Message(constants.API_KEY)
            message.send_message(mobile, code)
        except:
            raise serializers.ValidationError("验证码发送失败")

        return Response({'message': "验证码发送成功"}, status=http_status.HTTP_200_OK)
