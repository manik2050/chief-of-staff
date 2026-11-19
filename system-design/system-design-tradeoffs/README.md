# 50 system design tradeoffs

Learning evidence for Day 41 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Most people treat system design as picking the "best" architecture. Kim's
letter says it is not: you make the right tradeoffs for a given workload
and constraints. The letter lists 50 pairs. It is a paid post; this note
covers a handful from the public list rather than all 50.

After those 50, the pattern is the same: every architecture choice gives
you something and costs you something. The skill is knowing which
tradeoff the workload can afford. Kim quotes Sowell: there are no
solutions, only trade-offs.

```
workload + constraints ----> pick a side (not the "best" architecture)

#1  one-by-one request              batch of many
    low latency                     higher throughput; each waits

#3  uncompressed                    compressed
    less CPU, less processing wait  fewer bytes on the wire and disk

#5  short TTL                       long TTL
    fresher copies                  more hits; origin quieter; staler

#8  extra headroom                  high utilization
    absorbs bursts and spikes       lower cost per unit of work

#9  partition: reject some ops (C)  partition: serve and diverge (A)
```

```python
# Toy TTL, not a measurement. python3 - <<'PY' ... PY
def run(ttl, times):
    origin, until, val, rows = 0, -1, None, []
    for t in times:
        if t < until:
            rows.append(f"t={t} hit v{val}")
        else:
            origin += 1
            val, until = origin, t + ttl
            rows.append(f"t={t} miss v{val}")
    print("ttl", ttl, "origin", origin)
    print("\n".join(rows))

run(3, [0, 1, 2, 3])
run(1, [0, 1, 2, 3])
# ttl 3 origin 2
# t=0 miss v1
# t=1 hit v1
# t=2 hit v1          still v1: hit rate up, freshness down
# t=3 miss v2
# ttl 1 origin 4
# t=0 miss v1
# t=1 miss v2
# t=2 miss v3         fresher; four origin trips
# t=3 miss v4
```

Batch when throughput matters; send requests one by one when low latency
matters (#1). Compress when bandwidth and storage matter; leave data
uncompressed when CPU and processing latency matter (#3). Use a longer
TTL when a high cache hit rate matters, a shorter TTL when freshness
matters (#5). Run close to max utilization when cost efficiency matters;
keep extra headroom when traffic bursts matter (#8). During a partition,
prioritize consistency when stale or conflicting data is unacceptable;
prioritize availability when serving requests through the split matters
(#9). Adjacent days already treat #1 and #9 in depth; this note is the
menu, not those chapters.

Sources: [Neo Kim, 50 System Design Tradeoffs](https://newsletter.systemdesign.one/p/system-design-tradeoffs)
(#174 / 50 shades of system design: not the "best" architecture; 50
pairs; #1 latency vs throughput / batching; #3 compression vs CPU; #5
cache freshness vs hit rate; #8 high utilization vs headroom; #9
consistency vs availability during partitions; every choice gives and
costs; Sowell quote).
