class MetricsProcessor:
    """Core metrics processing engine."""

    def __init__(self):
        self.precision = 2

    def calculate(self, data):
        """Calculate metrics from data."""
        if not data:
            return {}
        return {
            "sum": sum(data),
            "avg": round(sum(data) / len(data), self.precision),
            "min": min(data),
            "max": max(data),
            "count": len(data)
        }

    def normalize(self, data):
        """Normalize data to 0-1 range."""
        if not data:
            return []
        min_val, max_val = min(data), max(data)
        if max_val == min_val:
            return [0.5] * len(data)
        return [(x - min_val) / (max_val - min_val) for x in data]
