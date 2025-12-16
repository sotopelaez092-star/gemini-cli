import re

def validate_phone(phone):
    """Validate phone number format."""
    if not phone:
        return False
    cleaned = re.sub(r'[^\d]', '', phone)
    return len(cleaned) >= 10

def format_phone(phone):
    """Format phone number."""
    cleaned = re.sub(r'[^\d]', '', phone)
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    return phone
