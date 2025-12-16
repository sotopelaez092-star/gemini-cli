# Case 05: Environment variable key naming error
# Difficulty: Medium
# env var keys use different convention than expected

from env_loader import load_env_config

def get_api_credentials():
    config = load_env_config()

    # Error: Keys use different prefix - 'API_KEY' should be 'APP_API_KEY'
    api_key = config["API_KEY"]
    api_secret = config["API_SECRET"]
    return api_key, api_secret

if __name__ == "__main__":
    key, secret = get_api_credentials()
    print(f"API Key: {key[:8]}...")
