"""Config loader - v2.0

Breaking change: Flat config keys have been restructured into nested groups:
- log_level -> logging.level
- log_format -> logging.format
- db_host -> database.host
- db_port -> database.port
"""

def load_app_config():
    """Load application configuration (v2.0 structure)."""
    return {
        "app_name": "MyApplication",
        "version": "2.0.0",
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "handlers": ["console", "file"]
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp"
        },
        "cache": {
            "enabled": True,
            "ttl": 3600
        }
    }


def load_legacy_config():
    """Load legacy flat config (v1.0 structure - deprecated)."""
    return {
        "app_name": "MyApplication",
        "log_level": "INFO",
        "log_format": "%(message)s",
        "db_host": "localhost",
        "db_port": 5432
    }
