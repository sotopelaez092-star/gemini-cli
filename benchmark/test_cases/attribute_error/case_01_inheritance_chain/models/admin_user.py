from models.authenticated_user import AuthenticatedUser

class AdminUser(AuthenticatedUser):
    """Admin user with elevated privileges."""

    def __init__(self, username, email, role):
        super().__init__(username, email)
        self.role = role
        self._permissions.add("admin.access")
        self._permissions.add("admin.manage_users")

    def promote_user(self, user):
        """Promote a user to admin."""
        user.add_permission("admin.access")

    def get_admin_dashboard(self):
        """Get admin dashboard data."""
        return {"role": self.role, "permissions": self.get_permissions()}
