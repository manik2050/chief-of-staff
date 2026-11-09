# Caching patterns

Learning evidence for Day 33 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A cache is temporary storage for frequently used data, usually in memory
for low latency (Neo Kim). Memory is limited, so how the cache is updated
matters. A hit is data already in the cache; a miss is not. Redis and
Memcached are popular caches. Real systems combine these patterns.

Cache aside (lazy loading): the app reads the cache, on a miss reads the
database, writes the cache, and returns. The cache never talks to the
database; the app does. Only queried data is cached. Easy to implement,
with finer control over population. Many trips degrade latency; data can
be inconsistent. General-purpose caching and read-heavy workloads.

Write through: the app writes the cache; the cache writes the database
synchronously. The app never talks to the database; the cache does.
Consistent, and reads are fast because the cache holds fresh data. Write
latency is high (both stores); most cached data is never read. Use when
few writes are expected and freshness is important.

Read through: the same four read steps as cache aside, except the cache
talks to the database, not the app. Low read latency for hot data, and
better read scalability. The cache can be stale; a miss is slow. Use on
read-heavy workloads. A high miss rate is acceptable.

Write back (write-behind): the app writes the cache; the cache writes the
database asynchronously, and those writes can be batched. Low write
latency. The cache can fail before the flush (data loss); implementation
is complex. Write-heavy workloads where durability is not important.

Write around: the app writes the database, then reads the cache, filling
it from the database on a miss. Lower data-loss risk and less cache
pollution (only frequently accessed data). High read latency and a high
miss rate. Use when no update is expected and reads are few.

| pattern | db talk | write | next read | when |
| --- | --- | --- | --- | --- |
| cache aside | app | db only | may stale | general / read-heavy |
| write through | cache, sync | cache then db | fresh | few writes, freshness |
| read through | cache | (read path) | may stale | read-heavy; miss ok |
| write back | cache, async | cache; db later | fresh | write-heavy; not durable |
| write around | app | db, then lazy fill | miss/stale | no updates; few reads |

```python
# Toy: dict cache + dict db. python3 - <<'PY' ... PY
def demo(name, to_cache, to_db, start_cache=True):
    db, n = {"k": "old"}, {"r": 0, "w": 0}
    cache = {"k": "old"} if start_cache else {}
    if to_cache:
        cache["k"] = "new"
    if to_db:
        db["k"] = "new"; n["w"] += 1
    if "k" in cache:
        val = cache["k"]
    else:
        n["r"] += 1
        val = cache["k"] = db["k"]  # miss fill: app (aside/around) vs cache
    flag = "fresh" if val == "new" else "stale"
    print(f"{name:13} db_r={n['r']} db_w={n['w']} {val} {flag}")

demo("aside", False, True)                # miss fill: app
demo("write-through", True, True)
demo("read-through", False, True)         # miss fill: cache
demo("write-back", True, False)
demo("write-around", False, True, False)  # empty cache; miss fill: app
# aside         db_r=0 db_w=1 old stale
# write-through db_r=0 db_w=1 new fresh
# read-through  db_r=0 db_w=1 old stale
# write-back    db_r=0 db_w=0 new fresh
# write-around  db_r=1 db_w=1 new fresh
```

Write-through and write-back update the cache, so the next read is fresh.
Aside and read-through wrote the database only, so a pre-filled cache is
still old (the inconsistency the article names). Write-around skipped the
cache on write too; with an empty cache the read misses and loads the new
value (the article's high read latency / miss rate cost).
Write-back has not flushed (`db_w=0`); a crash before that flush is the
data-loss risk. Combos of these patterns are what real systems run.

Sources: Neo Kim, [Top 5 Caching Patterns](https://newsletter.systemdesign.one/p/caching-patterns)
(The System Design Newsletter; cache aside, write through, read through,
write back / write behind, write around; Redis and Memcached; combinations
in real systems);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Cache: cache-aside, write-through, write-behind; Memcached on cache-aside;
Redis and Memcached as in-memory caches; no write-around section).
