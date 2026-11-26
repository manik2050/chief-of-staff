# API design concepts, part 1

Learning evidence for Day 29 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Neo Kim's #184 names 17 API design concepts (REST through API keys); Part
2 continues to 33. The public teaser defines seven, sketched here (status
codes through API keys are named there, not defined here). REST organizes
data as resources with their own URLs (`/users/42`, `/orders/17`) and
HTTP methods: GET read, POST create, PUT replace, DELETE remove. It stays
stateless, so any server can answer. GraphQL is one endpoint: the client
names the fields, the server walks the query and returns that shape in
one round trip (queries read, mutations change, subscriptions stream).
Authentication proves who is calling; a failed check is 401 and never
reaches business logic. Authorization then decides what that identity may
do; a known caller who still may not is 403. Rate limiting counts per
window and, past the cap, returns 429 Too Many Requests plus Retry-After.
Caching stores a copy so the next identical request skips origin work
(`Cache-Control` for freshness; `ETag` then 304 Not Modified with no
body). Pagination returns a slice: offset is page number and size; a
cursor is an opaque marker of where you stopped.

```
  client
     |
     |  REST: GET /users/42          GraphQL: { user { id name } }
     v
+------------------+  401 if identity fails (authn first)
|  API             |  403 if known and still no (authz)
|                  |  past the cap -> 429 + Retry-After
|                  |  cache: Cache-Control / ETag -> 304
+------------------+  page: offset (page+size) or cursor
```

```python
# Toy REST vs GraphQL shape. python3 - <<'PY' ... PY
user = {"id": 42, "name": "maya", "email": "hidden", "bio": "x"}

def rest_get(_id):
    return user                          # every field, including unused

def graphql(fields):
    return {k: user[k] for k in fields}  # client names what it needs

print("rest", sorted(rest_get(42)))
print("gql", graphql(["id", "name"]))
# rest ['bio', 'email', 'id', 'name']
# gql {'id': 42, 'name': 'maya'}
```

REST wastes requests and bandwidth: one screen may need a user, their
orders, and payment (three round trips); the server sends every field,
including the twenty you ignore. Keep resources small; reach for GraphQL
when clients shape their own responses. GraphQL makes caching harder
(every query is a POST to the same URL); one careless nested query could
walk the database for a minute; carry a schema, a resolver per field, and
an N+1 plan; set a depth limit and a query cost budget on day one. Pair
it with rate limiting: a single expensive query can cost more than a
thousand REST calls. Authn costs a lookup or signature check; keep
secrets out of URLs and rotate them. Authz rules sprawl; a missing check
is a breach; test the negative case and check ownership at the data layer
and the route. Rate limits frustrate honest heavy users; counting across
servers needs shared state; token bucket handles bursts better than a
fixed window. Cached copies go stale; never cache a private response in a
shared layer. Offset pagination drifts when a row is inserted mid-read;
cursor pagination cannot jump to an arbitrary page. Cursors for feeds,
offsets for admin tables. Primer: REST exposes data through URIs and
GET/POST/PUT/DELETE/PATCH, is stateless and cacheable, and is often used
for public HTTP APIs; nested views need multiple round trips and extra
fields bloat older clients.
REST for public APIs, mobile and web, edge-cached reads, and endpoints a
new developer should guess on the first try (Spring, Express, Django REST
Framework, FastAPI). GraphQL for mobile on slow networks, screens that
stitch several resources, and front ends that change faster than the
backend (Apollo, Relay, Hasura, graphql-js). Authn for private data,
money, or a user account. Authz for multi-tenant systems and admin
panels. Rate limits for public APIs, free tiers, login, and expensive
search or export. Cache catalogs, public profiles, and search results.
Paginate every list, feed, and export (Stripe, GitHub, and Slack publish
cursor-based APIs).

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([API Design Concepts - Part 1](https://newsletter.systemdesign.one/p/api-concepts-every-software-engineer-should-know)
— Neo Kim, #184: 17 concepts REST through API keys; public teaser
defines REST through pagination; `/users/42`; three round trips; twenty
unused fields; GraphQL POST cache; one-minute nested walk; depth and cost
budget; 401 then 403; 429 and Retry-After; Cache-Control, ETag, 304;
offset vs cursor; Stripe, GitHub, Slack cursors);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Communication: REST URIs, GET/POST/PUT/DELETE/PATCH, stateless,
cacheable, public HTTP APIs; nested views need multiple round trips;
extra fields bloat older clients).
