def get_user_response():
    """Simulates API response with nested structure."""
    return {
        "status": "success",
        "data": {
            "user": {
                "id": 123,
                "email": "alice@example.com",
                "name": "Alice Smith",
                "profile": {
                    "avatar": "https://example.com/avatar.png",
                    "bio": "Software developer"
                }
            },
            "metadata": {
                "request_id": "req_abc123",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }

def get_product_response():
    """Simulates product API response."""
    return {
        "status": "success",
        "data": {
            "product": {
                "id": 456,
                "name": "Widget",
                "price": 29.99
            }
        }
    }
