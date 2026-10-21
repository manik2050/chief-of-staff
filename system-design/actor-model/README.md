# Actor model

Learning evidence for Day 20 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

An actor is the fundamental unit of computation (academy). It holds
private state, reads from its own mailbox, and handles one message at a
time. Other actors never share that memory; they send. A supervisor
watches the child and restarts it on failure. The academy's PayPal case:
Akka (Java) took a billion daily transactions on 8 virtual machines
after scale-out had meant more than 1000 VMs.

```
  sender                         supervisor
     |                                |
     | message (no shared memory)     | restart on fail
     v                                v
+-----------+   FIFO, one at a time +----------+
|  mailbox  | --------------------> |  actor   |  private state
|  (queue)  |                       |  one msg |  then next
+-----------+                       +----------+
```

Many actors can run at once; each still serializes its own mailbox
(academy). Three messages in parallel need three actors.

```bash
python3 - <<'PY'
import asyncio

async def actor(name, mailbox):
    count = 0  # private; senders never touch this
    while True:
        msg = await mailbox.get()
        if msg is None:
            break
        count += 1
        print(f"{name} start {msg} n={count}", flush=True)
        await asyncio.sleep(0.05)
        print(f"{name} done  {msg} n={count}", flush=True)

async def main():
    box = asyncio.Queue()
    task = asyncio.create_task(actor("A", box))
    for i in (1, 2, 3):
        await box.put(i)
    await box.put(None)
    await task

asyncio.run(main())
PY
```

```
A start 1 n=1
A done  1 n=1
A start 2 n=2
A done  2 n=2
A start 3 n=3
A done  3 n=3
```

Start and done never interleave: one mailbox, one in-flight message, a
private counter the senders cannot touch. Toy asyncio, not Akka.

Hewitt, Bishop, and Steiger (1973) defined behavior as sending messages
to actors and needed no semaphore primitive. Akka: an actor instance
processes one message at a time, so no `synchronized` on that state;
`tell` does not block the caller. Each Akka actor has a Mailbox where
messages sit before they run. Erlang: each process has its own input
queue; a supervisor starts, stops, and monitors children and restarts
them when necessary (`one_for_one` restarts only the failed child).
Akka typed default is stop on exception; wrap with `Behaviors.supervise`
to restart.

Tradeoffs: the academy says it is not a silver bullet — learning curve,
and extra care against race conditions and deadlocks. Isolation removes
shared-memory races on the actor's own state; it does not make every
protocol race-free. An unbounded mailbox can grow until memory is gone
(Akka: a bounded mailbox sends overflow to dead letters). Local state in
the app server skips a cache or DB hop (academy); PayPal then routes a
customer back to the same server with consistent hashing.

Use it when many isolated units of work must run concurrently, when a
parent should restart a failed child, or when a thread per request is
the alternative. Skip it when a single-threaded path is enough: the
learning curve is the cost, and the academy says scale is not automatic.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Actor Model](https://newsletter.systemdesign.one/p/actor-model)
— unit of computation; private state; mailbox as FIFO queue; one message
at a time; supervisor restart; Akka at PayPal: billion daily transactions
on 8 VMs after >1000 VMs; consistent hashing; not a silver bullet);
[Hewitt, Bishop, and Steiger 1973](https://www.ijcai.org/Proceedings/73/Papers/027B.pdf)
(actors; sending messages; no semaphore primitive);
[Akka Introduction to Actors](https://doc.akka.io/docs/akka/current/typed/actors.html)
(one message at a time; no `synchronized`; async `tell`);
[Akka Mailboxes](https://doc.akka.io/libraries/akka-core/current/typed/mailboxes.html)
(each actor has a Mailbox; unbounded default; bounded overflow to dead
letters);
[Akka Fault Tolerance](https://doc.akka.io/libraries/akka-core/current/typed/fault-tolerance.html)
(typed default is stop; `Behaviors.supervise` to restart);
[Erlang Concurrent Programming](https://www.erlang.org/doc/system/conc_prog.html)
(per-process input queue);
[Erlang Supervisor Behaviour](https://www.erlang.org/doc/system/sup_princ.html)
(start, stop, monitor; restart; `one_for_one`).
