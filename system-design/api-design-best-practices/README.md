# API design best practices

Learning evidence for Day 23 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

REST (Representational State Transfer) is an architectural pattern for
systems talking over the Internet. It organizes data as resources: `/items`
is a collection, `/items/<id>` is one item. GET reads, POST adds, PUT
replaces, DELETE removes. That is predictable, but some actions (the
academy's example is publishing a draft) do not fit those verbs, so
balance REST with a pragmatic approach. The other practices cover what
broke that startup: a version so a breaking change does not break old
clients, a rate limit so spiky traffic does not take the API down, and
pages so a request for latest data is not the entire dataset.

```
  client
     |
     | GET /v1/items?page=1&limit=20
     v
+------------------+  over limit -> 429 Too Many Requests
|  rate limiter    |  X-RateLimit-Limit / Remaining / Reset
+------------------+  prefer API key; many clients share an IP
     |
     v
+------------------+  /v1 stays; breaking change on /v2
|  resource        |  GET / POST / PUT / DELETE
|  /items          |  error: status (client vs server) + body
|  /items/<id>     |  (only enough detail)
+------------------+
     | large set
     v
  offset (?page=&limit=) or cursor after last record
```

```python
# Toy API, not a product. python3 - <<'PY' ... PY
items = [1, 2, 3, 4, 5]
seen, idem = {}, {}

def handle(client, method, page=1, key=None):
    seen[client] = seen.get(client, 0) + 1
    if seen[client] > 2:                    # counter; reject past the limit
        return "429 Too Many Requests"
    if method == "GET":
        start = (page - 1) * 2              # ?page=2&limit=2 skips first 2
        return items[start:start + 2]
    if key in idem:
        return idem[key]                    # same key: cached, no second write
    items.append(len(items) + 1)
    idem[key] = "created %d" % items[-1]
    return idem[key]

print(handle("k1", "GET", page=1))
print(handle("k1", "GET", page=2))
print(handle("k1", "GET", page=1))
print(handle("k2", "POST", key="uuid-a"))
print(handle("k2", "POST", key="uuid-a"))
print("items", items)
# [1, 2]
# [3, 4]
# 429 Too Many Requests
# created 6
# created 6
# items [1, 2, 3, 4, 5, 6]
```

Path versioning puts the number in the URL (`/v1/subpath`, `/v2/subpath`);
the old path is not updated. The Accept header can carry the version
instead (`application/vnd.api.v1+json`). Query `?version=` is for
filtering or search, so the academy says to avoid it for versioning, and
to version only for breaking changes — it adds complexity and
maintenance. Offset pagination is simple and can jump to a page
(`?page=3&limit=20` skips 40, returns 20) but scans skipped rows and can
shift if rows are added or removed. Cursor pagination reads after a
pointer using an index and stays consistent; it cannot jump to a page.
Filter (`?type=`) and sort (`?sort=&order=asc`) shrink the payload; both
add server logic, and sort without an index can slow a large table.
Idempotency: a UUID in the header, cache the response, drop keys later;
extra cost, for retries that would otherwise double-apply. Primer: REST
exposes resources over uniform verbs, stateless and cacheable, weaker
coupling — stay REST while the data is a hierarchy of resources, and for
public HTTP APIs. RPC names the procedure; use it internally when the job
does not map onto GET, POST, PUT, DELETE, or PATCH.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Best Practices for API Design](https://newsletter.systemdesign.one/p/best-practices-for-api-design)
— REST resources and HTTP verbs; pragmatic when an action does not fit;
status plus body, only enough detail; path/header/query versioning, query
for filter/search so not for versions, version only breaking changes;
rate-limit counter, 429, X-RateLimit-* headers, API key over shared IP;
offset vs cursor pagination; idempotency key and cached response;
filter and sort query params);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Communication: REST vs RPC; HTTP verbs including PATCH; REST
stateless and cacheable, public HTTP APIs; RPC for internal
behavior-focused calls).
