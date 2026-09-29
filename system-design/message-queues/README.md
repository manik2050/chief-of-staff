# Message queues

Learning evidence for Day 3 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A message queue sits between a producer and a consumer. The producer writes
work and returns. The consumer pulls later, at its own pace. That is how a
spike of writes stops being both a latency tax on the caller and a crash on
the worker.

```
  producer
     |
     | put
     v
+-----------+     take / ack      +----------+
|   queue   | ------------------> | consumer |
|  hold it  |                     |  do work |
+-----------+                     +----------+
```

```
# work queue: one message, one consumer; ack only after success
def publish(job):
    queue.put(job)                 # return now; do not wait for the worker

def worker_loop():
    while True:
        job = queue.take()         # exclusive claim
        try:
            do(job)
            queue.ack(job)         # at-least-once until this line
        except:
            queue.nack(job)        # redeliver; the worker must be idempotent
```

Work queues compete: one message, one consumer. Pub/sub fans out: one
message, every subscriber. At-most-once drops on failure. At-least-once
redelivers, so duplicates happen. Exactly-once is usually at-least-once
plus an idempotent handler. A full queue is backpressure: slow the producer
or drop, rather than grow RAM without a bound.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Asynchronism); [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([What Is a Message Queue?](https://newsletter.systemdesign.one/p/what-is-a-message-queue),
[How Kafka Works](https://newsletter.systemdesign.one/p/how-kafka-works),
[System Design Tradeoffs](https://newsletter.systemdesign.one/p/system-design-tradeoffs)).
