# High-performance APIs

Learning evidence for Day 26 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Neo Kim's academy letter (#165) is his, not a guest post. Each request
parses, queries, packages, and sends; under traffic those waits stack.
The letter's claim is that faster code is not the fix: do less work and
stay fast under load. The public teaser walks through caching and
compression, load balancing and autoscaling, and asynchronous processing.
The contents also name connection pooling, rate limiting, and circuit
breakers as patterns to combine, and list failure modes (stale caches,
pool exhaustion, retry storms, payload bloat, poorly tuned autoscaling)
without the full how-to in the free text.

```
  request X
     |
     v
+------------------+  hit: return cached Y
| cache            |  miss: parse, query, package Y, store Y
+------------------+
     |  maybe gzip (Accept-Encoding / Content-Encoding)
     v
+------------------+  pick a healthy, less-busy server
| load balancer    |  autoscale on CPU / memory / request rate
+------------------+
     |  slow IO (email, files, downstream)
     v
  enqueue; return job id; worker does the wait
```

```python
# Toy API, not a product. python3 - <<'PY' ... PY
import gzip

work, cache, opens, pool = 0, {}, 0, []
body = ("item," * 400)              # 2000 bytes; academy: gzip helps past 1KB

def checkout():
    global opens
    if pool:
        return pool.pop(), "reuse"  # primer: pool instead of a new TCP each time
    opens += 1
    return "c", "open"

def get(key):
    global work
    conn, how = checkout()
    pool.append(conn)               # return the conn for the next call
    if key in cache:
        return cache[key], "hit", how
    work += 1                       # miss: parse, query, package once
    cache[key] = body
    return body, "miss", how

a, first, h1 = get("catalog")
_, second, h2 = get("catalog")
raw, gz = len(a.encode()), len(gzip.compress(a.encode()))
print(first, second, "work", work)
print(h1, h2, "opens", opens)
print("raw", raw, "gzip", gz)
# miss hit work 1
# open reuse opens 1
# raw 2000 gzip 40                  toy repeated text, not a JSON ratio
```

Cache data that does not change often (profile lookups, catalog searches);
Redis/Memcached in-memory, Fastly/Cloudflare at the edge. Invalidation is
TTL, manual removal, or Cache-Control; stale data is the cost. Gzip or
Brotli (or Protobuf/Avro) for large JSON/binary — the letter says best
past 1KB; CPU can outweigh the win on small bodies. Load balance (AWS
ELB, HAProxy, Nginx) so one box is not the queue; without redundancy the
balancer is a SPOF, and sticky sessions paper over local state. Autoscale
(Kubernetes HPA, AWS Auto Scaling Groups) adds and drops boxes; too-early
wastes money, too-late and slow startup hurt. Async (RabbitMQ, Kafka,
Celery) for IO-bound work: return a job id; little help for CPU-bound
work. Primer: a cache hit skips execution; aim for maximal throughput
with acceptable latency; reverse proxies can compress and cache; TCP
pooling avoids many open connections (e.g. to memcached); queue slow
work. Use these when traffic, payload size, or a slow dependency is the
wait. Skip a cache until you can name invalidation. Skip gzip on tiny
bodies. Skip a queue when the caller needs the result now.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([High Performance APIs](https://newsletter.systemdesign.one/p/api-performance)
— Neo Kim #165; parse/query/package/send; not faster code; cache then
compress; gzip/brotli, Accept-Encoding, best past 1KB; load balancing and
autoscaling; async IO via a queue; contents also name pooling, rate
limits, circuit breakers; failure modes listed above);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Cache: hit skips execution, invalidation is hard; Latency vs throughput:
maximal throughput with acceptable latency; Reverse proxy: compress and
cache responses; TCP: connection pooling; Asynchronism: queue slow work;
HTTP: hops may load-balance, cache, compress).
