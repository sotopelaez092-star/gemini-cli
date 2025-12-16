# Application settings
# Note: Inconsistent naming convention (some UPPER_CASE, some PascalCase)

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "name": "myapp",
    "user": "admin"
}

# Legacy naming - should be API_TIMEOUT but kept for backwards compatibility
Api_Timeout = 30

# New naming convention
MAX_RETRIES = 3
MAX_CONNECTIONS = 10
DEBUG_MODE = False

# More legacy names
Cache_Ttl = 3600
Log_Level = "INFO"
