from __future__ import annotations

import mimetypes
import os
import uuid


def build(files: dict, data: dict | None = None) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    ct = f"multipart/form-data; boundary={boundary}"
    parts = []

    if data:
        for k, v in data.items():
            parts.append(
                f"--{boundary}\r\n"
                f"Content-Disposition: form-data; name=\"{k}\"\r\n\r\n"
                f"{v}\r\n".encode()
            )

    for field, file in files.items():
        if isinstance(file, tuple):
            filename, fileobj = file[0], file[1]
        else:
            filename = os.path.basename(getattr(file, "name", field))
            fileobj = file

        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        content = fileobj.read() if hasattr(fileobj, "read") else file

        parts.append(
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"{field}\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n".encode() + content + b"\r\n"
        )

    body = b"".join(parts) + f"--{boundary}--\r\n".encode()
    return body, ct
