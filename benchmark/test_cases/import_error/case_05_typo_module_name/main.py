# Case 05: Typo in module name
# Difficulty: Easy

# Error: 'authentification' is French spelling, should be 'authentication'
from services.authentification import AuthService, TokenManager

def login(username, password):
    auth = AuthService()
    if auth.verify(username, password):
        token_mgr = TokenManager()
        return token_mgr.generate(username)
    return None

if __name__ == "__main__":
    print(login("admin", "password123"))
