# Consistent hashing

Learning evidence for Day 37 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Consistent hashing puts nodes and keys on a virtual ring (the hash ring).
The same hash function hashes a node's IP or domain and each data key onto
that circle; a uniform, independent hash such as MD5 is used. The largest
hash wraps to the smallest. From a key, walk clockwise to the first node
whose position is greater; that node stores or returns the object. Each
node owns the arc from its predecessor. Virtual nodes hash one physical ID
through distinct functions onto many spots so keys spread more evenly, and
a higher-capacity node can take more spots.

Static partitioning does node ID = hash(key) mod N. Lookup is O(1), but
adding or removing a node breaks existing maps and forces massive data
movement; most requests miss and swamp the origin. Cache replication does
not fix dynamic load: only a limited set fits, and keeping replicas consistent
is expensive. The ring exists so cache servers can scale with demand while
remapping far fewer keys when N changes.

```
  hash(key), hash(node) -> same ring; largest hash wraps to smallest
     |
     v
   D ---- *key ---- A ---- B ---- C ---- (wrap)
              |
              +-- clockwise --> first node with pos > key (A)

  add E between D and A: only keys on (D, E] move; the rest stay
  virtual nodes: one machine hashed onto many spots (A0, A1, ...)
```

```python
# Toy ring with virtual nodes. python3 - <<'PY' ... PY
import hashlib

def h(s):
    return int.from_bytes(hashlib.md5(s.encode()).digest(), "big")

N, V, K = 4, 64, 1000
keys = [f"k{i}" for i in range(K)]

def modmap(n):
    return {k: h(k) % n for k in keys}

def ring(n):
    pts = sorted((h(f"{i}:{v}"), i) for i in range(n) for v in range(V))
    def owner(k):
        p = h(k)
        for pos, i in pts:
            if pos >= p:
                return i
        return pts[0][1]
    return {k: owner(k) for k in keys}

def nmove(a, b):
    return sum(a[k] != b[k] for k in keys)

print("modulo", nmove(modmap(N), modmap(N + 1)))
print("ring  ", nmove(ring(N), ring(N + 1)))
print("1/N   ", K // N)
# modulo 782
# ring   203
# 1/N    250
```

It scales horizontally, moves less data when N changes, and makes
replication and partitioning quicker. Average keys on a node is k/N; add
or remove moves about that many. Uneven placement creates hot spots and
cascading failure, and the basic ring ignores that nodes differ in
performance. Virtual nodes spread load — including during downtime, when
a new node joins, and across heterogeneous machines — but a popular
object still hits the same subset of nodes, capacity planning is trickier,
a BST of positions costs memory and operational complexity, replication
needs extra logic to pick distinct physical nodes, and downtime of a
virtual node affects multiple nodes on the ring. BST add/remove node is
O(k/n + log n); add/remove key is O(log n). Use it to partition data or
to load-balance. Discord finds the nodes that host a server this way.
DynamoDB, Cassandra, and Riak partition with it for incremental scale.
Vimeo load-balances video traffic; Netflix distributes uploaded video
across a CDN. Memcached clients (Ketama) and Dynamo ship it; HAProxy has
a bounded-load variant. This toy used 1000 keys, 4 nodes, and 64 virtual
spots each (counts are from the toy, not the article). Adding a fifth
node remapped 782 keys under modulo and 203 on the ring. 1/N of 1000 is
250, so the ring moved about 1/N of the keys; modulo moved most of them.

Sources: Neo Kim,
[Consistent Hashing Explained](https://systemdesign.one/consistent-hashing-explained/)
(Fundamentals, 18 Dec 2022, updated 1 Mar 2023; hash ring; clockwise first
node with pos > key; hash(key) mod N remaps on N change; average keys per
node k/N; virtual nodes; MD5; Discord, DynamoDB, Cassandra, Riak, Vimeo,
Netflix, Memcached Ketama, Dynamo, HAProxy bounded-load).
