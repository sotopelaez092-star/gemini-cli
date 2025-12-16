# Case 01: KeyError - wrong dictionary key
from config import get_database_config

def connect_to_database():
    config = get_database_config()
    # KeyError: 'hostname' - should be 'host'
    host = config["hostname"]
    port = config["port"]
    print(f"Connecting to {host}:{port}")

if __name__ == "__main__":
    connect_to_database()
