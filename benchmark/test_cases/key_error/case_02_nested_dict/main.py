# Case 02: Nested dict key error
# Difficulty: Medium
# Key exists at wrong nesting level

from api_response import get_user_response

def process_user():
    response = get_user_response()

    # Error: 'email' is nested under 'data.user', not directly under 'data'
    user_email = response["data"]["email"]
    print(f"User email: {user_email}")

if __name__ == "__main__":
    process_user()
