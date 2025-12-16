"""Notification service for sending alerts."""

class NotificationService:
    def __init__(self, smtp_host="localhost", smtp_port=587):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sent_count = 0

    def send(self, recipient, subject, body):
        """Send single notification."""
        self.sent_count += 1
        return {"to": recipient, "subject": subject, "status": "sent"}

    def send_bulk(self, recipients, subject, body):
        """Send notification to multiple recipients."""
        results = []
        for recipient in recipients:
            result = self.send(recipient, subject, body)
            results.append(result)
        return results

    @classmethod
    def create_default(cls):
        """Factory method to create with default settings."""
        return cls()

    @staticmethod
    def validate_email(email):
        """Validate email format."""
        return "@" in email and "." in email.split("@")[1]
