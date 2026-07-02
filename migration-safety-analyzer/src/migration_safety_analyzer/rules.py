DESTRUCTIVE_KEYWORDS = {'DROP', 'TRUNCATE'}

def is_destructive(stmt):
    return any(kw in str(stmt).upper() for kw in DESTRUCTIVE_KEYWORDS)