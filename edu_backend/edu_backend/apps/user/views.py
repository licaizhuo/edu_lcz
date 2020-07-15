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

USER_ID = 0
STATUS = False


class CaptchaAPIView(APIView):
    """极验验证码"""
    user_id = 0
    status = False

    def get(self, request, *args, **kwargs):
        """获取验证码"""
        global USER_ID
        USER_ID = 0
        global STATUS
        STATUS = False
        username = request.query_params.get("username")
        user = get_user_by_account(username)
        if user is None:
            return Response({'message': "用户不存在"}, status=http_status.HTTP_400_BAD_REQUEST)
        USER_ID = user.id
        # print("111", USER_ID)
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        STATUS = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self, request, *args, **kwargs):
        """验证验证码"""
        # print(request.data)
        # print(type(request.data))
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.data.get(gt.FN_CHALLENGE, '')
        # print(challenge)
        validate = request.data.get(gt.FN_VALIDATE, '')
        seccode = request.data.get(gt.FN_SECCODE, '')
        # status = request.session[gt.GT_STATUS_SESSION_KEY]
        # user_id = request.session["user_id"]
        if STATUS:
            print(USER_ID, "---", challenge, validate, seccode)
            result = gt.success_validate(challenge, validate, seccode, USER_ID)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)


class UserRegisterAPIView(CreateAPIView):
    queryset = UserInfo.objects.all()
    serializer_class = UserRegisterModelSerializer


class CheckPhoneAPIView(APIView):

    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone')
        if not re.match(r'^1[3-9][0-9]{9}$', phone):
            raise serializers.ValidationError("手机号不符合规范")
        user = get_user_by_account(phone)
        if user:
            raise serializers.ValidationError("手机号已被注册")

        return Response({"message": "OK"})


class SendMessageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        mobile = request.GET.get('mobile')
        select = request.GET.get('select')
        if select not in ['1', '2']:
            raise serializers.ValidationError("出现错误，请刷新页面")
        redis_connection = get_redis_connection("sms_code")
        if redis_connection.get("%s_sms_%s" % (select, mobile)):
            raise serializers.ValidationError("您在60秒内，已发送过验证码")

        code = "%06d" % random.randint(100000, 999999)
        if redis_connection.get("%s_mobile_%s" % (select, mobile)):
            redis_connection.delete("%s_mobile_%s" % (select, mobile))
        redis_connection.setex("%s_sms_%s" % (select, mobile), constants.SMS_EXPIRE_TIME, code)
        redis_connection.setex("%s_mobile_%s" % (select, mobile), constants.MOBILE_EXPIRE_TIME, code)
        redis_connection.setex("%s_mobile_number_%s" % (select, mobile), constants.MOBILE_EXPIRE_TIME,
                               constants.VERIFICATION_NUMBER)
        try:
            message = Message(constants.API_KEY)
            message.send_message(mobile, code)
        except:
            raise serializers.ValidationError("验证码发送失败")

        return Response({'message': "验证码发送成功"}, status=http_status.HTTP_200_OK)
