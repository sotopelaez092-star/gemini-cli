# Bug: 循环导入导致 ImportError
# order_service.py 导入 user_service, user_service 又导入 order_service

from services.user_service import UserService

class OrderService:
    def __init__(self):
        self.user_service = UserService()

    def create_order(self, user_id: int, product_id: int, quantity: int):
        """创建订单"""
        user = self.user_service.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        order = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "status": "pending"
        }
        return order

    def get_user_orders(self, user_id: int):
        """获取用户的所有订单"""
        return [{"id": 1, "user_id": user_id, "status": "completed"}]
