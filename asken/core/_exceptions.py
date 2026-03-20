from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._response import Response


class AskenError(Exception):
    def __init__(self, msg: str, status: int | None = None, res: "Response | None" = None):
        super().__init__(msg)
        self.status = status
        self.response = res


class AuthError(AskenError): ...
class NotFoundError(AskenError): ...
class RateLimitError(AskenError): ...
class ServerError(AskenError): ...
class TimeoutError(AskenError): ...
class ConnectionError(AskenError): ...
