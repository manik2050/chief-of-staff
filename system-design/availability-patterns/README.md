# Availability patterns

Learning evidence for Day 15 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Fail-over and replication are complementary ways to stay up when a node
dies. Fail-over: a standby takes over. Active-passive: heartbeats; the
passive takes the active's IP; only the active serves (hot vs cold
standby sets the downtime). Active-active: both serve; DNS or the app
must know both. Replication: copies of the data. Master-slave: one writer,
slaves replay and serve reads; master down means read-only until a slave
is promoted. Master-master: both write; either down, still read and write.

```
active-passive                    active-active
  A --heartbeat--> B (standby)      A and B both serve
  heartbeat lost: B takes A's IP    DNS / app knows both

master-slave                      master-master
  writes on master                  both write and coordinate
  slaves replay + serve reads       either down: still read/write
  master down: read-only until
  a slave is promoted
```

```python
# Toy failover: promote a healthy replica. python3 - <<'PY' ... PY
def promote(nodes):
    live = [(n, s) for n, s in nodes.items() if s["healthy"]]
    if not live:
        return "error"
    latest = next(s["data"] for s in nodes.values() if s["role"] == "primary")
    caught = [(n, s) for n, s in live if s["data"] == latest]
    name, state = (caught or live)[0]
    state["role"] = "primary"
    return name, state["data"]

ok = {"A": {"role": "primary", "healthy": False, "data": "v2"},
      "C": {"role": "replica",  "healthy": True,  "data": "v2"}}
lag = {"A": {"role": "primary", "healthy": False, "data": "v2"},
       "B": {"role": "replica",  "healthy": True,  "data": "v1"}}
print("caught up:", promote(ok))
print("lagging:", promote(lag))
# caught up: ('C', 'v2')   replica already has the write
# lagging: ('B', 'v1')     write never reached B; promoting loses v2
```

Active-passive is simpler; downtime lasts until the standby is hot.
Active-active spreads load and keeps serving if one dies, at the cost of
DNS or app knowing both, plus write coordination. A sync copy waits for
another replica before ack, so a later failover is less likely to lose
an acknowledged write. An async copy answers faster and can lag: if the
primary dies first, the promoted replica may miss the last write. Both
patterns add hardware and complexity.

Adjacent, already boarded: consistency-patterns (how copies stay in
sync) and availability-vs-consistency / CAP (C or A in a partition).

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Availability patterns: fail-over, active-passive / active-active, hot vs
cold standby, replication via master-slave / master-master; data loss if
the active fails before a write is copied);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Consistency Patterns](https://systemdesign.one/consistency-patterns/)
(leader-follower failover is read-only; multi-leader stays read/write;
sync vs async),
[50 System Design Tradeoffs](https://newsletter.systemdesign.one/p/system-design-tradeoffs)
(#12 sync vs async replication; #49 active-active vs active-passive)).
