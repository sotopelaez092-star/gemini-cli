# Case 05: Calling instance method without instance
# Difficulty: Medium

from services.notification import NotificationService

def send_alerts():
    users = ["alice@example.com", "bob@example.com"]

    # Error: Calling instance method on class without creating instance
    # Should be: service = NotificationService(); service.send_bulk(...)
    NotificationService.send_bulk(users, "System Alert", "Maintenance scheduled")

if __name__ == "__main__":
    send_alerts()
