# API versioning

Learning evidence for Day 25 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Versioning is a structured way to change an API contract without stranding
the clients that already depend on it. The contract is the data shape, the
endpoints, and the behavior. A rename, a new response format, or a moved
endpoint can break someone else's production system. Versioning is how the
owner says the old contract is still valid while a new one exists. Putting
`/v1/` in the URL does not freeze that contract: the academy has seen APIs
keep renaming fields under the same number, and APIs that stay on `v1`
forever because the same organization owns the clients. Internal teams that
own both sides can sync deploys and ship a break. A public API whose
consumers you do not own is bound by SLAs, legal contracts, and third-party
dependencies, so you cannot just break them.

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
        extra["Location"] = "/api/v2/orders/123"
    return ver, extra, body(ver)

print(handle("/api/v1/orders/123")[0], "flat addr + Sunset")
for kw in (dict(query={"api-version": "2"}),
           dict(headers={"api-version": "2"}),
           dict(headers={"Accept": "application/vnd.example.v2+json"})):
    print(handle("/api/orders/123", **kw)[0], "nested address")
# 1 flat addr + Sunset
# 2 nested address   (query, then header, then media type)
```

Three paths as the API evolves: a new location (`/api/v2/orders` beside
`/api/v1/orders`) is easy for clients and expensive for the owner; a
backward-compatible change (new fields, optional parameters) needs no
client work but cannot absorb a large redesign; a break that forces every
client to upgrade is sometimes unavoidable. Additive versioning adds
without incrementing; explicit versioning creates a new URL, header, or
parameter when compatibility breaks. URI path (`/api/v1/orders`) is, per
the academy, one of the most common selectors: visible and easy to route,
at the cost of many versions in the URL. REST identifies a resource by
URI, so `/api/v1/orders` treats the same order as two identities; keep
the old path during a transition (an [API gateway](../api-gateway/) can
route `/v1` and `/v2` to different backends). Query (`?api-version=1.2.3`)
keeps the base URL stable but needs custom routing and cache keys.
[API design](../api-design-best-practices/) said avoid query for versions
(it is for filter/search); this article treats it as an option when you
want a stable path and can pay that cost. Neither names a universal
winner. Header (`api-version: 2`) or media type
(`Accept: application/vnd.example+json;api-version=2`) keeps the URI
stable; harder to debug and cache — send `Vary: Accept`. The academy
calls header versioning the cleanest long-term choice for stable URLs,
and also says there is no single best strategy. Primer REST: one URI
regardless of operation, representation through headers;
[communication](../communication/) RPC is the usual internal style.
Payload versioning (`"version": "v1"` in the body) is for events replayed
later, not short-lived REST. Deprecation is "please leave"; sunset is
"this URI will stop answering." The academy pairs `Deprecation: true`
with a Sunset date (example `Wed, 01 Jul 2026 00:00:00 GMT`); RFC 8594:
Sunset is an HTTP-date hint, and deprecation (still serving) is an earlier
stage. Academy "when": path when you control the consumers; query for
resource-level flexibility if you can tolerate routing complexity; header
for external or long-lived clients you do not control; payload for
event-driven replay. Stripe (academy): `Stripe-Version` CalVer. GitHub
(academy): date header on an unversioned URL, each version at least 24
months. Raise a version only when the contract changes in a way that
matters to consumers. Academy bottom line: additive is good enough for
most cases; pick the selector that surprises consumers least.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([API Versioning](https://newsletter.systemdesign.one/p/api-versioning)
— contract; `/v1/` does not freeze the contract; internal vs public;
new location / backward-compatible / break; additive vs explicit; path,
query, header, media type, payload; Sunset, `Deprecation: true`, 301;
Stripe and GitHub (24 months); when to bump; "when" by selector;
additive good enough for most),
[Best Practices for API Design](https://newsletter.systemdesign.one/p/best-practices-for-api-design)
(query for filter/search, not versions; version only breaking changes);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Communication: REST vs RPC; same URI regardless of operation;
representation through headers; REST for public HTTP APIs);
[RFC 8594](https://www.rfc-editor.org/rfc/rfc8594)
(Sunset HTTP-date; hint; deprecation vs sunset).
