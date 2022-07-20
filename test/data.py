from unittest import TestCase


class TestData(TestCase):
    def setUp(self) -> None:
        pass

    """
    TESTS TO ADD
    Instantiation.
    Closest, if we freeze IP.
    Greenest:
    -Bad region throws
    -No regions
    -Some good regions
    -Warning if single region can't lookup
    -Throws if all regions can't lookup.
    -Loud connection error if no internet, rate limit, bad/no key.
    """
