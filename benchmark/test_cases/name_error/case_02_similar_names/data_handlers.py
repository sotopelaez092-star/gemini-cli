from datetime import datetime
from utils.date_utils import parse_date, format_date

class DataProcessor:
    """Handles data processing operations."""

    def __init__(self):
        self.processed_count = 0

    def process_data(self, raw_data):
        """Process raw data and return structured result."""
        self.processed_count += 1
        return {
            "processed": True,
            "timestamp": datetime.now().isoformat(),
            "data": raw_data.get("values", []),
            "date_parsed": parse_date(raw_data.get("date", ""))
        }

    def validate_data(self, data):
        """Validate data structure."""
        required_keys = ["date", "values"]
        return all(key in data for key in required_keys)

    def transform_data(self, data, multiplier=1):
        """Transform data values."""
        values = data.get("values", [])
        return [v * multiplier for v in values]
