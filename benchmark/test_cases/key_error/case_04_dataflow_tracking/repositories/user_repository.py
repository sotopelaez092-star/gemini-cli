from models.user import User

class UserRepository:
    def __init__(self):
        self._users = {
            1: User(1, "Alice", "Smith", "alice@example.com"),
            2: User(2, "Bob", "Jones", "bob@example.com")
        }

    def find_by_id(self, user_id):
        return self._users.get(user_id)

    def find_all(self):
        return list(self._users.values())

    def save(self, user):
        self._users[user.id] = user
