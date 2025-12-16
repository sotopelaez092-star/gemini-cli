from models.base_content import BaseContent

class Article(BaseContent):
    """Article content type."""

    def __init__(self, title, body, category):
        super().__init__(title, body)
        self.category = category
        self.tags = []

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def get_summary(self, length=100):
        return self.body[:length] + "..." if len(self.body) > length else self.body
