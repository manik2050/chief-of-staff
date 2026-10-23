# API gateway vs load balancer vs reverse proxy

Learning evidence for Day 22 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A load balancer, an API gateway, and a reverse proxy all sit in front of
servers and manage traffic. They overlap: each forwards a request and
returns a response, and NGINX and HAProxy do both layer-7 reverse
proxying and load balancing. They are not the same job. A load balancer
spreads requests, often across servers that serve the same function, and
skips unhealthy ones. An API gateway is a single entry point: it throttles,
transforms, routes to microservices by URL path, headers, or query
parameters, and combines their responses. A reverse proxy is useful even
with one server: it hides the backend, terminates TLS, and caches
responses. A typical edge chains load balancer, API gateway, reverse
proxy, then servers, but that is not the only setup. Per-hop notes:
[load balancers](../load-balancers/), [reverse proxy](../reverse-proxy/),
[API gateway](../api-gateway/).

```
  clients
     |
     v
+------------------+
|  load balancer   |  even spread; skip unhealthy
+------------------+
     |
     v
+------------------+
|  API gateway     |  throttle, transform, route, combine
+------------------+
     |
     v
+------------------+
|  reverse proxy   |  hide backends; TLS; cache
+------------------+
     |
     v
  servers
```

```python
# Toy edge, not a product. python3 - <<'PY' ... PY

def lb(i, pool):
    live = [n for n, up in pool if up]
    return live[i % len(live)]              # equivalent replicas

cache = {}
def reverse_proxy(key, backend):
    hit = cache.get(key)
    if hit is not None:
        return "hit " + hit                 # skip the backend
    resp = backend
    cache[key] = resp
    return "miss " + resp

def gateway(path, client, routes, limited):
    if client in limited:
        return "throttled"                  # prevent overload
    parts = []
    for svc in routes[path]:                # different services
        parts.append(reverse_proxy(path + svc, svc + "-1"))
    return "; ".join(parts)                 # combine

print("lb", lb(0, [("gw-a", True), ("gw-b", True)]))
print("lb", lb(1, [("gw-a", True), ("gw-b", True)]))
print("lb skip", lb(0, [("gw-a", False), ("gw-b", True)]))
routes, limited = {"/feed": ["users", "posts"]}, {"bot"}
print("maya", gateway("/feed", "maya", routes, limited))
print("maya", gateway("/feed", "maya", routes, limited))
print("bot", gateway("/feed", "bot", routes, limited))
# lb gw-a
# lb gw-b
# lb skip gw-b
# maya miss users-1; miss posts-1
# maya hit users-1; hit posts-1
# bot throttled
```

The balancer spreads requests over equivalent servers. The gateway fans
one client call out to different services, combines the answers, and can
throttle the caller. The reverse proxy can answer a cached request
without calling the backend. Layer-7 load balancers already read URLs
and headers, and a gateway also routes by URL path and headers, so the
lines blur. Use a load balancer when several servers serve the same
function. Use a reverse proxy for one public face, TLS termination,
caching, or static content, even with one server. Use an API gateway
when clients need one entry point to many microservices, with
throttling, transforming, and combining in one place. A load balancer or
reverse proxy adds operational work and can be a single point of failure
without redundancy; the gateway's extra hop adds latency, and a load
balancer or gateway can become a bottleneck if set up badly.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([API Gateway vs Load Balancer vs Reverse Proxy](https://newsletter.systemdesign.one/p/api-gateway-load-balancer-reverse-proxy)
— LB distributes; gateway throttles, transforms, routes, combines;
reverse proxy hides backends, TLS, cache; typical edge is load balancer,
API gateway, reverse proxy, server, not the only setup; gateway extra hop
latency and bottleneck; LB and reverse proxy operational cost and SPOF);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Load balancer: skip unhealthy, L4 vs L7, bottleneck and SPOF;
Reverse proxy: hide backends, SSL termination, cache, static content;
Load balancer vs reverse proxy: LB for several equivalent servers, reverse
proxy useful with one, NGINX/HAProxy do both).
