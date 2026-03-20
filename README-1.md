<div align="center">

<h1>asken</h1>

<p>Modern async Python HTTP client — inspired by axios.<br>Fast, simple, and zero dependencies.</p>

<p>
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square" alt="MIT License"/>
  <img src="https://img.shields.io/badge/dependencies-none-f59e0b?style=flat-square" alt="Zero dependencies"/>
  <img src="https://img.shields.io/pypi/v/asken?style=flat-square&color=6366f1" alt="PyPI"/>
</p>

```bash
pip install asken
```

---

<h2>Quick Start</h2>

```python
import asken

res = await asken.get("https://api.example.com/users")
print(res.status, res.data)
```

---

<h2>Async</h2>

```python
import asken

# One-liner
res = await asken.get("https://api.example.com/users")

# Reusable instance
api = asken.create(base_url="https://api.example.com", token="my-token")
res = await api.post("/users", json={"name": "Cris"})

# Context manager
async with asken.create(base_url="https://api.example.com") as api:
    res = await api.get("/users")
```

<h2>Sync</h2>

```python
# One-liner
res = asken.sync.get("https://api.example.com/users")

# Reusable instance
api = asken.sync.create(base_url="https://api.example.com", token="my-token")
res = api.post("/users", json={"name": "Cris"})
```

---

<h2>Features</h2>

<h3>Upload File</h3>

```python
with open("photo.jpg", "rb") as f:
    res = await asken.post("/upload", files={"file": f})

# With additional fields
with open("photo.jpg", "rb") as f:
    res = await asken.post("/upload", files={"file": ("photo.jpg", f)}, data={"caption": "my photo"})
```

<h3>Streaming</h3>

```python
async for chunk in asken.stream("GET", "https://example.com/file.zip"):
    with open("file.zip", "ab") as f:
        f.write(chunk)
```

<h3>Cookies</h3>

```python
# Per request
res = await asken.get("/profile", cookies={"session": "abc123"})

# Per instance — applied to all requests
api = asken.create(base_url="https://api.example.com", cookies={"session": "abc123"})
```

<h3>SSL</h3>

```python
# Disable SSL verification
res = await asken.get("https://localhost/api", verify=False)

# Per instance
api = asken.create(base_url="https://localhost", verify=False)
```

<h3>HEAD &amp; OPTIONS</h3>

```python
res = await asken.head("https://api.example.com/users")
res = await asken.options("https://api.example.com/users")
print(res.headers)
```

---

<h2>Auth</h2>

```python
# Bearer token
api = asken.create(base_url="https://api.example.com", token="my-token")

# API Key
api = asken.create(base_url="https://api.example.com", api_key="my-key", api_key_header="X-API-Key")
```

---

<h2>Error Handling</h2>

```python
try:
    res = await api.get("/protected")
except asken.AuthError as e:
    print(e.status, e.response.data)   # 401 or 403
except asken.NotFoundError as e:
    print(e.status)                    # 404
except asken.RateLimitError as e:
    print(e.status)                    # 429
except asken.ServerError as e:
    print(e.status)                    # 5xx
except asken.AskenError as e:
    print(e.status)                    # catch-all
```

<br>

<details>
<summary>All available exceptions</summary>
<br>

| Exception | Status |
|:---------:|:------:|
| `AuthError` | 401, 403 |
| `NotFoundError` | 404 |
| `RateLimitError` | 429 |
| `ServerError` | 5xx |
| `TimeoutError` | request timed out |
| `ConnectionError` | connection failed |
| `AskenError` | base — catch-all |

</details>

---

<h2>Response</h2>

| Property | Type | Description |
|:--------:|:----:|:-----------:|
| `res.status` | `int` | HTTP status code |
| `res.data` | `dict \| str \| None` | Auto-parsed body |
| `res.headers` | `dict` | Response headers |
| `res.url` | `str` | Request URL |
| `bool(res)` | `bool` | `True` if 2xx |

---

<h2>Configuration</h2>

```python
api = asken.create(
    base_url       = "https://api.example.com",
    token          = "...",          # Bearer auth
    api_key        = "...",          # API key auth
    api_key_header = "X-API-Key",    # default: X-API-Key
    headers        = {"X-App": "myapp"},
    cookies        = {"session": "abc"},
    timeout        = 10.0,           # seconds, default: 10
    retries        = 3,              # default: 3
    retry_min      = 1.0,            # min wait between retries
    retry_max      = 8.0,            # max wait between retries
    verify         = True,           # SSL verification, default: True
)
```

---

<h2>Requirements</h2>

<p>Python 3.10+ &nbsp;·&nbsp; No external dependencies</p>

---

<h2>License</h2>

<p><a href="LICENSE">MIT</a></p>

</div>
