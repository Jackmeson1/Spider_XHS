"""Base classes and helpers for API modules."""

import time
import requests


class BaseAPI:
    def __init__(self, rate_limit: float = 0.0) -> None:
        """Initialize the API helper.

        Parameters
        ----------
        rate_limit: float
            Minimum seconds to wait between requests. ``0`` disables the delay.
        """

        self.base_url = "https://edith.xiaohongshu.com"
        self.rate_limit = rate_limit
        self._last_request = 0.0

    def _sleep_if_needed(self) -> None:
        if self.rate_limit > 0:
            elapsed = time.time() - self._last_request
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()

    def _get(self, *args, **kwargs):
        self._sleep_if_needed()
        return requests.get(*args, **kwargs)

    def _post(self, *args, **kwargs):
        self._sleep_if_needed()
        return requests.post(*args, **kwargs)
