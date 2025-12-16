# Data processing module
DEFAULT_MULTIPLIER = 1.5
MAX_RECORDS = 1000

def process_records(records, multiplier=DEFAULT_MULTIPLIER):
    """Process records with a multiplier."""
    return [{"id": r["id"], "value": r["value"] * multiplier} for r in records]

def filter_records(records, min_value=0):
    """Filter records by minimum value."""
    return [r for r in records if r["value"] >= min_value]
