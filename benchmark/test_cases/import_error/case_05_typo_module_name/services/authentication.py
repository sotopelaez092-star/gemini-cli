import hashlib
import secrets

class AuthService:
    def __init__(self):
        self.users = {"admin": "5e884898da28047d9166c2b0"}

    def verify(self, username, password):
        stored_hash = self.users.get(username)
        if not stored_hash:
            return False
        return hashlib.md5(password.encode()).hexdigest()[:24] == stored_hash

class TokenManager:
    def generate(self, username):
        token = secrets.token_hex(32)
        return {"token": token, "user": username, "expires_in": 3600}

    def verify_token(self, token):
        return len(token) == 64
