# Availability vs consistency

Learning evidence for Day 13 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

In a distributed system you can keep at most two of consistency, availability,
and partition tolerance. Consistency: every read gets the latest write, or an
error. Availability: every request gets a response, which may be stale.
Partition tolerance: the system keeps going when the network splits. Networks
are not reliable, so you take P and choose C or A in software.

```
no partition                         partition (A cannot reach B)
  A <---sync---> B                     A | | B
  both have v2                         A: v2     B: v1

CP: a read that cannot confirm         AP: B answers v1 (stale)
    the latest write returns error         A answers v2
    (no split-brain value)                 live answers disagree
```

```python
# Toy replicas, not a measurement. python3 - <<'PY' ... PY
replica = {"A": "v2", "B": "v1"}   # write landed on A; B not updated
partitioned = True

def cp_read(node):
    if partitioned:                # cannot confirm the other replica
        return "error"             # refuse rather than serve a guess
    return replica[node]

def ap_read(node):
    return replica[node]           # always answer; may be stale

print("CP B:", cp_read("B"))
print("AP B:", ap_read("B"), " AP A:", ap_read("A"))
# CP B: error                      no stale value; some requests fail
# AP B: v1  AP A: v2               every request answers; values disagree
```

Choose CP when the business needs atomic reads and writes, or when stale or
conflicting data is unacceptable. Choose AP when eventual consistency is
allowed, or when serving through a partition matters more than agreement.
Adjacent, not this topic: with no partition, PACELC still trades latency
against consistency.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Availability vs consistency; CAP theorem: definitions; take P, choose C or A;
CP for atomic reads/writes; AP for eventual consistency / keep working);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([50 System Design Tradeoffs](https://newsletter.systemdesign.one/p/system-design-tradeoffs)
(#9 consistency vs availability during partitions),
[11 System Design Concepts Explained](https://newsletter.systemdesign.one/p/11-system-design-concepts-explained)
(CAP; PACELC: else latency vs consistency)).
