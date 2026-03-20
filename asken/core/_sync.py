from __future__ import annotations

from . import _auth as auth_mod
from . import _retry as retry_mod
from ._request import _do
from ._response import Response, raise_for
from ._exceptions import ServerError, RateLimitError, TimeoutError, ConnectionError
import time
import logging

_log = logging.getLogger("asken")
_RETRYABLE = (ServerError, RateLimitError, TimeoutError, ConnectionError)


def _run_with_retry(fn, retries, mn, mx):
    attempt = 0
    while True:
        try:
            return fn()
        except _RETRYABLE as e:
            attempt += 1
            if attempt >= retries:
                raise
            wait = min(mn * (2 ** (attempt - 1)), mx)
            _log.warning("asken retry %d/%d in %.1fs — %s", attempt, retries, wait, e)
            time.sleep(wait)


class SyncAsken:
    def __init__(
        self,
        base_url: str = "",
        *,
        token: str | None = None,
        api_key: str | None = None,
        api_key_header: str = "X-API-Key",
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        retries: int = 3,
        retry_min: float = 1.0,
        retry_max: float = 8.0,
        verify: bool = True,
    ):
        self._base = base_url.rstrip("/")
        self._auth = auth_mod.resolve(token, api_key, api_key_header)
        self._timeout = timeout
        self._retries = retries
        self._rmin = retry_min
        self._rmax = retry_max
        self._verify = verify
        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "asken/1.0",
            **(headers or {}),
        }

    def _hdrs(self) -> dict:
        h = dict(self._headers)
        if self._auth:
            h.update(self._auth.headers())
        return h

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return self._base + "/" + path.lstrip("/")

    def _send(self, method, url, params=None, json=None, data=None, files=None, cookies=None, verify=None) -> Response:
        v = self._verify if verify is None else verify

        def _do_req():
            res = _do(method, self._url(url), self._hdrs(), params, json, data, files, cookies, self._timeout, v)
            raise_for(res)
            return res

        return _run_with_retry(_do_req, self._retries, self._rmin, self._rmax)

    def get(self, url, *, params=None, cookies=None, verify=None, **kw) -> Response:
        return self._send("GET", url, params=params, cookies=cookies, verify=verify)

    def post(self, url, *, json=None, data=None, files=None, cookies=None, verify=None, **kw) -> Response:
        return self._send("POST", url, json=json, data=data, files=files, cookies=cookies, verify=verify)

    def put(self, url, *, json=None, cookies=None, verify=None, **kw) -> Response:
        return self._send("PUT", url, json=json, cookies=cookies, verify=verify)

    def patch(self, url, *, json=None, cookies=None, verify=None, **kw) -> Response:
        return self._send("PATCH", url, json=json, cookies=cookies, verify=verify)

    def delete(self, url, *, cookies=None, verify=None, **kw) -> Response:
        return self._send("DELETE", url, cookies=cookies, verify=verify)

    def head(self, url, *, params=None, cookies=None, verify=None, **kw) -> Response:
        return self._send("HEAD", url, params=params, cookies=cookies, verify=verify)

    def options(self, url, *, cookies=None, verify=None, **kw) -> Response:
        return self._send("OPTIONS", url, cookies=cookies, verify=verify)

    def __enter__(self) -> SyncAsken:
        return self

    def __exit__(self, *_):
        pass
