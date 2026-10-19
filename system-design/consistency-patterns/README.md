# Consistency patterns

Learning evidence for Day 14 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

With multiple copies of the same data, you choose how those copies stay in
sync. CAP consistency is every read getting the latest write, or an error.
Weak: after a write, later reads may or may not see it (best effort).
Eventual: they will see it once replicas catch up (async copy). Strong:
they see it because the write waits for a sync copy.

```
write v2 on A                         a later read of B

weak       A: v2   B: v1              B may still be v1 (best effort)
eventual   A: v2   B: v1 (pending)    B becomes v2 after catch-up
strong     A: v2   B: v2 (acked)      B is already v2; the write waited
```

```python
# Toy replicas, not a measurement. python3 - <<'PY' ... PY
def weak(replicas, value):
    replicas["A"] = value                 # best effort; B is not updated

def eventual(replicas, value, catch_up):
    replicas["A"] = value                 # ack now
    if catch_up:
        replicas["B"] = value             # later; replicas catch up

def strong(replicas, value):
    replicas["A"] = replicas["B"] = value # sync; the write waited

w = {"A": "v1", "B": "v1"}; weak(w, "v2")
print("weak B:", w["B"])
e0 = {"A": "v1", "B": "v1"}; eventual(e0, "v2", False)
print("eventual B before:", e0["B"])
e1 = {"A": "v1", "B": "v1"}; eventual(e1, "v2", True)
print("eventual B after:", e1["B"])
s = {"A": "v1", "B": "v1"}; strong(s, "v2")
print("strong B:", s["B"])
# weak B: v1                 may or may not see the write
# eventual B before: v1      stale until catch-up
# eventual B after: v2       converged
# strong B: v2               reads see the write
```

Choose weak when a missed update is fine: VoIP, a live stream, a realtime
game, memcached. Choose eventual when the system must stay available and a
stale read is tolerable: DNS, email. Choose strong when you need
transactions: file systems, RDBMS. A sync copy raises write latency and can
refuse work in a partition; an async copy answers faster and can lag.
Adjacent, not this topic: the primer's next section is availability
patterns (fail-over and replication).

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Consistency patterns: weak / eventual / strong; memcached and VoIP vs
DNS/email vs file systems and RDBMS; async vs sync copy);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Consistency Patterns](https://systemdesign.one/consistency-patterns/)
(sync vs async; write-behind as weak; banking vs DNS/SMTP),
[50 System Design Tradeoffs](https://newsletter.systemdesign.one/p/system-design-tradeoffs)
(#9 consistency vs availability; #10/#12 sync copy vs write latency)).
