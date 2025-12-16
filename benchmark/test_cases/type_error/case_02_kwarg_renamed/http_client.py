"""HTTP Client - v3.0

Breaking changes from v2.0:
- Renamed 'timeout_seconds' to 'timeout' for consistency
- Renamed 'max_retries' to 'retries'
- Added 'verify_ssl' parameter
"""

class HttpClient:
    def __init__(self, base_url, default_timeout=30):
        self.base_url = base_url
        self.default_timeout = default_timeout

    def get(self, path, timeout=None, retries=1, verify_ssl=True, headers=None):
        """Make GET request.

        Args:
            path: URL path to request
            timeout: Request timeout in seconds (default: instance default)
            retries: Number of retry attempts (default: 1)
            verify_ssl: Whether to verify SSL certificates (default: True)
            headers: Optional request headers

        Returns:
            Response data
        """
        actual_timeout = timeout or self.default_timeout
        url = f"{self.base_url}{path}"

        # Simulate request
        return {
            "url": url,
            "timeout": actual_timeout,
            "retries": retries,
            "status": 200,
            "data": {"id": 123, "name": "Test User"}
        }

    def post(self, path, data, timeout=None, retries=1):
        """Make POST request."""
        return {"status": 201, "data": data}

    def put(self, path, data, timeout=None):
        """Make PUT request."""
        return {"status": 200, "data": data}
