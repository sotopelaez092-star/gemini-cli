# Bug: 这里导入 OrderService 造成循环依赖
from services.order_service import OrderService

class UserService:
    def __init__(self):
        self.order_service = OrderService()

    def get_user(self, user_id: int):
        """获取用户信息"""
        return {"id": user_id, "name": f"User_{user_id}", "email": f"user{user_id}@test.com"}

    def get_user_with_orders(self, user_id: int):
        """获取用户信息及其订单"""
        user = self.get_user(user_id)
        user["orders"] = self.order_service.get_user_orders(user_id)
        return user
