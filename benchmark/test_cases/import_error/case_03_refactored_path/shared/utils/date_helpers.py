from datetime import datetime

def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    """Format datetime object to string."""
    return dt.strftime(fmt)

def parse_datetime(text, fmt='%Y-%m-%d %H:%M:%S'):
    """Parse datetime string to object."""
    return datetime.strptime(text, fmt)
