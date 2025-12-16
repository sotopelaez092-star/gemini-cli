class UserEndpoint:
    """User API endpoint."""

    def list_users(self):
        return [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]

    def get_user(self, user_id):
        users = {1: "Alice", 2: "Bob"}
        return users.get(user_id)

    def create_user(self, name):
        return {"id": 3, "name": name, "status": "created"}
