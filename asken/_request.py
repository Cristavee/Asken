from __future__ import annotations

import asyncio
import builtins
import http.client
import json as _json
import socket
import ssl
import urllib.parse

from ._exceptions import TimeoutError, ConnectionError
from ._response import Response

_SSL = ssl.create_default_context()


def _body(json, data) -> tuple[bytes | None, str | None]:
    if json is not None:
        return _json.dumps(json).encode(), "application/json"
    if data is not None:
        return urllib.parse.urlencode(data).encode(), "application/x-www-form-urlencoded"
    return None, None


def _do(method: str, url: str, headers: dict, params: dict | None, json, data, timeout: float) -> Response:
    p = urllib.parse.urlparse(url)
    path = p.path or "/"

    qp = {}
    if p.query:
        qp.update(urllib.parse.parse_qs(p.query, keep_blank_values=True))
    if params:
        qp.update({k: [str(v)] for k, v in params.items()})
    if qp:
        flat = {k: v[0] if len(v) == 1 else v for k, v in qp.items()}
        path += "?" + urllib.parse.urlencode(flat, doseq=True)

    body, ct = _body(json, data)
    hdrs = dict(headers)
    if ct:
        hdrs["Content-Type"] = ct
    if body:
        hdrs["Content-Length"] = str(len(body))

    https = p.scheme == "https"
    Conn = http.client.HTTPSConnection if https else http.client.HTTPConnection
    kw = {"context": _SSL} if https else {}

    try:
        conn = Conn(p.netloc, timeout=timeout, **kw)
        conn.request(method, path, body=body, headers=hdrs)
        r = conn.getresponse()
        res = Response(r.status, dict(r.getheaders()), r.read(), url)
        conn.close()
        return res
    except builtins.TimeoutError as e:
        raise TimeoutError(f"timed out after {timeout}s") from e
    except (socket.timeout, http.client.ResponseNotReady) as e:
        raise TimeoutError(str(e)) from e
    except (ConnectionRefusedError, socket.gaierror, OSError) as e:
        raise ConnectionError(str(e)) from e


async def send(method: str, url: str, headers: dict, params, json, data, timeout: float) -> Response:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _do(method, url, headers, params, json, data, timeout))
