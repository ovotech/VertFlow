from typing import Optional, Any


def intersection_equal(a: Optional[Any], b: Optional[Any]) -> bool:
    """
    Determines mutual items (dictionary keys or list indices) in two iterables.
    Returns True if the values of those mutual items are equal.
    Recursively crawls through any nested iterables.
    If non-iterables are provided, a simple equality check is run on them both.
    :param a: A dictionary, list or non-iterable Any-type.
    :param b: A dictionary, list or non-iterable Any-type.
    :return: True, if the values of all mutual items are equal.
    """

    # Shortcuts
    if a == b:  # Either both None or both not-None and identical.
        return True
    if not a or not b:  # Exactly one is None.
        return False
    if not (type(a) == type(b) == dict) and not (type(a) == type(b) == list):
        return bool(a == b)

    equal = True

    for x in a:
        if x in b:
            if isinstance(a[x], dict) and isinstance(b[x], dict):
                equal = equal and intersection_equal(a[x], b[x])
            elif isinstance(a[x], list) and isinstance(b[x], list):
                k = 0
                for v in a[x]:
                    equal = equal and intersection_equal(a[x][k], b[x][k])
                    k += 1
            else:
                equal = equal and intersection_equal(a[x], b[x])
    return equal
