# Scalability patterns

Learning evidence for Day 40 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Neo Kim's letter is 11 interview techniques for "how to effectively scale a
system." Scale-up is the quickest extra load and needs no rewrite. Scale-out
adds machines behind a load balancer, then only works if session state is
not stuck on one box. The public text covers patterns 1-7 (shared-nothing
stops after its definition). Patterns 8-11 are behind the subscriber
paywall. The sketch lists each public pattern with its first note from the
letter.

```
pattern                          first note in the letter
1  vertical scaling              more CPU, memory, and/or faster disks
2  horizontal scaling            more machines behind a load balancer
3  stateless services            no client session stored between requests
4  loose coupling                depend on others as little as possible
5  modular architecture          one module per function; defined interfaces
6  event-driven architecture     publish events; consumers react on their own
7  shared-nothing architecture   each node owns compute, memory, and storage
8  (paywalled)                   not in the public text
9  (paywalled)                   not in the public text
10 (paywalled)                   not in the public text
11 (paywalled)                   not in the public text
```

```python
# Toy units, not from the letter. python3 - <<'PY' ... PY
def run(load, nodes, cap, sticky):
    workers = 1 if sticky else nodes
    served = min(load, workers * cap)
    return served, max(0, load - served)  # served, unserved

for name, nodes, cap, sticky in [
    ("vertical 1x8", 1, 8, False),
    ("horiz sticky 3x8", 3, 8, True),
    ("horiz stateless 3x8", 3, 8, False),
]:
    print(f"{name}: {run(12, nodes, cap, sticky)}")
# vertical 1x8: (8, 4)
# horiz sticky 3x8: (8, 4)
# horiz stateless 3x8: (12, 0)
```

Vertical is the fastest extra capacity, then larger machines cost more, all
machines have limits, and one server is a full outage. Scale up for a quick
bump; consider horizontal before that machine is the bottleneck. Horizontal
fits high or unpredictable traffic and adds availability with spare
instances, then needs load balancing, coordination, and consistent shared
data; local sessions vanish when the next request lands elsewhere. Stateless
puts session state in a shared store or a signed token so any server can
handle a request; that adds latency and a dependency, and sticky sessions
cut flexibility on failure. Loose coupling (APIs or messages) lets
components update, deploy, and scale on their own, then makes failures hard
to trace. Modularity alone does not guarantee independent scaling or failure
isolation. Event-driven consumers scale without waiting, at the cost of
late, duplicate, or out-of-order events and eventual consistency, so
consumers must be idempotent. Shared-nothing gives each node its own
compute, memory, and storage so processing does not sit on a central
resource; the rest of that pattern is paywalled. The toy's load of 12 and
caps of 8 are toy numbers, not the letter's.

Sources: Neo Kim,
[11 Scalability Patterns in System Design (With Examples)](https://newsletter.systemdesign.one/p/scalability-patterns-system-design)
(System Design Newsletter #197, 29 Oct 2026; patterns 1-7 in the public
text; 8-11 paywalled).
