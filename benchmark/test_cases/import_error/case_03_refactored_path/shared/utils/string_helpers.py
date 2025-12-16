import re

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def truncate(text, length, suffix='...'):
    """Truncate text to specified length."""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix

def capitalize_words(text):
    """Capitalize first letter of each word."""
    return ' '.join(word.capitalize() for word in text.split())
