from __future__ import annotations


class BearerAuth:
    def __init__(self, token: str):
        self._t = token

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._t}"}


class ApiKeyAuth:
    def __init__(self, key: str, header: str = "X-API-Key"):
        self._k = key
        self._h = header

    def headers(self) -> dict[str, str]:
        return {self._h: self._k}


def resolve(token: str | None, api_key: str | None, api_key_header: str):
    if token:
        return BearerAuth(token)
    if api_key:
        return ApiKeyAuth(api_key, api_key_header)
    return None
