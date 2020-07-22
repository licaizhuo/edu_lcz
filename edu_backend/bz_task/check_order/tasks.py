import logging
from datetime import datetime

from bz_task.main import app
from edu_backend.settings import constants
from order.models import Order

log = logging.getLogger('django')


@app.task(name="check_order")
def check_order():
    # print("现在是练习")
    order_list = Order.objects.filter(order_status=0, is_delete=False)
    for order in order_list:
        out_time = datetime.now().timestamp() - order.create_time.timestamp()
        if out_time > constants.ORDER_TIME:
            try:
                order.order_status = 3
                order.save()
            except:
                log.error("定时任务，更新支付状态失败")
                continue
