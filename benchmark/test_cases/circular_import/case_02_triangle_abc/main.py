# Case 02: Three-way circular import A -> B -> C -> A
# Difficulty: Hard

from services.auth_service import AuthService

def main():
    auth = AuthService()
    user = auth.authenticate("admin", "password")
    print(f"Authenticated: {user}")

if __name__ == "__main__":
    main()
