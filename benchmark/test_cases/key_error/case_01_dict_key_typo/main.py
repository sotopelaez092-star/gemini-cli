# Case 01: Dict key typo - simple case
# Difficulty: Easy

from config import get_database_config

def connect():
    config = get_database_config()
    # Error: 'hostname' should be 'host'
    host = config["hostname"]
    port = config["port"]
    return f"Connected to {host}:{port}"

if __name__ == "__main__":
    print(connect())
