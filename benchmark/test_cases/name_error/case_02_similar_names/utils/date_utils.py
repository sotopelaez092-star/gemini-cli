from datetime import datetime

def parse_date(date_string):
    """Parse date string to datetime object."""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        return None

def format_date(dt, fmt="%Y-%m-%d"):
    """Format datetime to string."""
    if not dt:
        return ""
    return dt.strftime(fmt)

def get_date_range(start, end):
    """Get list of dates between start and end."""
    # Implementation
    pass
