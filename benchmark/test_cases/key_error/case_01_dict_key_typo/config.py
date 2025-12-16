def get_database_config():
    return {
        "host": "localhost",
        "port": 5432,
        "database": "myapp",
        "user": "admin",
        "password": "secret"
    }

def get_cache_config():
    return {
        "host": "localhost",
        "port": 6379
    }
