from __future__ import annotations

import json as _json

from ._exceptions import AskenError, AuthError, NotFoundError, RateLimitError, ServerError


class Response:
    __slots__ = ("status", "data", "headers", "url", "_body")

    def __init__(self, status: int, headers: dict, body: bytes, url: str):
        self.status = status
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.url = url
        self._body = body
        self.data = self._parse()

    def _parse(self):
        if not self._body:
            return None
        ct = self.headers.get("content-type", "")
        return _json.loads(self._body) if "json" in ct else self._body.decode(errors="replace")

    def __repr__(self) -> str:
        return f"<Response [{self.status}] {self.url}>"

    def __bool__(self) -> bool:
        return 200 <= self.status < 300


def raise_for(res: Response) -> None:
    if bool(res):
        return
    msg = f"[{res.status}] {res.data or ''}"
    match res.status:
        case 401 | 403:     raise AuthError(msg, res.status, res)
        case 404:           raise NotFoundError(msg, res.status, res)
        case 429:           raise RateLimitError(msg, res.status, res)
        case s if s >= 500: raise ServerError(msg, res.status, res)
        case _:             raise AskenError(msg, res.status, res)
