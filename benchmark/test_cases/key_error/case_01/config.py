def get_database_config():
    """Return database configuration."""
    return {
        "host": "localhost",
        "port": 5432,
        "database": "myapp",
        "user": "admin",
        "password": "secret"
    }

def get_cache_config():
    """Return cache configuration."""
    return {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }
