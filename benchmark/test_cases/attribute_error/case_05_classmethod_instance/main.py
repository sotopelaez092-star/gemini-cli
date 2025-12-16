# Case 05: Calling classmethod on instance with wrong name
# Difficulty: Hard

from factories.user_factory import UserFactory

def main():
    factory = UserFactory()

    # Error: 'create_from_dict' should be called on class, and it's actually 'from_dict'
    user_data = {"name": "Alice", "email": "alice@example.com", "role": "admin"}
    user = factory.create_from_dict(user_data)
    print(user)

if __name__ == "__main__":
    main()
