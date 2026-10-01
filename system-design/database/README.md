# Database scaling

Learning evidence for Day 4 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A database scales first by copying writes, then by splitting data. The
primary takes every write. Replicas replay those writes and serve reads.
When one primary cannot hold the writes or the disk, you split: federation
by function, sharding by key. Denormalization shows up after the split,
when a join would otherwise cross machines.

```
  client
     |
     | write                    read (if lag is ok)
     v                               |
+-----------+     replicate      +-----------+
|  primary  | -----------------> |  replica  |
|  writes   |                    |  reads    |
+-----------+                    +-----------+
```

```
# write the primary; read a replica unless the caller needs a fresh row
def write(row):
    primary.write(row)             # never write a replica

def read(key, need_fresh):
    if need_fresh:
        return primary.read(key)   # replica lag is the cost of extra reads
    return replica.read(key)
```

Master-slave is one writer; master-master is two, paying sync latency or
looser consistency. Federation is users vs products. Sharding is users
A-M vs N-Z. Do not shard a box that still fits: you pay routing,
rebalancing, and cross-shard joins for write capacity you did not need.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Database / RDBMS, master-slave, master-master, federation, sharding,
denormalization); [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([How Figma Scaled Postgres](https://newsletter.systemdesign.one/p/postgres-scale),
[Quora MySQL sharding](https://newsletter.systemdesign.one/p/mysql-sharding),
[System Design Tradeoffs](https://newsletter.systemdesign.one/p/system-design-tradeoffs)).
