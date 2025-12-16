# Case 03: Key renamed in config file
# Difficulty: Hard
# Configuration key was renamed in YAML/JSON config

from config_loader import load_app_config

def setup_logging():
    config = load_app_config()

    # Error: 'log_level' was renamed to 'logging.level' in config restructure
    level = config["log_level"]
    print(f"Setting log level to: {level}")

if __name__ == "__main__":
    setup_logging()
