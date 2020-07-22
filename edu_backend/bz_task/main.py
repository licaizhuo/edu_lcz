import os

import django
from celery import Celery

# edu是给个名称，为了以后方便使用多个实例，如果只使用一个，可以不指定
app = Celery("edu")

# 识别并加载django的配置文件  django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_backend.settings.develop')
django.setup()

# 加载配置
app.config_from_object('bz_task.config')

# 添加任务
# app.autodiscover_tasks(['bz_task.exercise', 'bz_task.file'])
app.autodiscover_tasks(['bz_task.check_order'])
# 启动celery  --loglevel=info是日志等级
# celery -A  bz_task.main worker --loglevel=info
