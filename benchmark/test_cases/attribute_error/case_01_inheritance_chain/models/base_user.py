class BaseUser:
    """Base user class with common functionality."""

    def __init__(self, username, email):
        self.username = username
        self.email = email
        self._permissions = set()

    def get_permissions(self):
        """Get user permissions."""
        return list(self._permissions)

    def add_permission(self, permission):
        """Add a permission."""
        self._permissions.add(permission)

    def has_permission(self, permission):
        """Check if user has permission."""
        return permission in self._permissions

    def get_display_name(self):
        """Get display name."""
        return self.username
