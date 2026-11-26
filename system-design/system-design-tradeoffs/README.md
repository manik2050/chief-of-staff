# 50 system design tradeoffs

Learning evidence for Day 41 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Most people think system design is about building the "best"
architecture. Neo Kim's letter says it is not: it is about making the
right tradeoffs for a given workload and constraints. He then lists 50
pairs; most say what you gain, what it costs, and when to pick each side.
The sketch shows five of them, by their number in the letter.

He closes with the pattern behind all 50: every architecture choice gives
you something and costs you something. The skill is knowing which
tradeoff your workload can afford. He ends on Thomas Sowell: "There are
no solutions. There are only trade-offs."

```
workload + constraints ----> pick a side (not the "best" architecture)

#1  one-by-one request              batch of many
    low latency                     higher throughput; each waits

#3  uncompressed                    compressed
    less CPU, less processing wait  less bandwidth and storage

#5  short TTL                       long TTL
    fresher data                    more hits; fewer origin requests; staler

#8  extra headroom                  high utilization
    absorbs bursts, latency spikes  lower cost per unit of work

#9  partition: reject some ops (C)  partition: serve and diverge (A)
```

```python
# Toy TTL, not a measurement. python3 - <<'PY' ... PY
def run(ttl, times):
    trips, until, cached, rows = 0, -1, None, []
    for t in times:                    # toy origin's value changes every tick: v{t}
        if t < until:
            rows.append(f"t={t} hit  served v{cached} origin v{t}")
        else:
            trips += 1
            cached, until = t, t + ttl
            rows.append(f"t={t} miss served v{cached} origin v{t}")
    print("ttl", ttl, "origin trips", trips)
    print("\n".join(rows))

run(3, [0, 1, 2, 3])
run(1, [0, 1, 2, 3])
# ttl 3 origin trips 2
# t=0 miss served v0 origin v0
# t=1 hit  served v0 origin v1    stale by 1 tick
# t=2 hit  served v0 origin v2    stale by 2: more hits, less fresh
# t=3 miss served v3 origin v3
# ttl 1 origin trips 4
# t=0 miss served v0 origin v0
# t=1 miss served v1 origin v1
# t=2 miss served v2 origin v2    always fresh; every read hits the origin
# t=3 miss served v3 origin v3
```

Batch when throughput matters; send individual requests when low latency
matters (#1). Compress when bandwidth and storage matter; leave data
uncompressed when low CPU usage and processing latency matter (#3). Use
longer TTLs when a high cache hit rate matters, shorter TTLs when data
freshness matters (#5). Run close to maximum utilization when cost
efficiency matters; keep extra headroom when handling traffic bursts
matters (#8). During a partition, prioritize consistency when
stale or conflicting data is unacceptable, and availability when serving
requests during partitions matters (#9). For #1 and #9 in depth, see
[latency vs throughput](../latency-vs-throughput/) and
[availability vs consistency](../availability-vs-consistency/). The
toy's TTLs and ticks are toy numbers, not the letter's.

Sources: Neo Kim,
[50 shades of system design](https://newsletter.systemdesign.one/p/system-design-tradeoffs)
(System Design Newsletter #174, 3 Sep 2026; "#174: tradeoffs behind
designing scalable, reliable systems"; all 50 numbered pairs are in the
public text, the footnotes are for subscribers only; used here: not the
"best" architecture, #1, #3, #5, #8, #9, the closing pattern, and the
Sowell quote).
