# Audit Service - imports Auth Service (creates cycle!)
from services.auth_service import AuthService

class AuditService:
    def __init__(self):
        self.auth = AuthService()  # Needs auth to get current user

    def log(self, action, target):
        # Try to get current authenticated user
        print(f"Audit: {action} on {target}")

    def get_audit_trail(self, username):
        return [{"action": "login", "timestamp": "2024-01-15"}]
