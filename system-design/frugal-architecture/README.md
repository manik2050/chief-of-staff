# Frugal architecture

Learning evidence for Day 19 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Cost is a non-functional requirement, the same class as availability or
security, not an invoice that arrives after launch. Werner Vogels' seven
laws (The Frugal Architect; re:Invent 2023 keynote, per the academy)
split the work into design, measure, and observe. The academy restates
them as Amazon Frugal Architecture: ship only what users need, let spend
track the business, meter the system, name every trade-off, split into
tunable parts, keep optimizing, and question the stack that already
works. Frugality is maximizing value, not minimizing spend. If cost
exceeds revenue, the system does not last.

```
DESIGN                            MEASURE
 I  cost is an NFR                 IV  unobserved => unknown cost
 II architecture follows money     V   tunable controls by tier
 III every choice is a trade-off
                                   OBSERVE
                                   VI  optimize in small steps
                                   VII success is not a proof
```

```
  request
     |
     | rate-limit unused traffic          academy: align cost (II)
     v
+------------------+  CDN / cache hit     academy: CDN + object
| edge / LB pool   | ------------------>  store; skip origin bill
+------------------+
     | miss
     | autoscale chairs in / out          academy: scale with traffic
     v
+------------------+
| app blocks       |  T1 essential        Vogels V
| T1 / T2 / T3     |  T2 may shrink
+------------------+  T3 cheap or off
     |
     v
+------------------+  archive inactive    academy: storage follows use
| store            |  extra replicas      academy: paid trade-off
+------------------+                      (read copies vs write path)
     |
  meters: utilization, spend, errors      Vogels IV
```

```
# Vogels V: tunable blocks by criticality. no dollar amounts.
def admit(component, busy):
    if component.tier == 1:       # essential; keep serving
        return "serve"
    if component.tier == 2:       # important; may shrink
        return "serve" if busy else "shrink"
    return "off"                  # T3 nice-to-have
```

Back-of-the-envelope arithmetic makes Law I checkable before you buy
capacity: QPS and bytes, not a later surprise bill. A cache or CDN hit
is a skipped origin trip (and bill). A load balancer in front of an
autoscaling pool is how chairs appear and leave with traffic. Indexes
and read replicas buy read speed; they are paid trade-offs, not free
speed. Revisit production patterns (Law VI). Do not keep a language or
store only because "we have always done it this way" (Law VII). Cheapen
T3 before you starve T1.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Amazon Frugal Architecture Explained](https://newsletter.systemdesign.one/p/frugal-architecture)
— cost as an NFR; essential features; autoscaling, archive inactive
data, rate-limiting; monitor usage and errors; indexes and read replicas
as trade-offs; rank and tune services; compressed object storage plus
CDN; question the default stack; points at the re:Invent 2023 keynote);
[The Frugal Architect](https://thefrugalarchitect.com/)
(Laws I–VII: cost as a non-functional requirement; systems that last
align cost to the business; architecting is a series of trade-offs;
unobserved systems lead to unknown costs; cost-aware architectures
implement cost controls, including T1/T2/T3; cost optimization is
incremental; unchallenged success leads to assumptions).
