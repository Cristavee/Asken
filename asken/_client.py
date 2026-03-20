from __future__ import annotations

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
    ):
        self._base = base_url.rstrip("/")
        self._auth = auth_mod.resolve(token, api_key, api_key_header)
        self._timeout = timeout
        self._retries = retries
        self._rmin = retry_min
        self._rmax = retry_max
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

    async def _send(self, method: str, url: str, **kw) -> Response:
        async def _do():
            res = await req_mod.send(
                method,
                self._url(url),
                self._hdrs(),
                kw.get("params"),
                kw.get("json"),
                kw.get("data"),
                self._timeout,
            )
            raise_for(res)
            return res

        return await retry_mod.run(_do, self._retries, self._rmin, self._rmax)

    async def get(self, url: str, *, params: dict | None = None, **kw) -> Response:
        return await self._send("GET", url, params=params, **kw)

    async def post(self, url: str, *, json=None, data: dict | None = None, **kw) -> Response:
        return await self._send("POST", url, json=json, data=data, **kw)

    async def put(self, url: str, *, json=None, **kw) -> Response:
        return await self._send("PUT", url, json=json, **kw)

    async def patch(self, url: str, *, json=None, **kw) -> Response:
        return await self._send("PATCH", url, json=json, **kw)

    async def delete(self, url: str, **kw) -> Response:
        return await self._send("DELETE", url, **kw)

    async def __aenter__(self) -> Asken:
        return self

    async def __aexit__(self, *_):
        pass
