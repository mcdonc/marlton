def sort_byint(keys):
    """Sort a list of integer id keys in reverse order"""
    keys = list(keys)
    def byint(a, b):
        try:
            return cmp(int(a), int(b))
        except TypeError:
            return cmp(a, b)
    keys.sort(byint)
    keys.reverse()
    return keys

