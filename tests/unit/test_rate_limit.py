import time
from apis.pc.base import BaseAPI


def test_rate_limiting():
    api = BaseAPI(rate_limit=0.1)
    start = time.time()
    api._sleep_if_needed()  # first call
    api._sleep_if_needed()  # second call should wait
    assert time.time() - start >= 0.1

