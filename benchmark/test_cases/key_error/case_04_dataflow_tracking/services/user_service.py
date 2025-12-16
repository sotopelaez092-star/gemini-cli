from repositories.user_repository import UserRepository

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def get_user_details(self, user_id):
        """Get user details by ID."""
        user = self.repo.find_by_id(user_id)
        if user:
            return user.to_dict()
        return None

    def get_all_users(self):
        """Get all users."""
        users = self.repo.find_all()
        return [u.to_dict() for u in users]
