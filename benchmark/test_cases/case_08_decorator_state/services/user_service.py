"""用户服务"""
from core.registry import service, ServiceRegistry

@service("user")
class UserService:
    """
    用户服务

    Bug: 在 __init__ 中依赖 logger 服务
    但由于装饰器执行顺序问题，logger 可能还没注册
    """
    def __init__(self):
        registry = ServiceRegistry()
        # Bug: 尝试获取 logger 服务，但可能还没注册
        self.logger = registry.get("logger")
        if self.logger is None:
            raise RuntimeError("Logger service not found! Service dependency issue.")

    def create_user(self, username: str) -> dict:
        """创建用户"""
        user = {"id": 1, "username": username}
        self.logger.log(f"Created user: {username}")
        return user

    def get_user(self, user_id: int) -> dict:
        """获取用户"""
        self.logger.log(f"Getting user: {user_id}")
        return {"id": user_id, "username": f"user_{user_id}"}
