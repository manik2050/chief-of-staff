# API gateways

Learning evidence for Day 21 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

An API gateway is a single entry point for the site. Clients send one
request there instead of a public URL per microservice. The services
behind it stay independently deployable. Calling each service directly
meant tight coupling and more client complexity; the gateway simplifies
the client and takes non-business logic such as authorization.

```
  clients  (HTTPS)
     |
     v
+------------------+  SSL termination (decrypt here)
|  API gateway     |  rate limit
|  single entry    |  allowed? (authorization)
|                  |  schema; transform if needed
+------------------+  route: path, headers, method, query
     |
     |  one or more microservices
     v
+--------------+  +--------------+
| microservice |  | microservice |
+--------------+  +--------------+
     |                 |
     v
API gateway: combine responses, cache if needed --> client
```

```python
# Toy gateway, not a real one. python3 - <<'PY' ... PY
over_limit, allowed = {"bot"}, {"maya", "bot"}      # rate limit, authorization
routes = {"/profile": ["users", "reviews"]}         # route by URL path
services = {"users": "name=maya", "reviews": "stars=ok"}
cache = {}

def handle(client, path):
    if client in over_limit:
        return "rejected: rate limit"               # prevent server overload
    if client not in allowed:
        return "rejected: not allowed"
    parts = [services[s] for s in routes[path]]     # one or more microservices
    resp = "; ".join(parts)                         # combine responses
    cache[path] = resp                              # cache if needed
    return resp

for client in ("maya", "bot", "eve"):
    print(f"{client}: {handle(client, '/profile')}")
# maya: name=maya; stars=ok   one request, two services combined
# bot: rejected: rate limit
# eve: rejected: not allowed
```

Without the gateway, each client talks to each service, and desktop and
mobile get the same payload: worse latency and bandwidth. The gateway
also terminates SSL so backends skip decrypt. Device type in HTTP headers
can pick a different route; a backend-for-frontend is a separate gateway
per device (desktop, mobile). A circuit breaker pauses repeated failing
requests so unhealthy servers are not overloaded. The extra network hop
adds latency; the gateway adds cost and ops work from maintenance; it can
become a bottleneck under high traffic, and a SPOF if set up incorrectly,
so run more than one instance. Nginx,
Kong, and Tyk are common setups. Use a gateway when clients would otherwise
call many public microservice URLs, or when rate limiting, authorization,
and combining responses should sit off the business services. Skip it when
that complexity is more than the value.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([How API Gateway Works](https://newsletter.systemdesign.one/p/how-api-gateway-works)
— single entry; SSL termination; rate limiting; authorization; schema
validation and transform; route by URL path, HTTP headers, method, or
query parameters; combine responses; cache; device-type routing; circuit
breaker; BFF; extra hop, cost, bottleneck, SPOF unless several instances;
Nginx, Kong, Tyk);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Reverse proxy: SSL termination so backends skip decrypt; Application
layer: independently deployable microservices behind the web tier).
