"""用户服务"""
from models.user import User
from datetime import datetime

class UserService:
    def __init__(self):
        self.users = {}

    def create_user(self, user_id: int, username: str, email: str) -> User:
        """创建用户 - Bug: 缺少 role 参数，但 User 现在需要它"""
        user = User(
            id=user_id,
            username=username,
            email=email,
            created_at=datetime.now()
            # 缺少 role 参数
        )
        self.users[user_id] = user
        return user

    def get_user(self, user_id: int) -> User:
        return self.users.get(user_id)
