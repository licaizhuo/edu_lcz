from celery.schedules import crontab

from bz_task.main import app

# 任务队列的存储地址
broker_url = "redis://192.168.217.129:7000/11"
# 任务结果的存储地址
result_backend = "redis://192.168.217.129:7000/10"

app.conf.beat_schedule = {
    'check_order_out_time': {
        # 本次调度的任务
        'task': 'check_order',
        # 定时任务的调度周期
        'schedule': crontab(),  # 每分钟调度一次
    },
}
