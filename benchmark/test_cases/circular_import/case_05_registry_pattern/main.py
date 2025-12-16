# Case 05: Circular import in registry/plugin pattern
# Difficulty: Hard
# Plugins register with registry, registry imports plugins

from plugins import registry

def main():
    registry.load_plugins()
    result = registry.execute("compress", data="hello world")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
