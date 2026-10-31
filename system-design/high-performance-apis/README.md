# High-performance APIs

Learning evidence for Day 26 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Every API request does work: parse the payload, query the database,
package the response, send it back. As traffic grows those small delays
add up. Neo Kim's letter argues the fix is not faster code but a system
that does less work per request: cache responses that do not change,
compress big ones, spread load across servers, and move slow IO onto a
queue. Databases, network round trips, downstream services, and large
payloads usually dominate latency before application code does.

```
  request X
     |
     v
+---------------+  pick a healthy, less-busy server
| load balancer |  autoscale on CPU / memory / request rate
+---------------+
     |
     v
+---------------+  hit: return cached Y
| API server    |  miss: parse, query, package Y, store Y
| + cache       |  gzip Y if Accept-Encoding allows it
+---------------+
     |  slow IO (email, files, downstream call)
     v
  enqueue; return a job id; a worker does the wait
```

```python
# Toy API, not a measurement. python3 - <<'PY' ... PY
import gzip

work, cache = 0, {}
body = "item," * 400                 # 2000 bytes; letter: best past 1KB

def get(key):
    global work
    if key in cache:
        return cache[key], "hit"
    work += 1                        # miss: parse, query, package once
    cache[key] = body
    return body, "miss"

a, first = get("catalog")
_, second = get("catalog")
raw, gz = len(a.encode()), len(gzip.compress(a.encode()))
print(first, second, "work", work)
print("raw", raw, "gzip", gz)
# miss hit work 1
# raw 2000 gzip 40                   repeated text, not a JSON ratio
```

A cache skips the database, but stale data is the cost; invalidate with
a TTL, manual removal, or Cache-Control headers. Compression costs CPU
on every encode and decode and can lose on small bodies. A load balancer
without redundancy is a single point of failure, and autoscaling that
triggers too early wastes money while too late hurts. A queue keeps
IO-bound requests fast but helps little with CPU-bound work; keep cheap
or realtime work synchronous. The letter also names connection pooling,
rate limiting, circuit breakers, pool exhaustion, and retry storms, but
the free teaser does not explain them.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([High Performance APIs](https://newsletter.systemdesign.one/p/api-performance)
(#165: per-request work; not faster code; caching and compression; load
balancing and autoscaling; asynchronous processing; contents list));
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Asynchronism: realtime and inexpensive work may be better synchronous).
