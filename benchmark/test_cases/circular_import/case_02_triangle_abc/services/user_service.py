# User Service - imports Audit Service
from services.audit_service import AuditService

class UserService:
    def __init__(self):
        self.audit = AuditService()

    def get_user(self, username):
        self.audit.log("get_user", username)
        return {"username": username, "password_hash": "abc123"}

    def create_user(self, username, email):
        self.audit.log("create_user", username)
        return {"username": username, "email": email}
