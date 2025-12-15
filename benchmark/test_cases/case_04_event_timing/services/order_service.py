"""订单服务"""
from events.event_bus import EventBus
from repository.order_repository import OrderRepository

class OrderService:
    def __init__(self):
        self.event_bus = EventBus()
        self.order_repo = OrderRepository()

    def create_order(self, user_id: int, product_id: int, quantity: int) -> dict:
        """
        创建订单

        Bug: 事件发布时序错误
        先发布事件，再保存到数据库
        导致事件监听器查询订单时可能找不到
        """
        order = {
            "id": self._generate_id(),
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "status": "created"
        }

        # Bug: 先发布事件
        self.event_bus.publish("order_created", {"order_id": order["id"], "user_id": user_id})

        # 后保存订单 - 事件监听器可能在这之前就查询了
        self.order_repo.save(order)

        return order

    def _generate_id(self) -> int:
        import random
        return random.randint(10000, 99999)
