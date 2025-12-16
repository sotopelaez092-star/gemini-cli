class User:
    def __init__(self, id, first_name, last_name, email):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "full_name": self.full_name,  # Note: 'full_name', not 'name'
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email
        }
