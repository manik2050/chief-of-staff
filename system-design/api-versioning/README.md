# API versioning

Learning evidence for Day 25 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

An API is a contract: the data shape, the endpoints, and the behavior.
Renaming a field, changing a response format, or moving an endpoint can
break someone else's production system. Versioning says the old contract
is still valid while a new one exists. A `/v1/` in the URL does not freeze
the contract: the article's author has seen APIs rename fields under the
same number for years. Teams that own both sides can sync deploys and ship
a break; a public API is bound by SLAs, legal contracts, and third-party
dependencies, so it cannot just break consumers.

```
  client
     |
     |  version selector (one of)
     v
  /api/v1/orders                      URI path
  /api/orders?api-version=1           query
  api-version: 1                      custom header
  Accept: application/vnd.x.v1+json   media type
     |
     v
+------------------+  additive: same version, new fields only
|  contract        |  explicit: v1 and v2 both live
|  /orders/123     |  same resource, different representation
+------------------+
     |  retiring v1
     v
  Deprecation: true
  Sunset: <HTTP-date>            RFC 8594
  301 Location: /api/v2/orders   small move; big breaks still need code
```

```python
# Toy version router, not a product. python3 - <<'PY' ... PY
order = {"id": 123, "status": "shipped", "addr": "1 Main St"}

def body(ver):
    if ver == 1:
        return {"id": order["id"], "status": order["status"], "addr": order["addr"]}
    return {"id": order["id"], "status": order["status"],
            "address": {"line": order["addr"]}}   # v2 nested; breaking rename

def version(path, query, headers):
    for part in path.split("/"):
        if part in ("v1", "v2"):
            return int(part[1])
    if "api-version" in query:
        return int(query["api-version"])
    if "api-version" in headers:
        return int(headers["api-version"])
    accept = headers.get("Accept", "")
    if "v2" in accept or "api-version=2" in accept:
        return 2
    return 1

def handle(path, query=None, headers=None):
    ver = version(path, query or {}, headers or {})
    extra = {"Vary": "Accept"}
    if ver == 1:
        extra["Deprecation"] = "true"
        extra["Sunset"] = "Wed, 01 Jul 2026 00:00:00 GMT"  # academy example
    return ver, extra, body(ver)

ver, extra, b = handle("/api/v1/orders/123")
print("path ", ver, sorted(b), extra["Sunset"])
for name, kw in (("query", dict(query={"api-version": "2"})),
                 ("header", dict(headers={"api-version": "2"})),
                 ("media", dict(headers={"Accept": "application/vnd.example.v2+json"}))):
    ver, extra, b = handle("/api/orders/123", **kw)
    print(f"{name:6}", ver, sorted(b))
# path  1 ['addr', 'id', 'status'] Wed, 01 Jul 2026 00:00:00 GMT
# query  2 ['address', 'id', 'status']
# header 2 ['address', 'id', 'status']
# media  2 ['address', 'id', 'status']
```

Additive changes (new fields, optional parameters) need no client work and
are, per the article, good enough for most cases; explicit versions carry
a break. Path (`/api/v1/orders`) is common and easy to route, but pollutes
URLs and gives one order two identities; keep the old path alive during
the transition (an [API gateway](../api-gateway/) can route `/v1` and `/v2`
to different backends). Query keeps the URL stable but needs custom
routing and cache keys; [API design](../api-design-best-practices/) said
to avoid it because query is for filter/search. Header or media type keeps
the URI stable but is harder to debug and cache, so send `Vary: Accept`;
the article calls it the cleanest long-term choice while also saying no
single strategy is best. Its "when": path for internal consumers you
control, header for external or long-lived clients, payload for events
replayed later. Stripe uses a CalVer `Stripe-Version` header; GitHub a
date header on a stable base URL, each version supported at least 24
months. To retire v1, send `Deprecation: true` plus a `Sunset` HTTP-date
(a hint the URI will stop answering); a `301` only helps a small move.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([API Versioning](https://newsletter.systemdesign.one/p/api-versioning)
(contract; `/v1/` does not freeze it; internal vs public; additive vs
explicit; path, query, header, media type, payload; Sunset example,
`Deprecation: true`, 301; Stripe CalVer and GitHub 24 months; "when" by
selector; additive good enough for most),
[Best Practices for API Design](https://newsletter.systemdesign.one/p/best-practices-for-api-design)
(query for filter/search, not versions; version only breaking changes));
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Communication: REST identifies a resource by the same URI regardless of
operation);
[RFC 8594](https://www.rfc-editor.org/rfc/rfc8594)
(Sunset is an HTTP-date hint; the still-serving deprecation stage is
signalled by other mechanisms).
