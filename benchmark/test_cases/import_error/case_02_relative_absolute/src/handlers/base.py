class BaseHandler:
    """Base handler with common functionality."""

    def __init__(self):
        self.logger = None

    def format_response(self, data):
        return {"status": "success", "data": data}

    def format_error(self, message):
        return {"status": "error", "message": message}
