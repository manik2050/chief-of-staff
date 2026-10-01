# Load balancers

Learning evidence for Day 1 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A load balancer sits in front of a pool of equivalent backends. Clients talk
to one address. The balancer picks a healthy backend, forwards the request,
and returns the response. That is how one process stops being both the
capacity limit and the single point of failure.

```
  clients
     |
     v
+----------------+     health probes      +-------+
| load balancer  | ---------------------> | app-a |
|  pick backend  | ---------------------> | app-b |
|  skip the dead | ---------------------> | app-c |
+----------------+                        +-------+
     ^                                        |
     +----------- request / response ---------+
```

```
# pick a backend; skip anything the last probe marked down
def next_backend(pool, algo):
    live = [b for b in pool if b.healthy]
    if not live:
        fail()
    return algo.choose(live)  # round-robin, least-conn, ip-hash, ...
```

L4 chooses from IP and port only. L7 reads the request and can route by
path or cookie. Pinning a client to one backend (sticky sessions) is a
workaround for local session state; a shared store is the cleaner fix.
The balancer itself is a SPOF unless it is paired.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Load balancer); [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([How Load Balancing Algorithms Work](https://newsletter.systemdesign.one/p/load-balancing-algorithms),
[Facebook software load balancer](https://newsletter.systemdesign.one/p/facebook-load-balancer)).
