from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    role: str = "user"


class UserFactory:
    """Factory for creating User instances."""

    def __init__(self):
        self.default_role = "user"

    @classmethod
    def from_dict(cls, data):
        """Create User from dictionary (classmethod)."""
        return User(
            name=data.get("name", "Unknown"),
            email=data.get("email", ""),
            role=data.get("role", "user")
        )

    @classmethod
    def from_json(cls, json_str):
        """Create User from JSON string."""
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)

    @staticmethod
    def validate_email(email):
        """Validate email format."""
        return "@" in email and "." in email

    def create_default(self, name, email):
        """Instance method to create user with default role."""
        return User(name=name, email=email, role=self.default_role)
