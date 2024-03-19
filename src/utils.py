import re
from time import sleep
from typing import Optional, Any, Callable


def wait_until(  # type: ignore
    condition: Callable[..., bool],
    timeout_seconds: int,
    wait_interval_seconds: int = 5,
    *args,
    **kwargs,
) -> None:
    waited_for_seconds = 0
    while not condition(*args, **kwargs):
        if waited_for_seconds >= timeout_seconds:
            raise TimeoutError(
                f"Timeout exceeded waiting for condition: {condition.__code__}"
            )
        sleep(wait_interval_seconds)
        waited_for_seconds += wait_interval_seconds


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


def to_g(spec: str) -> float:
    """Convert a value in G, M, Mi or Gi into G."""
    match = re.match(r"([0-9]+)([a-z]+)", spec, re.I)
    if match:
        value, unit = match.groups()
    else:
        raise ValueError("Value wrongly formatted.")
    if unit == "G":
        g = float(value)
    if unit == "M":
        g = float(value) / 1000
    if unit == "Mi":
        g = float(value) * 0.001048576
    if unit == "Gi":
        g = float(value) * 0.931323
    return g
