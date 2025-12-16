# Case 02: Keyword argument renamed
# Difficulty: Hard
# Keyword argument was renamed in a refactoring

from http_client import HttpClient

def fetch_user_data(user_id):
    client = HttpClient(base_url="https://api.example.com")

    # Error: 'timeout_seconds' was renamed to 'timeout' in new version
    response = client.get(f"/users/{user_id}", timeout_seconds=30, retries=3)
    return response

if __name__ == "__main__":
    print(fetch_user_data(123))
