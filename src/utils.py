from typing import Optional


def intersection_equal(dict_a: Optional[dict], dict_b: Optional[dict]) -> bool:
    """
    Determines mutual keys between two dictionaries.
    Returns True if the values of those mutual keys are equal.
    Recursively crawls through any nested dictionaries and lists of dictionaries.
    :param dict_a: A dictionary, potentially containing nested (lists of) dictionaries.
    :param dict_b: A dictionary, potentially containing nested (lists of) dictionaries.
    :return: True, if the values of all mututal keys in the dictionary tree are equal.
    """

    # Shortcut
    if dict_a == dict_b:  # Either both None or both not-None and identical.
        return True

    if not dict_a or not dict_b:  # Exactly one is None.
        return False

    equal = True
    for x in dict_a:
        if x in dict_b:
            if isinstance(dict_a[x], dict) and isinstance(dict_b[x], dict):
                equal = equal and intersection_equal(dict_a[x], dict_b[x])
            elif isinstance(dict_a[x], list) and isinstance(dict_b[x], list):
                k = 0
                for v in dict_a[x]:
                    equal = equal and intersection_equal(
                        dict_a[x][k], dict_b[x][k]
                    )  # This will only work if both of them are lists of dicts of equal length. Need to genercise to work with any lists of arbitary length with any inner type.
                    k += 1
            else:
                equal = equal and dict_a[x] == dict_b[x]
    return equal
