# Bloom filter

Learning evidence for Day 31 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A Bloom filter is a space-efficient probabilistic structure that tests
whether an item is in a set (Neo Kim / System Design). It is a bit array
of length n plus k hash functions. Add hashes the item k times, takes
each hash modulo n, and sets those bits. A membership check uses the
same hashes: if any bit is unset, the item is definitely not in the set;
if every bit is set, it might be. False positives are possible. False
negatives are not. The classic filter has no delete: clearing a bit could
mark some other item absent.

```
  empty n=10:  0 0 0 0 0 0 0 0 0 0
               0 1 2 3 4 5 6 7 8 9

  add red  (1, 3, 5) and blue (4, 5, 9)
               0 1 0 1 1 1 0 0 0 1

  query blue  (4, 5, 9 all 1) -> maybe
  query black (0, 3, 6; bit 0 is 0) -> no
  query green (3, 4, 5 all 1, never added) -> false yes
```

```python
# Toy filter, not a library. python3 - <<'PY' ... PY
import hashlib

N, K = 10, 3

def loc(item):
    out = []
    for seed in range(K):
        d = hashlib.md5(f"{seed}:{item}".encode()).digest()
        out.append(int.from_bytes(d[:4], "little") % N)
    return out

def add(bits, item):
    for i in loc(item):
        bits[i] = 1

def maybe(bits, item):
    return all(bits[i] for i in loc(item))

bits = [0] * N
for w in ("red", "blue"):
    add(bits, w)

print("red", maybe(bits, "red"), loc("red"))
print("black", maybe(bits, "black"), loc("black"))
print("yellow", maybe(bits, "yellow"), loc("yellow"))
# red True [8, 1, 2]
# black False [3, 7, 5]
# yellow True [8, 8, 0]   never inserted; those bits were already set
```

Add runs k hashes, maps each onto a bucket, and sets those bits to one;
the same bucket can be set more than once because hashes collide. Check
repeats the hashes: a zero means never added; all ones means maybe
(another item or a collision may have set them). The article's green
query is that false-positive case: red and blue already turned on 3, 4,
and 5. Time is O(k) for add and for membership, independent of how many
items are already stored; the k lookups can run in parallel. Space is a
fixed bit array (the article calls this constant / O(1)): the filter
stores bits, not the items. Accuracy depends on k, hash quality, n, and
how many items were inserted; faster, independent, uniform hashes help,
and the false-positive rate cannot be driven to zero. Advantages the
article names: constant time, constant space, parallel operations, no
false negatives, and privacy because the actual items are not stored.
Disadvantages: the classic filter has no delete, false positives cannot
reach zero, and a filter on disk needs random access because hashes
scatter the indices — do not clear a bit to "remove" an item, or shared
bits create false negatives. Use it on high-ingestion paths to skip disk
seeks for keys that are not there: the article names in-memory filters
in front of large on-disk tables, Cassandra LSM SSTables, taken user
IDs, already-shown recommendation posts, spell checkers (misspellings
and profanity), malicious URLs / blocked IPs / fraud, and MapReduce
over large datasets. Counting, scalable, and striped Bloom filters
exist as named extensions; quotient and cuckoo filters are named as
related structures. The primer has no Bloom filter or
probabilistic-membership section.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Bloom Filter](https://systemdesign.one/bloom-filters-explained/)
— Neo Kim / System Design; academy B technologies after API Design
Concepts - Part 2: bit array plus k hashes; add sets bits; all bits set
is maybe, any unset is no; no false negatives; no classic delete; O(k)
time, constant bit-array space; disk-seek skip, Cassandra SSTables,
spell checkers, MapReduce; counting / scalable / striped named);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(no Bloom filter or probabilistic membership).
