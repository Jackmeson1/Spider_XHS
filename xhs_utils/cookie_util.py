"""Utility helpers for cookie handling."""


def trans_cookies(cookies_str: str) -> dict:
    """Translate a cookie string into a dictionary.

    Empty values return an empty dict instead of ``{"": ""}``.
    ``cookies_str`` may use either ``;`` or ``; `` as separators.
    """

    cookies_str = cookies_str.strip()
    if not cookies_str:
        return {}

    separator = "; " if "; " in cookies_str else ";"
    ck = {}
    for item in cookies_str.split(separator):
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        ck[key] = value
    return ck
