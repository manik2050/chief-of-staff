# Concurrency vs parallelism

Learning evidence for Day 38 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A single CPU once ran only one task at a time. It still finished faster
than humans, but waiting on I/O such as keyboard input wasted CPU time,
and the system became slow and non-responsive as tasks grew. So a
scheduler broke each task into smaller parts, gave each a slice, then
moved on: one CPU runs those micro-tasks in interleaved order. Switching
between different tasks at once is concurrency. It creates only an
illusion of parallel execution; as tasks grow, each waits its turn and
performance worsens. Extra CPU cores, each a processing unit that runs a
task independently, handle many tasks at once: parallelism, which offers
efficiency. Concurrency is about the design; parallelism is about the
execution model.

One chef making doner kebab for 3 customers switches between fries, meat,
and vegetables (concurrency). Three chefs for 3 customers are all done at
the same time (parallelism). CPU-intensive tasks run efficiently with
parallelism; parallelism wastes CPU time on I/O-heavy tasks. Running
tasks on different CPUs does not always speed them up, because
coordinating tasks for independent execution is necessary. Combine
concurrency with parallelism for efficient, scalable, and responsive
systems: concurrency + parallelism = high throughput.

```
concurrency (1 CPU, interleaved)         parallelism (many cores)

  time -->                               time -->
  A A | B B | A A | B B                  A A A A     core 1
  1 chef switches: fries, meat, veg      B B B B     core 2
                                         3 chefs, 3 customers, done together
  illusion of parallel execution         each core runs a task
  extra delay as tasks wait their turn   independently
```

```python
# Toy, not the article; needs 2+ cores. python3 - <<'PY' ... PY
import asyncio, multiprocessing as mp, time

async def io_task(name):
    print(f"{name} start")
    await asyncio.sleep(0.05)              # I/O wait: the loop switches
    print(f"{name} done")

async def main():
    await asyncio.gather(io_task("A"), io_task("B"))

def burn():
    x = 0
    for i in range(8_000_000):
        x += i

def wall(fn):
    t0 = time.perf_counter(); fn(); return time.perf_counter() - t0

def parallel():
    ctx = mp.get_context("fork")           # stdin script: fork, not spawn
    ps = [ctx.Process(target=burn) for _ in range(2)]
    for p in ps: p.start()
    for p in ps: p.join()

print("concurrent, 1 event loop:")
io = wall(lambda: asyncio.run(main()))     # two 0.05s waits back to back = 0.10s
print("I/O waits overlapped:", io < 0.09)
serial = wall(lambda: (burn(), burn()))    # 2 CPU burns, 1 process
print("parallel faster than serial:", wall(parallel) < 0.8 * serial)
# concurrent, 1 event loop:
# A start
# B start
# A done
# B done
# I/O waits overlapped: True
# parallel faster than serial: True
```

One event loop switches on I/O waits: A and B both start before either
finishes, so the two waits overlap. Two CPU burns run back to back in one
process and at once in two processes on two cores (toy timings, not the
article). Simultaneous changes to the same data might corrupt it, and it
is hard to know when a thread, the smallest processing unit the OS
schedules, will run or which instructions it will run, so synchronization
such as locking is necessary: a thread acquires the lock for a set of
operations, and another thread can use the CPU only after it is
released. Mutex and semaphore are the two popular primitives that
coordinate access to a shared resource.

Sources: Neo Kim,
[Concurrency Is Not Parallelism](https://newsletter.systemdesign.one/p/concurrency-is-not-parallelism)
(#75, 18 Jun 2025; single CPU and wasted I/O time; scheduler and
interleaving; illusion of parallel execution; extra delay; cores and
parallelism; design vs execution model; doner kebab chefs; CPU-intensive
vs I/O-heavy; coordination; concurrency + parallelism = high throughput;
threads; locking; mutex and semaphore).
