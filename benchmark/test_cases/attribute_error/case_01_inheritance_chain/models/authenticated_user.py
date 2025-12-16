from models.base_user import BaseUser

class AuthenticatedUser(BaseUser):
    """User that has been authenticated."""

    def __init__(self, username, email):
        super().__init__(username, email)
        self.is_authenticated = True
        self.session_token = None

    def set_session(self, token):
        self.session_token = token

    def logout(self):
        self.session_token = None
        self.is_authenticated = False
