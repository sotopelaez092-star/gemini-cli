# Case 05: Constant name case error
# Difficulty: Medium

from config.settings import DATABASE_CONFIG, Api_Timeout, MAX_RETRIES

def connect_database():
    host = DATABASE_CONFIG["host"]
    port = DATABASE_CONFIG["port"]
    # Error: 'API_TIMEOUT' should be 'Api_Timeout' (inconsistent naming in codebase)
    timeout = API_TIMEOUT
    retries = MAX_RETRIES

    print(f"Connecting to {host}:{port} with timeout={timeout}, retries={retries}")
    return True

if __name__ == "__main__":
    connect_database()
