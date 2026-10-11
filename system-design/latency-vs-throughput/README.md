# Latency vs throughput

Learning evidence for Day 12 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Latency is the time to perform some action or to produce some result.
Throughput is the number of such actions or results per unit of time.
They are not inverses. Cadence's factory takes eight hours to finish a
car and still ships 120 cars a day (5 per hour) because many cars are
in the line at once. One car at a time would be 1/8 of a car per hour
(illustrative inverse of that latency, not a measurement). Aim for
maximal throughput with acceptable latency.

```
one at a time                         batched
  item 1                                items already queued
    |                                     |
    | overhead, then work                 v
    v                                 +--------+
+--------+  then item 2               | batch  |  one overhead
| item 1 |                            | of N   |  then all leave
+--------+                            +--------+
latency: one item                     latency: wait for the batch
throughput: 1 / that wait             throughput: N / that wait
```

```python
# Toy units, not a measurement. python3 - <<'PY' ... PY
overhead, work, n = 2, 1, 10          # items already queued
serial_lat = overhead + work          # 3
serial_tp = 1 / serial_lat            # 0.33 items per unit time
batch_lat = overhead + n * work       # 12
batch_tp = n / batch_lat              # 0.83 items per unit time
print(f"serial: latency {serial_lat}, throughput {serial_tp:.2f}")
print(f"batch:  latency {batch_lat}, throughput {batch_tp:.2f}")
# serial: latency 3, throughput 0.33   first item finishes sooner
# batch:  latency 12, throughput 0.83  more items finish per unit time
```

Batching many requests together can cut network, serialization, and
processing overhead, so throughput rises; each request waits while the
batch forms, so per-item latency rises. Send one-by-one when low latency
matters (gaming, a video call, a trade). Batch when throughput matters
(a high-traffic API). Caching, a nearby copy, or a CDN cut the wait for
one request.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Latency vs throughput);
[Understanding latency vs throughput](https://community.cadence.com/cadence_blogs_8/b/fv/posts/understanding-latency-vs-throughput)
(definitions; factory example: 8 hours, 120 cars/day);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([50 System Design Tradeoffs](https://newsletter.systemdesign.one/p/system-design-tradeoffs)
(#1 latency vs throughput: batching),
[11 System Design Concepts Explained](https://newsletter.systemdesign.one/p/11-system-design-concepts-explained)
(latency; caching / CDN / replicas),
[114 System Design Concepts - Part 1](https://newsletter.systemdesign.one/p/system-design-concepts)
(latency vs throughput vs bandwidth; when to optimize which)).
