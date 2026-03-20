from __future__ import annotations

import asyncio
import builtins
import http.client
import json as _json
import socket
import ssl
import urllib.parse
from collections.abc import AsyncIterator

from ._exceptions import TimeoutError, ConnectionError
from ._multipart import build as build_multipart
from ._response import Response

_SSL = ssl.create_default_context()


def _make_conn(host: str, https: bool, timeout: float, verify: bool):
    if https:
        ctx = _SSL if verify else ssl._create_unverified_context()
        return http.client.HTTPSConnection(host, timeout=timeout, context=ctx)
    return http.client.HTTPConnection(host, timeout=timeout)


def _cookie_header(cookies: dict) -> str:
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def _build_body(json, data, files):
    if files is not None:
        body, ct = build_multipart(files, data)
        return body, ct
    if json is not None:
        return _json.dumps(json).encode(), "application/json"
    if data is not None:
        return urllib.parse.urlencode(data).encode(), "application/x-www-form-urlencoded"
    return None, None


def _prep(method, url, headers, params, json, data, files, cookies, verify):
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

    body, ct = _build_body(json, data, files)
    hdrs = dict(headers)
    if ct:
        hdrs["Content-Type"] = ct
    if body:
        hdrs["Content-Length"] = str(len(body))
    if cookies:
        hdrs["Cookie"] = _cookie_header(cookies)

    https = p.scheme == "https"
    return p.netloc, path, hdrs, body, https


def _do(method, url, headers, params, json, data, files, cookies, timeout, verify) -> Response:
    host, path, hdrs, body, https = _prep(method, url, headers, params, json, data, files, cookies, verify)
    try:
        conn = _make_conn(host, https, timeout, verify)
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


def _do_stream(method, url, headers, params, json, data, cookies, timeout, verify, chunk_size):
    host, path, hdrs, body, https = _prep(method, url, headers, params, json, data, None, cookies, verify)
    try:
        conn = _make_conn(host, https, timeout, verify)
        conn.request(method, path, body=body, headers=hdrs)
        r = conn.getresponse()
        status = r.status
        resp_headers = dict(r.getheaders())

        def read_chunks():
            while True:
                chunk = r.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            conn.close()

        return status, resp_headers, read_chunks()
    except builtins.TimeoutError as e:
        raise TimeoutError(f"timed out after {timeout}s") from e
    except (socket.timeout, http.client.ResponseNotReady) as e:
        raise TimeoutError(str(e)) from e
    except (ConnectionRefusedError, socket.gaierror, OSError) as e:
        raise ConnectionError(str(e)) from e


async def send(method, url, headers, params, json, data, files, cookies, timeout, verify) -> Response:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: _do(method, url, headers, params, json, data, files, cookies, timeout, verify)
    )


async def stream(method, url, headers, params, json, data, cookies, timeout, verify, chunk_size=8192) -> AsyncIterator[bytes]:
    loop = asyncio.get_event_loop()
    status, resp_headers, chunks = await loop.run_in_executor(
        None, lambda: _do_stream(method, url, headers, params, json, data, cookies, timeout, verify, chunk_size)
    )
    for chunk in chunks:
        yield chunk
