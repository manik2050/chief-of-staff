# Back of the envelope

Learning evidence for Day 16 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Back-of-the-envelope estimates are arithmetic on known orders of
magnitude so you can size a design before you prototype. Powers of two
turn a count into bytes. The latency table is orders of magnitude, not
a benchmark. Convert traffic to operations per second, then multiply
records by bytes per record.

```
powers of two (primer)              latency (primer; orders of magnitude)
  2^10   1024   ~1 thousand  1 KB     L1 cache reference          0.5 ns
  2^20   ~1e6   ~1 million   1 MB     main memory reference       100 ns
  2^30   ~1e9   ~1 billion   1 GB     same-datacenter round trip  500 us
  2^40   ~1e12  ~1 trillion  1 TB     HDD seek                     10 ms
                                      CA->Netherlands->CA         150 ms
```

Recipe: QPS = (DAU × requests/user/day) / (24×60×60). The academy
rounds 1 million requests/day to 12 QPS. Storage = writes × bytes/write;
read the product in 2^10 / 2^20 / 2^30 units. Round (83 becomes 100)
and name the assumptions.

```python
# Toy assumptions, not measurements. python3 - <<'PY' ... PY
dau = 1_000_000                 # toy
req_per_user = 1                # toy → 1e6 req/day
bytes_per_write = 2**10         # primer: 2^10 = 1 KB
req_day = dau * req_per_user
qps = req_day / (24 * 60 * 60)
storage = req_day * bytes_per_write
print(f"QPS: {qps:.2f}")
print(f"storage: {storage} B")
# QPS: 11.57                      academy: 1e6 req/day = 12 QPS
# storage: 1024000000 B           primer: 2^30 ≈ 1 billion B = 1 GB
```

Use this to compare designs, decide whether to partition, and hunt
bottlenecks — not as a measurement. Unknown numbers need a prototype.
In an interview it is not mandatory and should stay under five minutes
unless the interviewer says otherwise.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Appendix: Powers of two table; Latency numbers every programmer should know);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Back of the Envelope](https://systemdesign.one/back-of-the-envelope/)
(definition; 1e6 req/day = 12 QPS; rounding 83→100; when to use)).
