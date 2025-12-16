# Case 01: ImportError - wrong module path
from services.user_service import UserService  # Wrong: should be services.users.user_service

def main():
    service = UserService()
    user = service.get_user(1)
    print(user)

if __name__ == "__main__":
    main()
