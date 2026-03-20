# asken 🔵

Modern async Python HTTP client. Faster and more productive.

```bash
pip install asken
```

## Async

```python
import asken

# simple use
res = await asken.get("https://api.example.com/users")
print(res.status, res.data)

# with config
api = asken.create(base_url="https://api.example.com", token="my-token")
res = await api.post("/users", json={"name": "Cris"})

# Context
async with asken.create(base_url="https://api.example.com") as api:
    res = await api.get("/users")
```

## Sync

```python
# simple use
res = asken.sync.get("https://api.example.com/users")

# Instance
api = asken.sync.create(base_url="https://api.example.com", token="my-token")
res = api.post("/users", json={"name": "Cris"})
```

## Upload File

```python
with open("foto.jpg", "rb") as f:
    res = await asken.post("/upload", files={"file": f})

# with more field
res = await asken.post("/upload", files={"file": ("nama.jpg", f)}, data={"caption": "foto"})
```

## Streaming

```python
async for chunk in asken.stream("GET", "https://example.com/file.zip"):
    with open("file.zip", "ab") as f:
        f.write(chunk)
```

## Cookies

```python
res = await asken.get("/profile", cookies={"session": "abc123"})

# create
api = asken.create(base_url="...", cookies={"session": "abc123"})
```

## SSL

```python
# ssl verif
res = await asken.get("https://localhost/api", verify=False)

# create
api = asken.create(base_url="https://localhost", verify=False)
```

## HEAD & OPTIONS

```python
res = await asken.head("https://api.example.com/users")
res = await asken.options("https://api.example.com/users")
print(res.headers)
```

## Auth

```python
api = asken.create(base_url="...", token="my-token")
api = asken.create(base_url="...", api_key="my-key", api_key_header="X-API-Key")
```

## Error Handling

```python
try:
    res = await api.get("/protected")
except asken.AuthError as e:
    print(e.status, e.response.data)
except asken.NotFoundError: ...
except asken.RateLimitError: ...
except asken.ServerError: ...
except asken.AskenError as e:
    print(e.status)
```

## Response

```python
res.status     # int
res.data       # dict | str | None
res.headers    # dict
res.url        # str
bool(res)      # True if 2xx
```

## Requirements

- Python 3.10+

## License

MIT
