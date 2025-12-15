"""通知服务"""
from events.event_bus import EventBus
from repository.order_repository import OrderRepository

class NotificationService:
    def __init__(self):
        self.event_bus = EventBus()
        self.order_repo = OrderRepository()
        self.notifications_sent = []
        self._setup_listeners()

    def _setup_listeners(self):
        """设置事件监听"""
        self.event_bus.subscribe("order_created", self._on_order_created)

    def _on_order_created(self, event):
        """
        处理订单创建事件

        Bug: 尝试从数据库查询订单详情
        但此时订单可能还没保存
        """
        order_id = event.data["order_id"]
        user_id = event.data["user_id"]

        # 尝试获取订单详情
        order = self.order_repo.get(order_id)

        if order is None:
            # Bug 会触发这里
            raise ValueError(f"Order {order_id} not found in database!")

        notification = {
            "type": "order_created",
            "user_id": user_id,
            "order_id": order_id,
            "message": f"Your order #{order_id} has been created!"
        }
        self.notifications_sent.append(notification)

    def get_notifications(self):
        return self.notifications_sent
