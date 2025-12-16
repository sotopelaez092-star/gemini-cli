import json
from datetime import datetime

class SerializableMixin:
    """Mixin that adds serialization capabilities."""

    def to_json(self):
        """Convert object to JSON string."""
        data = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = value
        return json.dumps(data)

    def to_dict(self):
        """Convert object to dictionary."""
        return json.loads(self.to_json())


class TimestampMixin:
    """Mixin that adds timestamp tracking."""

    def __init__(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def touch(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()


class ValidatableMixin:
    """Mixin that adds validation capabilities."""

    def validate(self):
        """Override in subclass to add validation logic."""
        return True

    def is_valid(self):
        """Check if object is valid."""
        return self.validate()
