from __future__ import annotations

from .core._client import Asken
from .core._sync import SyncAsken
from .core._response import Response
from .core._auth import BearerAuth, ApiKeyAuth
from .core._exceptions import (
    AskenError,
    AuthError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ConnectionError,
)

__version__ = "1.1.0"
__all__ = [
    "create", "sync",
    "get", "post", "put", "patch", "delete", "head", "options", "stream",
    "Asken", "SyncAsken",
    "Response",
    "BearerAuth", "ApiKeyAuth",
    "AskenError", "AuthError", "NotFoundError",
    "RateLimitError", "ServerError", "TimeoutError", "ConnectionError",
]


def create(
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
) -> Asken:
    return Asken(
        base_url=base_url, token=token, api_key=api_key,
        api_key_header=api_key_header, headers=headers,
        timeout=timeout, retries=retries,
        retry_min=retry_min, retry_max=retry_max,
        verify=verify, cookies=cookies,
    )


class _Sync:
    def create(
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
    ) -> SyncAsken:
        return SyncAsken(
            base_url=base_url, token=token, api_key=api_key,
            api_key_header=api_key_header, headers=headers,
            timeout=timeout, retries=retries,
            retry_min=retry_min, retry_max=retry_max,
            verify=verify,
        )

    def get(self, url, *, params=None, **kw) -> Response:
        return SyncAsken().get(url, params=params, **kw)

    def post(self, url, *, json=None, data=None, files=None, **kw) -> Response:
        return SyncAsken().post(url, json=json, data=data, files=files, **kw)

    def put(self, url, *, json=None, **kw) -> Response:
        return SyncAsken().put(url, json=json, **kw)

    def patch(self, url, *, json=None, **kw) -> Response:
        return SyncAsken().patch(url, json=json, **kw)

    def delete(self, url, **kw) -> Response:
        return SyncAsken().delete(url, **kw)

    def head(self, url, *, params=None, **kw) -> Response:
        return SyncAsken().head(url, params=params, **kw)

    def options(self, url, **kw) -> Response:
        return SyncAsken().options(url, **kw)


sync = _Sync()

_default = Asken()


async def get(url, *, params=None, **kw) -> Response:
    return await _default.get(url, params=params, **kw)

async def post(url, *, json=None, data=None, files=None, **kw) -> Response:
    return await _default.post(url, json=json, data=data, files=files, **kw)

async def put(url, *, json=None, **kw) -> Response:
    return await _default.put(url, json=json, **kw)

async def patch(url, *, json=None, **kw) -> Response:
    return await _default.patch(url, json=json, **kw)

async def delete(url, **kw) -> Response:
    return await _default.delete(url, **kw)

async def head(url, *, params=None, **kw) -> Response:
    return await _default.head(url, params=params, **kw)

async def options(url, **kw) -> Response:
    return await _default.options(url, **kw)

async def stream(method, url, *, params=None, json=None, data=None, cookies=None, chunk_size=8192):
    async for chunk in _default.stream(method, url, params=params, json=json, data=data, cookies=cookies, chunk_size=chunk_size):
        yield chunk
