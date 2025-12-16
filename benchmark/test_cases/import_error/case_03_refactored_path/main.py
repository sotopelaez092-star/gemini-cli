# Case 03: Module path changed after refactoring
# Difficulty: Hard
# The utils module was moved to shared/utils but old import path still used

from utils.string_helpers import slugify, truncate
from utils.date_helpers import format_datetime

def process_title(title):
    slug = slugify(title)
    short = truncate(title, 50)
    return {"slug": slug, "short_title": short}

if __name__ == "__main__":
    print(process_title("Hello World Article Title"))
