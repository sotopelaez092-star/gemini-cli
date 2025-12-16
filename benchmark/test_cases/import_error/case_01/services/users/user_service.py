class UserService:
    """Service for user operations."""

    def __init__(self):
        self.users = {
            1: {"id": 1, "name": "Alice"},
            2: {"id": 2, "name": "Bob"},
        }

    def get_user(self, user_id):
        return self.users.get(user_id)

    def create_user(self, name):
        new_id = max(self.users.keys()) + 1
        self.users[new_id] = {"id": new_id, "name": name}
        return self.users[new_id]
