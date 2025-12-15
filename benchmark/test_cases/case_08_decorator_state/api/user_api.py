"""用户 API"""
from core.registry import ServiceRegistry

class UserAPI:
    def __init__(self):
        registry = ServiceRegistry()
        self.user_service = registry.get("user")
        self.logger = registry.get("logger")

    def register_user(self, data: dict) -> dict:
        """注册用户"""
        if not self.user_service:
            raise RuntimeError("User service not available")

        user = self.user_service.create_user(data["username"])
        return {"status": "success", "user": user}

    def get_user_info(self, user_id: int) -> dict:
        """获取用户信息"""
        if not self.user_service:
            raise RuntimeError("User service not available")

        return self.user_service.get_user(user_id)
