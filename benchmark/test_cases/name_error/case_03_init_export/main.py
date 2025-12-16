# Case 03: Symbol exported from __init__.py with typo
# Difficulty: Medium

from validators import validata_email, validate_phone

def register_user(email, phone):
    # Error: 'validata_email' is typo, should be 'validate_email'
    if not validata_email(email):
        raise ValueError("Invalid email")
    if not validate_phone(phone):
        raise ValueError("Invalid phone")
    return {"email": email, "phone": phone, "status": "registered"}

if __name__ == "__main__":
    result = register_user("test@example.com", "1234567890")
    print(result)
