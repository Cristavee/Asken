from __future__ import annotations

import asyncio
import logging

from ._exceptions import ServerError, RateLimitError, TimeoutError, ConnectionError

_log = logging.getLogger("asken")
_RETRYABLE = (ServerError, RateLimitError, TimeoutError, ConnectionError)


async def run(fn, retries: int, mn: float, mx: float):
    attempt = 0
    while True:
        try:
            return await fn()
        except _RETRYABLE as e:
            attempt += 1
            if attempt >= retries:
                raise
            wait = min(mn * (2 ** (attempt - 1)), mx)
            _log.warning("asken retry %d/%d in %.1fs — %s", attempt, retries, wait, e)
            await asyncio.sleep(wait)
