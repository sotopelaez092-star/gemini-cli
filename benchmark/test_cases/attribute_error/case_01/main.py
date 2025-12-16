# Case 01: AttributeError - typo in method name
from models.user import User

def main():
    user = User("Alice", "alice@example.com")
    # Typo: should be get_display_name()
    name = user.get_dispaly_name()
    print(f"User: {name}")

if __name__ == "__main__":
    main()
