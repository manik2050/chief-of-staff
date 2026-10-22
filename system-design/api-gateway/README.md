# API gateways

Learning evidence for Day 21 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

An API gateway is a single entry point for the site. Clients send one
request there instead of a public URL per microservice. The services
behind it stay independently deployable. That coupling and the extra
client logic move onto the gateway, along with non-business work such as
authorization.

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
+--------------+  +--------------+   combine responses
| microservice |  | microservice | --------------------> client
+--------------+  +--------------+   cache if needed
```

```
# one public hop: limit, auth, then route; combine if several services reply
def handle(req):
    if over_limit(req):                 # prevent server overload
        reject()
    if not allowed(req):                # authorization
        reject()
    req = transform(validate(req))      # header and body vs schema
    backends = route(req.path, req.headers, req.method, req.query)
    parts = [b.fetch(req) for b in backends]
    resp = combine(parts)
    if should_cache(resp):
        cache.put(req, resp)
    return resp
```

Without the gateway, each client talks to each service and often gets the
same payload on desktop and mobile: worse latency and bandwidth. The hop
also terminates SSL so backends skip decrypt. Device type in HTTP headers
can pick a different route; a backend-for-frontend is a separate gateway
per device (desktop, mobile). A circuit breaker pauses repeated failing
requests so unhealthy servers are not overloaded. The extra hop adds
latency, cost, and ops work, and one instance is a bottleneck and a SPOF
unless you run more. Nginx, Kong, and Tyk are common setups. Use a
gateway when clients would otherwise call many public microservice URLs,
or when rate limiting, authorization, and combining responses should sit
off the business services. Skip it when that complexity is more than
the value.

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
