# Case 04: Key error requiring data flow tracking
# Difficulty: Hard
# Need to trace where the dict comes from to understand the correct keys

from services.user_service import UserService

def display_user_info(user_id):
    service = UserService()
    user_data = service.get_user_details(user_id)

    # Error: Key should be 'full_name' not 'name'
    # Need to trace through UserService -> UserRepository -> User model
    print(f"User: {user_data['name']}")
    print(f"Email: {user_data['email']}")

if __name__ == "__main__":
    display_user_info(1)
