import functools

def cached(func):
    """Simple cache decorator."""
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

def lru_cached(maxsize=128):
    """LRU cache decorator with configurable size."""
    def decorator(func):
        return functools.lru_cache(maxsize=maxsize)(func)
    return decorator
