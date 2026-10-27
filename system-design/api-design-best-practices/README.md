# API design best practices

Learning evidence for Day 23 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

REST (Representational State Transfer) is an architectural pattern for
systems talking over the Internet. It organizes data as resources: `/items`
is a collection, `/items/<id>` is one item. GET reads, POST adds, PUT
replaces, DELETE removes. That is predictable, but some actions (the
academy's example is publishing a draft) do not fit those verbs, so
balance REST with a pragmatic approach. The academy's startup had public
APIs that failed under spiky traffic, sent the entire dataset when users
asked for the latest data, and got hard to manage as features grew. The
other practices answer those: a rate limit, pages, and a version so a
breaking change does not break old clients.

```
  client
     |
     | GET /v1/items?page=1&limit=20
     v
+------------------+  over limit -> 429 Too Many Requests
|  rate limiter    |  X-RateLimit-Limit / Remaining / Reset
+------------------+  prefer API key; people may share an IP
     |
     v
+------------------+  /v1 stays; breaking change on /v2
|  resource        |  GET / POST / PUT / DELETE
|  /items          |  error: status (client vs server) + body
|  /items/<id>     |  (only enough detail)
+------------------+
     | large set
     v
  offset (?page=&limit=) or cursor (?cursor=&limit=)
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
instead (`application/vnd.api.v1+json`). Query parameters
(`?version=1`) are meant for filtering or search, so the academy says to
avoid them for versioning, and to version only for breaking changes — it
adds complexity and maintenance. Offset pagination is simple and can jump
to a page (`?page=3&limit=20` skips 40, returns 20) but scans skipped rows and can
shift if rows are added or removed. Cursor pagination reads after a
pointer using an index and stays consistent; it cannot jump to a page.
Filter (`?type=`) cuts bandwidth but adds server logic; sort
(`?sort=&order=asc`) orders results but can slow queries on a large
dataset without an index. Idempotency: a UUID in the request header, the
server caches the response, and keys are removed periodically to save
memory; it adds complexity and operational cost, so use it mainly for
critical APIs where a retry could cause unwanted side effects. Primer:
REST exposes data as resources through URIs and the verbs GET, POST,
PUT, DELETE, and PATCH; it is stateless and cacheable, minimizes
client/server coupling, and is often used for public HTTP APIs, but fits
poorly when resources are not a simple hierarchy or an action does not
fit those verbs. RPC exposes behaviors and is often used for internal
communication for performance.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Best Practices for API Design](https://newsletter.systemdesign.one/p/best-practices-for-api-design)
— REST resources and HTTP verbs; pragmatic when an action does not fit;
status plus body, only enough detail; path/header/query versioning, query
for filter/search so not for versions, version only breaking changes;
rate-limit counter, 429, X-RateLimit-* headers, API key over shared IP;
offset vs cursor pagination; idempotency key, cached response, periodic
key removal; filter and sort query params);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Communication: REST vs RPC; HTTP verbs including PATCH; REST
stateless and cacheable, public HTTP APIs; REST disadvantages:
non-hierarchical data, actions that do not fit the verbs; RPC exposes
behaviors, often internal for performance).
