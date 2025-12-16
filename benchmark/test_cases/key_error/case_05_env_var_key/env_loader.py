"""Environment configuration loader.

All environment variables are prefixed with APP_ for namespacing.
"""

import os

def load_env_config():
    """Load configuration from environment variables.

    All keys are prefixed with APP_ to avoid conflicts with system variables.

    Expected environment variables:
    - APP_API_KEY: API key for external service
    - APP_API_SECRET: API secret
    - APP_DATABASE_URL: Database connection string
    - APP_DEBUG: Debug mode flag
    """
    # In real code, this would read from os.environ
    # Simulating environment variables here
    return {
        "APP_API_KEY": "sk_live_abc123xyz",
        "APP_API_SECRET": "secret_456def",
        "APP_DATABASE_URL": "postgresql://localhost:5432/myapp",
        "APP_DEBUG": "false",
        "APP_LOG_LEVEL": "INFO"
    }


def get_env(key, default=None):
    """Get single environment variable with APP_ prefix."""
    config = load_env_config()
    return config.get(f"APP_{key}", default)
