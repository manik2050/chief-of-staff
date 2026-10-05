# Reverse proxies

Learning evidence for Day 7 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A reverse proxy sits in front of internal services and is the one public
address. Clients send a request to the proxy. The proxy forwards it to a
backend that can fulfill it, then returns that response. Backends stay
private. The public interface stays one hop even as you add, move, or
replace servers.

```
  clients
     |
     v
+------------------+  static / cache hit   +--------+
|  reverse proxy   | --------------------> | reply  |
|  terminate TLS   |                       +--------+
|  hide backends   |
+------------------+
     | app path / miss
     v
+------------------+
|  upstream        |
|  (one is enough) |
+------------------+
```

```
# one public hop: static and cache stay on the proxy; else forward upstream
def handle(req):
    if is_static(req.path):
        return proxy.read_file(req.path)   # HTML/CSS/JS, photos, video
    cached = proxy.cache.get(req)
    if cached is not None:
        return cached                      # skip the backend
    resp = upstream.fetch(req)             # TLS already terminated
    if cacheable(resp):
        proxy.cache.put(req, resp)
    return resp
```

A load balancer belongs in front of several equivalent servers. A reverse
proxy is useful even with one app: hide backends, blacklist or cap
connections, terminate SSL so X.509 lives on one box, compress, cache, and
serve static files. NGINX and HAProxy can do both L7 reverse proxying and
load balancing. The extra hop adds complexity. One proxy is a SPOF; a
failover pair adds more complexity. Use a reverse proxy when you want one
public face, TLS at the edge, or static/cache off the app. Use a load
balancer when equivalent servers must share load.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Reverse proxy: security, SSL termination, compression, caching, static
content; load balancer vs reverse proxy; NGINX/HAProxy);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Forward Proxy vs Reverse Proxy](https://newsletter.systemdesign.one/p/forward-proxy-vs-reverse-proxy),
[API Gateway vs Load Balancer vs Reverse Proxy](https://newsletter.systemdesign.one/p/api-gateway-load-balancer-reverse-proxy));
[NGINX: reverse proxy vs load balancer](https://www.nginx.com/resources/glossary/reverse-proxy-vs-load-balancer/);
[NGINX Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
(`proxy_pass`: forward, fetch, return);
[Wikipedia: Reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy).
