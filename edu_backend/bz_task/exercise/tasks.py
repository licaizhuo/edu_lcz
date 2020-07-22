from bz_task.main import app


# celery的任务必须卸载tasks的文件中，使用其他的名称不识别
# 可以不指定，默认是一个目录名和函数名拼接的名称
from edu_backend.settings import constants
from user.utils import Message


@app.task(name="send_sms")
def send_sms(mobile, code):
    # print("我是一个任务")
    message = Message(constants.API_KEY)
    message.send_message(mobile, code)
    return "hello"


@app.task(name="send_mail")
def send_mail():
    print("我是第二个任务")

    return "email"
