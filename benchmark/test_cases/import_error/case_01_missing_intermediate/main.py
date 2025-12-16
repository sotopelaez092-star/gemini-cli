# Case 01: Missing intermediate package in import path
# Difficulty: Medium

# Error: Missing 'v2' in the path
# Correct: from api.v2.endpoints.users import UserEndpoint
from api.endpoints.users import UserEndpoint

def main():
    endpoint = UserEndpoint()
    users = endpoint.list_users()
    print(users)

if __name__ == "__main__":
    main()
