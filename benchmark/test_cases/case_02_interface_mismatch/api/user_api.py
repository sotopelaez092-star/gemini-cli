"""用户 API"""
from services.user_service import UserService
from models.user import User

class UserAPI:
    def __init__(self):
        self.user_service = UserService()

    def register_user(self, data: dict) -> dict:
        """注册用户 - Bug: 调用 create_user 时参数不匹配"""
        user = self.user_service.create_user(
            user_id=data["id"],
            username=data["username"],
            email=data["email"],
            # Bug: 传了 role 但 create_user 不接受这个参数
            role=data.get("role", "user")
        )
        return {"status": "success", "user_id": user.id}

    def get_user_info(self, user_id: int) -> dict:
        user = self.user_service.get_user(user_id)
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        return {"error": "User not found"}
