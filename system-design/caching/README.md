# Caching

Learning evidence for Day 2 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A cache is a small, fast store in front of a slower source of truth. On a hit,
return the copy. On a miss, load from the origin, keep a copy, then return it.
That is how a hot key stops being both a latency tax and a database hotspot.

```
  request
     |
     v
+-----------+   hit    +-------+
|   cache   | -------> | reply |
+-----------+          +-------+
     | miss
     v
+-----------+   fill   +-------+
|  origin   | -------> | cache |
+-----------+          +-------+
```

```
# cache-aside read; delete the key on write so the next read refills
def get_user(user_id):
    cached = cache.get(user_id)
    if cached is not None:
        return cached
    user = db.get(user_id)          # miss: three trips
    cache.set(user_id, user, ttl=jitter(60))
    return user

def save_user(user):
    db.save(user)
    cache.delete(user.id)           # invalidate; do not write-through
```

Cache-aside (lazy load) puts the app in charge: only requested keys are stored.
Write-through keeps the cache fresh by writing cache and origin together, at the
cost of write latency. Write-behind writes the cache first and flushes later —
fast, but a crash before flush loses data. A TTL is the safety net when you
cannot name every key to invalidate. A stampede is many callers missing the
same hot key at once; jitter the TTL and coalesce the refill.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Cache); [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Top 5 Caching Patterns](https://newsletter.systemdesign.one/p/caching-patterns),
[How Meta Achieves Cache Consistency](https://newsletter.systemdesign.one/p/cache-consistency),
[Redis Use Cases](https://newsletter.systemdesign.one/p/redis-use-cases)).
