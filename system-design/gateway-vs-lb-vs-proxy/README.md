# API gateway vs load balancer vs reverse proxy

Learning evidence for Day 22 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A load balancer, an API gateway, and a reverse proxy all sit in front of
servers and manage traffic. They overlap: each can be the public address,
each forwards a request and returns a response, and NGINX and HAProxy do
both layer-7 reverse proxying and load balancing. They are not the same
job. Per-hop notes are already boarded:
[load balancers](../load-balancers/), [reverse proxy](../reverse-proxy/),
[API gateway](../api-gateway/). This day is the comparison.

A load balancer picks one healthy replica of the same function so one
process is not the capacity limit or the SPOF. An API gateway is the
single entry for many services: throttle, transform, route by path,
headers, or query, then combine responses. A reverse proxy is useful even
with one backend: one public face, hide internals, cache, terminate TLS.
A typical edge stacks them — balancer across gateway instances, gateway
in front of per-service proxies — but that is not the only order.

```text
  clients
     |
     v
+------------------+
|  load balancer   |  even spread; skip the dead
+------------------+
     |
     v
+------------------+
|  API gateway     |  throttle, transform, route, combine
+------------------+
     | /feed              | /pay
     v                    v
+------------+      +------------+
| reverse    |      | reverse    |  hide backends; cache
| proxy      |      | proxy      |
+------------+      +------------+
     |                    |
     v                    v
   feed svc             pay svc
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

The balancer spreads equivalent boxes. The gateway fans one client call
out to different services and can reject it. The reverse proxy can answer
from cache so the second identical call never reaches the backend. Layer-7
load balancing already reads URLs and headers, so it starts to look like
a gateway; a gateway that only routes starts to look like a reverse proxy.
Use a load balancer when equivalent servers must share load. Use a reverse
proxy when you want one public face, TLS at the edge, or static/cache off
the app — even with one server. Use an API gateway when clients would
otherwise call many public microservice URLs, or when rate limiting,
authorization, and combining responses should sit off the business
services. Skip a hop when the extra network step and ops work are more
than the value: each hop adds latency and can be a bottleneck or a SPOF
unless paired.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([API Gateway vs Load Balancer vs Reverse Proxy](https://newsletter.systemdesign.one/p/api-gateway-load-balancer-reverse-proxy)
— LB distributes; gateway throttles, transforms, routes, combines;
reverse proxy hides backends, TLS, cache; typical edge stacks all three,
not the only setup; extra hop, bottleneck, SPOF);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Load balancer: skip unhealthy, L4 vs L7, bottleneck and SPOF;
Reverse proxy: hide backends, SSL termination, cache, static content;
Load balancer vs reverse proxy: LB for several equivalent servers, reverse
proxy useful with one, NGINX/HAProxy do both).
