# Case 02: Relative vs Absolute import confusion
# Difficulty: Hard

# Error: Using relative import syntax but missing the dot
# Should be: from .base import BaseHandler or from src.handlers.base import BaseHandler
from base import BaseHandler
from src.models.user import User

class UserHandler(BaseHandler):
    def handle(self, request):
        user_id = request.get("user_id")
        user = User(user_id, "test@example.com")
        return self.format_response(user.to_dict())

if __name__ == "__main__":
    handler = UserHandler()
    print(handler.handle({"user_id": 1}))
