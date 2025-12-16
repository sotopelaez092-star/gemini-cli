from models.mixins import SerializableMixin, TimestampMixin

class BaseContent(SerializableMixin, TimestampMixin):
    """Base class for all content types."""

    def __init__(self, title, body):
        TimestampMixin.__init__(self)
        self.title = title
        self.body = body
        self.status = "draft"

    def publish(self):
        self.status = "published"
        self.touch()

    def archive(self):
        self.status = "archived"
        self.touch()
