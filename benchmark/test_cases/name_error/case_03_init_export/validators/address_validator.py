def validate_address(address):
    """Validate address has required fields."""
    required = ['street', 'city', 'zip']
    if not isinstance(address, dict):
        return False
    return all(field in address for field in required)
