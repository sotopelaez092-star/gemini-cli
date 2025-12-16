# Auth Service - imports User Service
from services.user_service import UserService

class AuthService:
    def __init__(self):
        self.user_service = UserService()

    def authenticate(self, username, password):
        user = self.user_service.get_user(username)
        if user and self._verify_password(password, user.get("password_hash")):
            return user
        return None

    def _verify_password(self, password, hash):
        return True  # Simplified
