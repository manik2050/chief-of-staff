# Performance vs scalability

Learning evidence for Day 11 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A performance problem is slow for one user. A scalability problem is fast
for one user and slow under load. A service is scalable if adding resources
increases performance in proportion — more units of work, or larger ones as
datasets grow. Adjacent, not the topic: latency is the wait for one action;
throughput is how many finish per unit time. Aim for maximal throughput
with acceptable latency.

```
performance                         scalability
  1 user, expensive work              1 user: cheap
                                      N users, 1 slot: queued

+-----------+                       +-----------+
|    app    |  already slow         |  1 worker | -- A (running)
|  one box  |  no load needed       |  one slot | -- B (wait)
+-----------+                       +-----------+ -- C (wait)

add workers (resources)

+--------+  +--------+  +--------+
| worker |  | worker |  | worker |  N cheap requests ~ 1 cheap request
+--------+  +--------+  +--------+
```

```python
# stdlib only. python3 - <<'PY' ... PY
import time, threading

def burn(seconds):
    end = time.perf_counter() + seconds
    n = 0
    while time.perf_counter() < end:
        n += 1

def cheap():
    time.sleep(0.05)

def timed(label, fn):
    t0 = time.perf_counter()
    fn()
    print(f"{label}: {time.perf_counter() - t0:.2f}s")

def many(n_clients, n_workers):
    gate = threading.Semaphore(n_workers)
    def client():
        with gate:
            cheap()
    threads = [threading.Thread(target=client) for _ in range(n_clients)]
    t0 = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    return time.perf_counter() - t0

timed("one user, 0.30s of work", lambda: burn(0.30))
timed("one user, cheap request", cheap)
print(f"4 users, 1 worker:  {many(4, 1):.2f}s")
print(f"4 users, 4 workers: {many(4, 4):.2f}s")
# one user, 0.30s of work: 0.30s   performance: slow with no load
# one user, cheap request: 0.05s
# 4 users, 1 worker:  0.20s        scalability: cheap alone, queued under load
# 4 users, 4 workers: 0.05s        scaled: wall time stays near one cheap request
```

`cheap()` sleeps, so extra threads actually overlap. A CPU-bound `burn` would
not: CPython's GIL runs only one thread of bytecode at a time. Vertical
scaling (more CPU/RAM on one box) is simpler until that box is the ceiling.
Horizontal scaling (more machines) grows past it, but you must split
requests or data. Adding nodes for redundancy should not make the service
slower. Early YouTube chose Python over C — efficiency traded for the
ability to scale out. Fix the single-user path first. Add workers when one
user is already fast.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Performance vs scalability; Latency vs throughput);
[Werner Vogels: A Word on Scalability](https://www.allthingsdistributed.com/2006/03/a_word_on_scalability.html)
(proportional performance as resources are added; redundancy without a
slowdown);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([11 System Design Concepts Explained](https://newsletter.systemdesign.one/p/11-system-design-concepts-explained)
(scalability; horizontal vs vertical),
[50 System Design Tradeoffs](https://newsletter.systemdesign.one/p/system-design-tradeoffs)
(#25 vertical vs horizontal),
[11 Reasons Why YouTube Was Able to Support 100 Million Video Views a Day
With Only 9 Engineers](https://newsletter.systemdesign.one/p/youtube-scalability)
(Python over C; efficiency for scale-out)).
