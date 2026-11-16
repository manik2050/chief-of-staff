# Concurrency vs parallelism

Learning evidence for Day 38 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Concurrency is switching between different tasks at once. A scheduler
breaks each task into smaller parts, assigns a slice, then moves on, so
one CPU runs those micro-tasks in interleaved order. That creates an
illusion of parallel execution; as the number of tasks grows, each waits
for its turn and performance worsens. A single CPU ran only one task at
a time. It still finished faster than humans, but waiting on I/O such as
keyboard input wasted CPU, and the system became slow and non-responsive
as tasks grew. Parallelism is handling many tasks at once: extra CPU
cores, each a processing unit inside the CPU that runs a task
independently, which offers efficiency. Concurrency is about the design;
parallelism is about the execution model.

One chef making doner kebab for 3 customers switches between fries, meat,
and vegetables (concurrency). Three chefs for 3 customers finish at the
same time (parallelism). CPU-intensive tasks run efficiently with
parallelism; parallelism wastes CPU time on I/O-heavy tasks. Running
tasks on different CPUs does not always speed them up, because
coordinating independent execution is necessary. Combine concurrency
with parallelism for efficient, scalable, and responsive systems; that
pairing is high throughput.

```
concurrency (1 CPU, interleaved)         parallelism (many cores)

  time -->                               time -->
  A A | B B | A A | B B                  A A A A     core 1
  chef: fries, then meat, then veg       B B B B     core 2
                                         3 chefs, 3 customers at once

  illusion of parallel execution         each core runs a task
  extra delay as tasks wait their turn   independently
```

```python
# stdlib only. python3 - <<'PY' ... PY
import asyncio, time
from multiprocessing import Process

async def io_task(name):
    print(f"{name} start", flush=True)
    await asyncio.sleep(0.05)
    print(f"{name} done", flush=True)

async def concurrent():
    await asyncio.gather(io_task("A"), io_task("B"))

print("concurrent (1 worker, interleaved):")
t0 = time.perf_counter()
asyncio.run(concurrent())
print(f"wall {time.perf_counter() - t0:.2f}s")

def burn():
    x = 0
    for i in range(8_000_000):
        x += i
    return x

print("serial (2 CPU tasks, 1 process):")
t0 = time.perf_counter()
burn(); burn()
print(f"wall {time.perf_counter() - t0:.2f}s")

print("parallel (2 processes, CPU):")
t0 = time.perf_counter()
ps = [Process(target=burn) for _ in range(2)]
for p in ps: p.start()
for p in ps: p.join()
print(f"wall {time.perf_counter() - t0:.2f}s")
# concurrent (1 worker, interleaved):
# A start
# B start
# A done
# B done
# wall 0.05s
# serial (2 CPU tasks, 1 process):
# wall 0.39s
# parallel (2 processes, CPU):
# wall 0.20s
```

One event loop switches on I/O waits (A and B both start before either
finishes). Two CPU burns on one process run back to back; two processes
run them at once (wall times from this toy, not the article). A thread
is the smallest processing unit scheduled by the OS. Simultaneous
changes to the same data might corrupt it, and it is hard to know when a
thread will be scheduled or which instructions it will run, so use
synchronization such as locking: a thread acquires the lock for a set of
operations, and another thread can use the CPU only after that lock is
released. Mutex and semaphore are the two popular primitives that
coordinate access to a shared resource. Use concurrency when work waits
on I/O and one worker should switch rather than sit idle. Use
parallelism for CPU-intensive work on extra cores. Combine both when the
system must stay efficient, scalable, and responsive. Extra CPUs do not
always speed a task that still needs coordination.

Sources: Neo Kim,
[Concurrency Is Not Parallelism](https://newsletter.systemdesign.one/p/concurrency-is-not-parallelism)
(#75, 18 Jun 2025; concurrency as interleaved switching; illusion of
parallel execution; extra delay as tasks wait; parallelism as extra
cores handling many tasks at once; design vs execution model; 3-customer
doner kebab chef vs 3 chefs; CPU-intensive vs I/O-heavy; coordination;
concurrency + parallelism = high throughput; threads; locking; mutex and
semaphore).
