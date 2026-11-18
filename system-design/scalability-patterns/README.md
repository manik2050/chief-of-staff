# Scalability patterns

Learning evidence for Day 40 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Neo Kim opens with an interview question: "How to effectively scale a
system?" Vertical scaling gives one machine more CPU, memory, and/or faster
disks; the code stays the same, and it is probably the quickest way to
handle extra load. Horizontal scaling runs several copies of the app behind
a load balancer, adding machines as traffic grows and removing them when it
drops. Before you scale out, you must decide where the app stores its state:
if user sessions live on one instance, requests routed to another can lose
them.

The next patterns make scaling out work. A stateless service keeps no client
session between requests; the session lives in a shared database, a cache
like Redis, or a signed token like a JWT, so any server can handle any
request. Loose coupling lets components talk through APIs or messages, so
each can be updated, deployed, and scaled on its own. Modular architecture
gives each module one function and defined interfaces. Event-driven services
publish events to a broker, and consumers react without the publisher
waiting. Shared-nothing gives each node its own compute, memory, and storage.
The sketch lists patterns 1-7 with the letter's one-line definition.

```
pattern                          one line from the letter
1  vertical scaling              more CPU, memory, and/or faster disks
2  horizontal scaling            more machines behind a load balancer
3  stateless services            no client session stored between requests
4  loose coupling                depend on others as little as possible
5  modular architecture          one module per function; defined interfaces
6  event-driven architecture     publish events; consumers react on their own
7  shared-nothing architecture   each node owns compute, memory, and storage
```

```python
# Toy units, not from the letter. python3 - <<'PY' ... PY
def serve(requests, servers, shared):
    store, found = {}, 0
    for i in range(requests):
        node = i % servers                # round-robin load balancer
        key = "shared" if shared else node
        if i == 0:
            store[key] = "user-1"         # login creates the session
        elif store.get(key) == "user-1":
            found += 1
    return found, requests - 1 - found   # session found, session lost

for name, servers, shared in [("1 server, local", 1, False),
                              ("3 servers, local", 3, False),
                              ("3 servers, shared", 3, True)]:
    print(f"{name}: {serve(6, servers, shared)}")
# 1 server, local: (5, 0)
# 3 servers, local: (1, 4)
# 3 servers, shared: (5, 0)
```

Each pattern buys scale with a new cost. Larger machines cost more, all
machines have limits, and one failed server can take the whole app down, so
scale up for quick capacity, then consider horizontal scaling before one
machine is the bottleneck. Scaling out needs load balancing, coordination,
and consistent shared data. A session store adds infrastructure, latency,
and a dependency, and sticky sessions reduce flexibility when servers fail.
Loose coupling makes failures hard to trace, and many tiny services add
communication overhead; use it when components must evolve independently.
Modules in one app still share resources and failure risks, so modularity
alone does not guarantee independent scaling. Events can arrive late, out of
order, or more than once, so consumers must be idempotent. The toy's 6
requests and 3 servers are toy numbers, not the letter's.

Sources: Neo Kim,
[11 Scalability Patterns in System Design (With Examples)](https://newsletter.systemdesign.one/p/scalability-patterns-system-design)
(System Design Newsletter #197, Part 1, 29 Oct 2026; patterns 1-7 in the
public text, the rest for subscribers only).
