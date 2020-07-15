import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status

from edu_backend.utils.response import MyResponse

logger = logging.getLogger('django')


def exception_handler(exc, context):
    error = "%s--%s--%s" % (context['view'], context['request'].method, exc)

    response = drf_exception_handler(exc, context)
    if response is None:
        logger.error(error)
        return MyResponse(data_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          data_message="程序内部错误，请稍等一会儿~", exception=None)
    return response
