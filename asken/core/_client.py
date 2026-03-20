from __future__ import annotations

from collections.abc import AsyncIterator

from . import _auth as auth_mod
from . import _retry as retry_mod
from . import _request as req_mod
from ._response import Response, raise_for


class Asken:
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
        cookies: dict | None = None,
    ):
        self._base = base_url.rstrip("/")
        self._auth = auth_mod.resolve(token, api_key, api_key_header)
        self._timeout = timeout
        self._retries = retries
        self._rmin = retry_min
        self._rmax = retry_max
        self._verify = verify
        self._cookies = cookies or {}
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

    def _merged_cookies(self, cookies: dict | None) -> dict:
        return {**self._cookies, **(cookies or {})}

    async def _send(self, method, url, params=None, json=None, data=None, files=None, cookies=None, verify=None) -> Response:
        v = self._verify if verify is None else verify
        ck = self._merged_cookies(cookies)

        async def _do():
            res = await req_mod.send(method, self._url(url), self._hdrs(), params, json, data, files, ck, self._timeout, v)
            raise_for(res)
            return res

        return await retry_mod.run(_do, self._retries, self._rmin, self._rmax)

    async def get(self, url, *, params=None, cookies=None, verify=None, **kw) -> Response:
        return await self._send("GET", url, params=params, cookies=cookies, verify=verify)

    async def post(self, url, *, json=None, data=None, files=None, cookies=None, verify=None, **kw) -> Response:
        return await self._send("POST", url, json=json, data=data, files=files, cookies=cookies, verify=verify)

    async def put(self, url, *, json=None, cookies=None, verify=None, **kw) -> Response:
        return await self._send("PUT", url, json=json, cookies=cookies, verify=verify)

    async def patch(self, url, *, json=None, cookies=None, verify=None, **kw) -> Response:
        return await self._send("PATCH", url, json=json, cookies=cookies, verify=verify)

    async def delete(self, url, *, cookies=None, verify=None, **kw) -> Response:
        return await self._send("DELETE", url, cookies=cookies, verify=verify)

    async def head(self, url, *, params=None, cookies=None, verify=None, **kw) -> Response:
        return await self._send("HEAD", url, params=params, cookies=cookies, verify=verify)

    async def options(self, url, *, cookies=None, verify=None, **kw) -> Response:
        return await self._send("OPTIONS", url, cookies=cookies, verify=verify)

    async def stream(self, method: str, url: str, *, params=None, json=None, data=None, cookies=None, verify=None, chunk_size=8192) -> AsyncIterator[bytes]:
        v = self._verify if verify is None else verify
        ck = self._merged_cookies(cookies)
        async for chunk in req_mod.stream(method, self._url(url), self._hdrs(), params, json, data, ck, self._timeout, v, chunk_size):
            yield chunk

    async def __aenter__(self) -> Asken:
        return self

    async def __aexit__(self, *_):
        pass
