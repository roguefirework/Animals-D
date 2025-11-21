import re

def normalize(s: str) -> str:
    # Lowercase, collapse spaces, keep hyphens & apostrophes inside words
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s