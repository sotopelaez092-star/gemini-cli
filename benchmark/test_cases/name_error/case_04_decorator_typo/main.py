# Case 04: Decorator name typo
# Difficulty: Hard

from decorators import time_it, cached, retry

class DataFetcher:
    def __init__(self):
        self.cache = {}

    @timit  # Error: should be @time_it
    @retry(max_attempts=3)
    def fetch_data(self, url):
        import time
        time.sleep(0.1)
        return {"url": url, "data": "sample"}

    @cached
    def get_config(self):
        return {"timeout": 30, "retries": 3}

if __name__ == "__main__":
    fetcher = DataFetcher()
    print(fetcher.fetch_data("http://example.com"))
