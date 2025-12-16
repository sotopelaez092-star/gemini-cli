class User:
    """User model class."""

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def get_display_name(self):
        """Return formatted display name."""
        return f"{self.name} <{self.email}>"

    def get_email_domain(self):
        """Return email domain."""
        return self.email.split("@")[1]
